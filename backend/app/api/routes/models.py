from __future__ import annotations

import os
import re
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.config import get_settings
from app.db.deps import get_db
from app.models.dataset import Dataset
from app.models.model import Model
from app.schemas.common import Paginated
from app.schemas.model import (
    EpfAutoTrainResponse,
    EpfCandidateOut,
    ModelOut,
    ModelTrainResponse,
)
from app.services.epf_model_selector import load_epf_model_metrics, score_epf_metrics, select_best_epf_model
from app.services.storage_service import delete_file, save_upload_file
from app.utils.pagination import paginate

router = APIRouter(prefix="/models", tags=["models"])

EPF_SEED_MODELS = [
    ("TCN周前概率", "EPF TCN 概率预测"),
    ("Mamba周前概率", "EPF Mamba 概率预测"),
    ("NLinear周前概率", "EPF NLinear 概率预测"),
    ("集成周前概率", "EPF Ensemble 概率预测"),
]


@router.get("", response_model=Paginated[ModelOut])
def list_models(
    page: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Paginated[ModelOut]:
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
    if not (file.filename or "").endswith(".py"):
        raise HTTPException(status_code=400, detail="Only Python model files (.py) are supported.")

    if prediction_type != "week_ahead":
        raise HTTPException(status_code=400, detail="Only week_ahead is supported.")

    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded model file is empty.")

    _, stored_path = save_upload_file(content, file.filename or "model.py")

    model = Model(
        name=name,
        description=description,
        file_path=stored_path,
        original_name=file.filename or "model.py",
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


@router.post("/seed-epf")
def seed_epf_models(
    dataset_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> dict:
    if dataset_id is not None:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    else:
        dataset = db.query(Dataset).filter(Dataset.name == "广东电价数据").first()
    if not dataset:
        raise HTTPException(status_code=400, detail="Dataset not found for EPF seed.")

    created = 0
    existing = 0
    items = []
    for name, desc in EPF_SEED_MODELS:
        model = db.query(Model).filter(Model.name == name, Model.dataset_id == dataset.id).first()
        if model:
            existing += 1
        else:
            model = Model(
                name=name,
                description=desc,
                file_path="epf_stub.py",
                original_name="epf_stub.py",
                dataset_id=dataset.id,
                train_start_date=date(2024, 1, 1),
                train_end_date=date(2024, 12, 31),
                prediction_type="week_ahead",
                status="untrained",
            )
            db.add(model)
            db.commit()
            db.refresh(model)
            created += 1
        items.append({"id": model.id, "name": model.name})

    return {
        "dataset_id": dataset.id,
        "created": created,
        "existing": existing,
        "items": items,
    }


def _sanitize_model_name(model_name: str) -> str:
    sanitized = re.sub(r"[^a-zA-Z0-9_\-\u4e00-\u9fff]+", "_", model_name).strip("_")
    return sanitized or "model"


def _trained_model_dir(model_name: str) -> Path:
    settings = get_settings()
    base = Path(settings.upload_dir) / "trained_models" / _sanitize_model_name(model_name)
    base.mkdir(parents=True, exist_ok=True)
    return base


def _match_epf_folder(model_name: str) -> Optional[str]:
    name = model_name.lower()
    if "ensemble" in name or "集成" in model_name:
        return "ensemble"
    if "mamba" in name:
        return "mamba"
    if "nlinear" in name:
        return "nlinear"
    if "tcn" in name:
        return "tcn"
    return None


def _latest_epf_results_json(model_name: str) -> Optional[Path]:
    folder = _match_epf_folder(model_name)
    if not folder:
        return None
    root = Path(__file__).resolve().parents[4] / "epf" / folder
    candidates = list(root.glob("results/**/results.json"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


@router.post("/trained-files/upload")
def upload_trained_file(
    model_name: str = Form(...),
    file: UploadFile = File(...),
    _admin=Depends(get_current_admin),
) -> dict:
    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    file_name = file.filename or "trained_model.bin"
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    stored_name = f"{timestamp}_{uuid.uuid4().hex}_{file_name}"
    target_path = _trained_model_dir(model_name) / stored_name
    target_path.write_bytes(content)

    return {
        "message": "Trained file uploaded.",
        "model_name": model_name,
        "stored_name": stored_name,
    }


@router.get("/trained-files/download")
def download_trained_file(
    model_name: str,
    _admin=Depends(get_current_admin),
) -> FileResponse:
    model_dir = _trained_model_dir(model_name)
    uploaded_files = [p for p in model_dir.iterdir() if p.is_file()]
    if uploaded_files:
        latest_uploaded = max(uploaded_files, key=lambda p: p.stat().st_mtime)
        return FileResponse(str(latest_uploaded), filename=latest_uploaded.name)

    fallback = _latest_epf_results_json(model_name)
    if fallback and fallback.exists():
        return FileResponse(str(fallback), filename=f"{_sanitize_model_name(model_name)}_latest_results.json")

    raise HTTPException(
        status_code=404,
        detail="No trained file found for this model. Please upload one first.",
    )


@router.post("/auto-train", response_model=EpfAutoTrainResponse)
def auto_train_with_epf(
    _admin=Depends(get_current_admin),
) -> EpfAutoTrainResponse:
    """
    Evaluate EPF model outputs with weighted metrics and automatically select
    the best model.
    """
    try:
        selection = select_best_epf_model()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    candidates = [
        EpfCandidateOut(
            model_name=item.model_name,
            score=item.score,
            mape_150=item.metrics["MAPE_150"],
            mae=item.metrics["MAE"],
            rmse=item.metrics["RMSE"],
            r2=item.metrics["R2"],
            source_file=item.source_file,
        )
        for item in selection.candidates
    ]

    return EpfAutoTrainResponse(
        selected_model=selection.selected_model,
        selected_score=selection.selected_score,
        retrained=selection.retrained,
        used_cache=selection.used_cache,
        candidates=candidates,
        message=(
            f"Best model: {selection.selected_model}. "
            f"{selection.detail}"
        ),
    )


@router.get("/{model_id}", response_model=ModelOut)
def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Model:
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found.")
    return model


@router.post("/{model_id}/train", response_model=ModelTrainResponse)
def train_model(
    model_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ModelTrainResponse:
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found.")

    try:
        metrics, source_file = load_epf_model_metrics(model.name)
        score = score_epf_metrics(metrics)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    model.status = "trained"
    model.trained_at = datetime.utcnow()
    model.description = _append_auto_selection_note(
        model.description,
        model.name,
        score,
    )
    db.add(model)
    db.commit()
    db.refresh(model)

    return ModelTrainResponse(
        id=model.id,
        status=model.status,
        trained_at=model.trained_at,
        selected_model=model.name,
        selected_score=score,
        retrained=False,
        used_cache=True,
        message=(
            f"Training completed for model: {model.name}. "
            f"Loaded metrics from {source_file}."
        ),
    )


def _append_auto_selection_note(
    description: Optional[str],
    selected_model: str,
    selected_score: float,
) -> str:
    note = f"[EPF_AUTO_SELECTED] {selected_model} (score={selected_score:.6f})"
    if not description:
        return note

    cleaned_lines = [
        line
        for line in description.splitlines()
        if not line.strip().startswith("[EPF_AUTO_SELECTED]")
    ]
    cleaned_lines.append(note)
    return "\n".join(cleaned_lines)


@router.delete("/{model_id}")
def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> dict:
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found.")

    delete_file(model.file_path)
    db.delete(model)
    db.commit()
    return {"message": "Deleted"}
