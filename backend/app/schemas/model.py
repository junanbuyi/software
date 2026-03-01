from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ModelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    dataset_id: int
    train_start_date: date
    train_end_date: date
    prediction_type: str  # 'day_ahead' | 'week_ahead'


class ModelOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    file_path: str
    original_name: str
    dataset_id: int
    train_start_date: date
    train_end_date: date
    prediction_type: str
    status: str
    trained_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelTrainResponse(BaseModel):
    id: int
    status: str
    trained_at: Optional[datetime]
    message: str
