from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.deps import get_db
from app.models.ranking import Ranking
from app.schemas.common import Paginated
from app.schemas.ranking import RankingOut
from app.utils.pagination import paginate

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("", response_model=Paginated[RankingOut])

def list_rankings(
    page: int = 1,
    size: int = 20,
    rank_type: Optional[str] = None,
    weather: Optional[str] = None,
    is_holiday: Optional[bool] = None,
    model_name: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Paginated[RankingOut]:
    query = db.query(Ranking)
    if rank_type:
        query = query.filter(Ranking.rank_type == rank_type)
    if weather:
        query = query.filter(Ranking.weather == weather)
    if is_holiday is not None:
        query = query.filter(Ranking.is_holiday == int(is_holiday))
    if model_name:
        query = query.filter(Ranking.model_name.contains(model_name))
    total, items = paginate(query.order_by(Ranking.id.desc()), page, size)
    return Paginated(total=total, items=items, page=page, size=size)

