from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.session import Base, get_engine
from app.services.seed_service import seed_demo_data
from app.services.import_base_data import import_all_base_data


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    with Session(bind=engine) as db:
        seed_demo_data(db)
        import_all_base_data(db)

