from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PlanBase(BaseModel):
    name: str
    plan_type: str
    dataset_id: Optional[int] = None
    status: str
    description: Optional[str] = None


class PlanCreate(PlanBase):
    pass


class PlanUpdate(PlanBase):
    pass


class PlanOut(PlanBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

