from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.deps import get_db
from app.models.base_price_data import BasePriceData
from app.models.dataset import Dataset
from app.models.dataset_file import DatasetFile
from app.models.dataset_record import DatasetRecord
from app.models.prediction_detail import PredictionDetail
from app.models.plan import Plan
from app.schemas.common import Paginated
from app.schemas.dataset import DatasetCreate, DatasetOut, DatasetUpdate
from app.services.csv_service import validate_csv_structure
from app.services.storage_service import delete_file, save_upload_file
from app.services.excel_service import parse_excel_file, parse_csv_file, validate_excel_structure

from app.utils.pagination import paginate

router = APIRouter(prefix="/datasets", tags=["datasets"])
ALLOWED_DATASET_NAME = "广东电价数据"


def _ensure_allowed_dataset_name(name: str) -> str:
    normalized = (name or "").strip()
    if normalized != ALLOWED_DATASET_NAME:
        raise HTTPException(
            status_code=400,
            detail=f"仅允许使用数据集: {ALLOWED_DATASET_NAME}",
        )
    return normalized


def _ensure_allowed_dataset(dataset: Dataset) -> None:
    if dataset.name != ALLOWED_DATASET_NAME:
        raise HTTPException(status_code=404, detail="Dataset not found")


@router.get("", response_model=Paginated[DatasetOut])
def list_datasets(
    page: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Paginated[DatasetOut]:
    query = db.query(Dataset).filter(Dataset.name == ALLOWED_DATASET_NAME)
    if keyword:
        query = query.filter(Dataset.name.contains(keyword))
    total, items = paginate(query.order_by(Dataset.id.desc()), page, size)
    return Paginated(total=total, items=items, page=page, size=size)


@router.post("", response_model=DatasetOut)
def create_dataset(
    payload: DatasetCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
) -> Dataset:
    name = _ensure_allowed_dataset_name(payload.name)
    dataset = Dataset(
        name=name,
        description=payload.description,
        created_by=current_admin.id,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def compare_records(new_records: list, existing_records: list) -> bool:
    """
    对比上传的数据与已有数据是否相同。
    相同返回True，不同返回False。
    """
    if len(new_records) != len(existing_records):
        return False
    
    # 按时间排序后逐条对比
    new_sorted = sorted(new_records, key=lambda x: x.get("record_time") or "")
    existing_sorted = sorted(existing_records, key=lambda x: x.record_time)
    
    for new_rec, existing_rec in zip(new_sorted, existing_sorted):
        new_time = new_rec.get("record_time")
        new_price = float(new_rec.get("price_kwh", 0) or 0)
        
        if new_time != existing_rec.record_time:
            return False
        if abs(new_price - float(existing_rec.price_kwh or 0)) > 0.001:
            return False
    
    return True


@router.post("/upload", response_model=DatasetOut)
def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
) -> Dataset:
    """
    上传Excel数据集文件并解析导入数据。
    """
    import traceback
    print(f"[DEBUG] 上传请求: name={name}, file={file.filename}, current_admin={current_admin}")
    
    # 验证文件类型
    filename = file.filename or ""
    is_csv = filename.lower().endswith(".csv")
    is_excel = filename.lower().endswith((".xlsx", ".xls"))
    
    if not is_csv and not is_excel:
        raise HTTPException(status_code=400, detail=f"只支持Excel(.xlsx, .xls)或CSV(.csv)文件，当前文件: {filename}")
    
    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件为空")
    
    # 解析上传的数据
    try:
        if is_csv:
            new_records = parse_csv_file(content)
        else:
            new_records = parse_excel_file(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解析数据失败: {str(e)}")
    
    # 检查是否存在同名数据集
    normalized_name = _ensure_allowed_dataset_name(name)
    existing_dataset = db.query(Dataset).filter(Dataset.name == normalized_name).first()
    
    if existing_dataset:
        # 删除旧数据集的记录，准备用新数据覆盖
        db.query(DatasetRecord).filter(DatasetRecord.dataset_id == existing_dataset.id).delete()
        db.commit()
        
        dataset = existing_dataset
        dataset.description = description
        dataset.verify_status = "未校核"  # 重新上传后状态重置为未校核
    else:
        # 创建新数据集，状态为未校核
        dataset = Dataset(
            name=normalized_name,
            description=description,
            verify_status="未校核",
            created_by=current_admin.id,
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
    
    # 保存文件
    stored_name, stored_path = save_upload_file(content, file.filename)
    size_kb = round(len(content) / 1024, 2)
    
    # 创建或更新文件记录
    db_file = db.query(DatasetFile).filter(DatasetFile.dataset_id == dataset.id).first()
    if db_file:
        delete_file(db_file.stored_path)
        db_file.original_name = file.filename
        db_file.stored_path = stored_path
        db_file.size_kb = size_kb
    else:
        db_file = DatasetFile(
            dataset_id=dataset.id,
            original_name=file.filename,
            stored_path=stored_path,
            size_kb=size_kb,
            description=description,
            created_by=current_admin.id,
        )
        db.add(db_file)
    
    # 导入数据记录（分批提交避免超时）
    batch_size = 1000
    count = 0
    for record_data in new_records:
        record = DatasetRecord(
            dataset_id=dataset.id,
            record_time=record_data.get("record_time"),
            price_kwh=record_data.get("price_kwh", 0.0),
            generation_kwh=record_data.get("generation_kwh", 0.0),
            load_kw=record_data.get("load_kw", 0.0),
            weather_type=record_data.get("weather_type", "unknown"),
            is_holiday=record_data.get("is_holiday", False),
        )
        db.add(record)
        count += 1
        if count % batch_size == 0:
            db.commit()
    
    db.commit()
    db.refresh(dataset)
    return dataset


def _verify_dataset_internal(db: Session, dataset_id: int) -> tuple[Dataset, Optional[str]]:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        return None, "数据集不存在"  # type: ignore[return-value]
    _ensure_allowed_dataset(dataset)

    uploaded_records = db.query(DatasetRecord).filter(
        DatasetRecord.dataset_id == dataset_id
    ).order_by(DatasetRecord.record_time).all()

    if not uploaded_records:
        return dataset, "数据集没有记录，无法校核"

    base_records = db.query(BasePriceData).order_by(BasePriceData.record_time).all()
    if not base_records:
        return dataset, "基础数据不存在，无法校核"

    base_data_map = {}
    for r in base_records:
        base_data_map[r.record_time] = {
            "price_kwh": float(r.price_kwh) if r.price_kwh else 0.0,
            "load_kw": float(r.load_kw) if r.load_kw else 0.0,
        }

    is_match = True
    for record in uploaded_records:
        base_data = base_data_map.get(record.record_time)
        if base_data is None:
            is_match = False
            break
        if abs(float(record.price_kwh or 0) - base_data["price_kwh"]) > 0.01:
            is_match = False
            break
        if abs(float(record.load_kw or 0) - base_data["load_kw"]) > 0.01:
            is_match = False
            break

    dataset.verify_status = "校核通过" if is_match else "校核失败"
    db.commit()
    db.refresh(dataset)
    return dataset, None


def _verify_dataset_background(dataset_id: int) -> None:
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        _verify_dataset_internal(db, dataset_id)
    finally:
        db.close()


@router.post("/{dataset_id}/verify", response_model=DatasetOut)
def verify_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Dataset:
    """
    同步校核数据集。
    """
    dataset, err = _verify_dataset_internal(db, dataset_id)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return dataset


@router.post("/{dataset_id}/verify-async", response_model=DatasetOut)
def verify_dataset_async(
    dataset_id: int,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Dataset:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")
    _ensure_allowed_dataset(dataset)
    dataset.verify_status = "校核中"
    db.commit()
    db.refresh(dataset)
    background.add_task(_verify_dataset_background, dataset_id)
    return dataset


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Dataset:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    _ensure_allowed_dataset(dataset)
    return dataset


@router.get("/{dataset_id}/download")
def download_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> FileResponse:
    """下载数据集的原始Excel文件"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")
    _ensure_allowed_dataset(dataset)
    
    # 获取关联的文件
    db_file = db.query(DatasetFile).filter(DatasetFile.dataset_id == dataset_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="数据集文件不存在")
    
    if not os.path.exists(db_file.stored_path):
        raise HTTPException(status_code=404, detail="文件已丢失")
    
    return FileResponse(db_file.stored_path, filename=db_file.original_name)


@router.put("/{dataset_id}", response_model=DatasetOut)
def update_dataset(
    dataset_id: int,
    payload: DatasetUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Dataset:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    _ensure_allowed_dataset(dataset)
    dataset.name = _ensure_allowed_dataset_name(payload.name)
    dataset.description = payload.description
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


@router.delete("/{dataset_id}")
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> dict:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    _ensure_allowed_dataset(dataset)
    
    # 删除关联的文件
    db_files = db.query(DatasetFile).filter(DatasetFile.dataset_id == dataset_id).all()
    for db_file in db_files:
        delete_file(db_file.stored_path)
    
    db.delete(dataset)
    db.commit()
    return {"message": "Deleted"}


@router.post("/upload-csv", response_model=DatasetOut)
def upload_csv_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    overwrite: bool = Form(False),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
) -> Dataset:
    """
    上传CSV数据集文件并解析导入数据。
    
    支持的CSV格式（如广东电价数据.csv）：
    - 第一行为表头
    - 必须包含：时间、电价 列
    - 可选列：负荷、温度、风速、云量、天气类型、是否节假日
    
    如果overwrite=True，会覆盖同名数据集的数据
    """
    # 验证文件类型
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="只支持CSV文件(.csv)")
    
    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件为空")
    
    # 验证CSV结构
    is_valid, error_msg = validate_csv_structure(content)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 检查是否存在同名数据集
    existing = db.query(Dataset).filter(Dataset.name == normalized_name).first()
    
    if existing:
        if overwrite:
            # 删除旧数据记录
            db.query(DatasetRecord).filter(DatasetRecord.dataset_id == existing.id).delete()
            db.commit()
            dataset = existing
        else:
            raise HTTPException(status_code=400, detail=f"数据集 '{name}' 已存在，如需覆盖请设置 overwrite=true")
    else:
        # 创建新数据集
        dataset = Dataset(
            name=normalized_name,
            description=description,
            created_by=current_admin.id,
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
    
    # 保存文件
    stored_name, stored_path = save_upload_file(content, file.filename)
    size_kb = round(len(content) / 1024, 2)
    
    # 创建或更新文件记录
    db_file = db.query(DatasetFile).filter(DatasetFile.dataset_id == dataset.id).first()
    if db_file:
        # 删除旧文件
        delete_file(db_file.stored_path)
        db_file.original_name = file.filename
        db_file.stored_path = stored_path
        db_file.size_kb = size_kb
    else:
        db_file = DatasetFile(
            dataset_id=dataset.id,
            original_name=file.filename,
            stored_path=stored_path,
            size_kb=size_kb,
            description=description,
            created_by=current_admin.id,
        )
        db.add(db_file)
    
    # 解析并导入数据
    try:
        records = parse_csv_file(content)
        batch_size = 1000
        batch = []
        
        for record_data in records:
            record = DatasetRecord(
                dataset_id=dataset.id,
                record_time=record_data.get("record_time"),
                price_kwh=record_data.get("price_kwh", 0.0),
                generation_kwh=record_data.get("generation_kwh", 0.0),
                load_kw=record_data.get("load_kw", 0.0),
                weather_type=record_data.get("weather_type", "unknown"),
                temperature=record_data.get("temperature"),
                wind_speed=record_data.get("wind_speed"),
                cloud_cover=record_data.get("cloud_cover"),
                is_holiday=record_data.get("is_holiday", False),
            )
            batch.append(record)
            
            if len(batch) >= batch_size:
                db.add_all(batch)
                db.commit()
                batch = []
        
        if batch:
            db.add_all(batch)
            db.commit()
        
        # 同时更新预测数据
        # 查找或创建关联的预测方案
        plan = db.query(Plan).filter(Plan.dataset_id == dataset.id).first()
        if not plan:
            plan = Plan(
                name=f"{name}_预测方案",
                dataset_id=dataset.id,
                plan_type="day-ahead",
                status="completed",
                description=f"从CSV导入的预测数据",
                created_by=current_admin.id,
            )
            db.add(plan)
            db.commit()
            db.refresh(plan)
        else:
            # 删除旧的预测详情
            db.query(PredictionDetail).filter(PredictionDetail.plan_id == plan.id).delete()
            db.commit()
        
        # 创建预测详情记录
        prediction_batch = []
        for record_data in records:
            price = record_data.get("price_kwh", 0.0)
            predicted = record_data.get("predicted_price", price)  # 如果CSV有预测值就用，否则用实际值
            
            detail = PredictionDetail(
                plan_id=plan.id,
                record_time=record_data.get("record_time"),
                actual_price=price,
                predicted_price=predicted,
            )
            prediction_batch.append(detail)
            
            if len(prediction_batch) >= batch_size:
                db.add_all(prediction_batch)
                db.commit()
                prediction_batch = []
        
        if prediction_batch:
            db.add_all(prediction_batch)
            db.commit()
            
    except Exception as e:
        db.rollback()
        delete_file(stored_path)
        raise HTTPException(status_code=400, detail=f"解析数据失败: {str(e)}")
    
    db.refresh(dataset)
    return dataset

    normalized_name = _ensure_allowed_dataset_name(name)
