from __future__ import annotations

from datetime import datetime

from sqlalchemy import Integer, String, Float, Boolean, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class MarketThermalPlant(Base):
    """火电厂信息 (来源: ROTS 44_DM&ASInputData.xlsm / UnitThermalPlants)"""
    __tablename__ = "market_thermal_plants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plant_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MarketThermalUnit(Base):
    """火电机组详细参数 (来源: ROTS 44_DM&ASInputData.xlsm / UnitThermalGenerators)"""
    __tablename__ = "market_thermal_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    unit_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    unit_name: Mapped[str] = mapped_column(String(100))
    plant_id: Mapped[str] = mapped_column(String(50), index=True)
    bus_id: Mapped[str] = mapped_column(String(50))
    capacity: Mapped[float] = mapped_column(Float)
    initial_state: Mapped[bool] = mapped_column(Boolean)
    initial_duration: Mapped[int] = mapped_column(Integer)
    min_output: Mapped[float] = mapped_column(Float)
    ramp_up: Mapped[float] = mapped_column(Float)
    ramp_down: Mapped[float] = mapped_column(Float)
    min_on_time: Mapped[int] = mapped_column(Integer)
    min_off_time: Mapped[int] = mapped_column(Integer)
    start_cost: Mapped[float] = mapped_column(Float)
    stop_cost: Mapped[float] = mapped_column(Float)
    fuel_id: Mapped[str] = mapped_column(String(50))
    cost_a: Mapped[float] = mapped_column(Float)
    cost_b: Mapped[float] = mapped_column(Float)
    cost_c: Mapped[float] = mapped_column(Float)
    freq_response: Mapped[float] = mapped_column(Float)
    freq_error: Mapped[float] = mapped_column(Float)
    reg_speed: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MarketWindUnit(Base):
    """风电机组信息 (来源: ROTS 44_DM&ASInputData.xlsm / UnitWindGenerators)"""
    __tablename__ = "market_wind_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    unit_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    unit_name: Mapped[str] = mapped_column(String(100))
    bus_id: Mapped[str] = mapped_column(String(50))
    capacity: Mapped[float] = mapped_column(Float)
    curve_name: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MarketSolarUnit(Base):
    """光伏机组信息 (来源: ROTS 44_DM&ASInputData.xlsm / UnitSolarGenerators)"""
    __tablename__ = "market_solar_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    unit_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    unit_name: Mapped[str] = mapped_column(String(100))
    bus_id: Mapped[str] = mapped_column(String(50))
    capacity: Mapped[float] = mapped_column(Float)
    curve_name: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MarketClearingHistory(Base):
    """成交历史数据 (来源: ROTS_合并数据_按顺序.xlsx)
    每行存一个指标的所有时段数据(JSON数组)
    """
    __tablename__ = "market_clearing_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metric_name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    period_values: Mapped[dict] = mapped_column(JSON)
    total_periods: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MarketOutResult(Base):
    """市场出清结果时序数据 (来源: out.xlsx)
    每行存一个sheet中一个单元(机组/节点)的96个时段数据
    """
    __tablename__ = "market_out_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sheet_name: Mapped[str] = mapped_column(String(100), index=True)
    row_index: Mapped[int] = mapped_column(Integer)
    period_values: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MarketDayAheadQuote(Base):
    """日前市场机组报价 (来源: ROTS 44_DM&ASInputData.xlsm / MarDayAheadUnitQuotes)"""
    __tablename__ = "market_day_ahead_quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quote_id: Mapped[int] = mapped_column(Integer)
    unit_id: Mapped[str] = mapped_column(String(50), index=True)
    market_name: Mapped[str] = mapped_column(String(50))
    quote_time: Mapped[int] = mapped_column(Integer)
    quote_section: Mapped[str] = mapped_column(String(50))
    quote_price: Mapped[float] = mapped_column(Float)
    quote_quantity: Mapped[float] = mapped_column(Float)
    is_used: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)





class MarketLoad(Base):
    """负荷数据 (来源: ROTS 44_DM&ASInputData.xlsm / Loads)"""
    __tablename__ = "market_loads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    load_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    load_name: Mapped[str] = mapped_column(String(100))
    bus_id: Mapped[str] = mapped_column(String(50))
    load_curve_name: Mapped[str] = mapped_column(String(100))
    capacity_ratio: Mapped[float] = mapped_column(Float)
    responsiveness: Mapped[float] = mapped_column(Float)
    is_interrupt: Mapped[bool] = mapped_column(Boolean)
    is_transfer: Mapped[bool] = mapped_column(Boolean)
    interrupt_cost: Mapped[float] = mapped_column(Float)
    transfer_cost: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
