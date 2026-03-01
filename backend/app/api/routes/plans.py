from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.deps import get_db
from app.models.plan import Plan
from app.schemas.common import Paginated
from app.schemas.plan import PlanCreate, PlanOut, PlanUpdate
from app.utils.pagination import paginate

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=Paginated[PlanOut])

def list_plans(
    page: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    dataset_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Paginated[PlanOut]:
    query = db.query(Plan)
    if keyword:
        query = query.filter(Plan.name.contains(keyword))
    if dataset_id:
        query = query.filter(Plan.dataset_id == dataset_id)
    total, items = paginate(query.order_by(Plan.id.desc()), page, size)
    return Paginated(total=total, items=items, page=page, size=size)


@router.post("", response_model=PlanOut)

def create_plan(
    payload: PlanCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
) -> Plan:
    plan = Plan(
        name=payload.name,
        plan_type=payload.plan_type,
        dataset_id=payload.dataset_id,
        status=payload.status,
        description=payload.description,
        created_by=current_admin.id,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/{plan_id}", response_model=PlanOut)

def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Plan:
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.put("/{plan_id}", response_model=PlanOut)

def update_plan(
    plan_id: int,
    payload: PlanUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Plan:
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan.name = payload.name
    plan.plan_type = payload.plan_type
    plan.dataset_id = payload.dataset_id
    plan.status = payload.status
    plan.description = payload.description
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}")

def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> dict:
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return {"message": "Deleted"}

