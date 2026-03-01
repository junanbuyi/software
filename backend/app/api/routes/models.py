from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.deps import get_db
from app.models.model import Model
from app.schemas.common import Paginated
from app.schemas.model import ModelOut, ModelTrainResponse
from app.services.storage_service import delete_file, save_upload_file
from app.utils.pagination import paginate

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=Paginated[ModelOut])
def list_models(
    page: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Paginated[ModelOut]:
    """获取模型列表"""
    query = db.query(Model)
    if keyword:
        query = query.filter(Model.name.contains(keyword))
    if status:
        query = query.filter(Model.status == status)
    total, items = paginate(query.order_by(Model.id.desc()), page, size)
    return Paginated(total=total, items=items, page=page, size=size)


@router.post("/upload", response_model=ModelOut)
def upload_model(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    dataset_id: int = Form(...),
    train_start_date: str = Form(...),
    train_end_date: str = Form(...),
    prediction_type: str = Form(...),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Model:
    """上传模型文件"""
    # 验证文件类型
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="只支持Python文件(.py)")
    
    # 验证预测类型
    if prediction_type not in ("day_ahead", "week_ahead"):
        raise HTTPException(status_code=400, detail="预测类型必须是 day_ahead 或 week_ahead")
    
    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件为空")
    
    stored_name, stored_path = save_upload_file(content, file.filename)
    
    model = Model(
        name=name,
        description=description,
        file_path=stored_path,
        original_name=file.filename,
        dataset_id=dataset_id,
        train_start_date=train_start_date,
        train_end_date=train_end_date,
        prediction_type=prediction_type,
        status="untrained",
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


@router.get("/{model_id}", response_model=ModelOut)
def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Model:
    """获取模型详情"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    return model


@router.post("/{model_id}/train", response_model=ModelTrainResponse)
def train_model(
    model_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ModelTrainResponse:
    """训练模型"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    if model.status == "trained":
        raise HTTPException(status_code=400, detail="模型已训练")
    
    # TODO: 实际的模型训练逻辑
    # 目前只更新状态
    model.status = "trained"
    model.trained_at = datetime.utcnow()
    db.add(model)
    db.commit()
    db.refresh(model)
    
    return ModelTrainResponse(
        id=model.id,
        status=model.status,
        trained_at=model.trained_at,
        message="训练完成"
    )


@router.delete("/{model_id}")
def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> dict:
    """删除模型"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    # 删除物理文件
    delete_file(model.file_path)
    
    db.delete(model)
    db.commit()
    return {"message": "删除成功"}
