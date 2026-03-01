from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class PricePrediction(Base):
    """电价预测结果表 - 存储模型预测的电价数据"""
    __tablename__ = "price_prediction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    actual_price: Mapped[float] = mapped_column(Numeric(12, 4))
    predicted_price: Mapped[float] = mapped_column(Numeric(12, 4))
