"""电力市场平台API"""
from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.deps import get_db
from app.models.market import (
    MarketThermalPlant,
    MarketThermalUnit,
    MarketWindUnit,
    MarketSolarUnit,
    MarketClearingHistory,
    MarketOutResult,
    MarketDayAheadQuote,
    MarketLoad,
)

router = APIRouter()


# ==================== 企业信息 ====================

@router.get("/companies")
def get_companies(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """获取火电厂列表及其机组"""
    plants = db.query(MarketThermalPlant).order_by(MarketThermalPlant.id).all()
    result = []
    for p in plants:
        units = db.query(MarketThermalUnit).filter(
            MarketThermalUnit.plant_id == p.plant_id
        ).order_by(MarketThermalUnit.id).all()
        result.append({
            "id": p.plant_id,
            "name": p.name,
            "units": [
                {
                    "id": u.unit_id,
                    "bus": u.bus_id,
                    "capacity": u.capacity,
                    "initState": "TRUE" if u.initial_state else "FALSE",
                    "initDuration": u.initial_duration,
                    "minOutput": u.min_output,
                    "rampUp": u.ramp_up,
                    "rampDown": u.ramp_down,
                    "minOnTime": u.min_on_time,
                    "minOffTime": u.min_off_time,
                    "startCost": u.start_cost,
                    "stopCost": u.stop_cost,
                    "fuel": u.fuel_id,
                    "costA": u.cost_a,
                    "costB": u.cost_b,
                    "costC": u.cost_c,
                    "freqResp": round(u.freq_response, 6),
                    "freqErr": round(u.freq_error, 6),
                    "regSpeed": round(u.reg_speed, 6),
                }
                for u in units
            ],
        })
    return {"items": result}


@router.get("/wind-units")
def get_wind_units(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """获取风电机组列表"""
    units = db.query(MarketWindUnit).order_by(MarketWindUnit.id).all()
    return {
        "items": [
            {
                "id": u.unit_id,
                "name": u.unit_name,
                "bus": u.bus_id,
                "capacity": u.capacity,
                "curveName": u.curve_name,
            }
            for u in units
        ]
    }


@router.get("/solar-units")
def get_solar_units(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """获取光伏机组列表"""
    units = db.query(MarketSolarUnit).order_by(MarketSolarUnit.id).all()
    return {
        "items": [
            {
                "id": u.unit_id,
                "name": u.unit_name,
                "bus": u.bus_id,
                "capacity": u.capacity,
                "curveName": u.curve_name,
            }
            for u in units
        ]
    }


# ==================== 成交历史 ====================

@router.get("/clearing-history")
def get_clearing_history(
    metric: Optional[str] = None,
    start: int = 0,
    limit: int = 96,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """获取成交历史数据
    metric: 指标名称(出清电价/风电消纳功率/光伏消纳功率/总负荷功率/供需比)，为空返回所有
    start/limit: 时段范围切片
    """
    query = db.query(MarketClearingHistory)
    if metric:
        query = query.filter(MarketClearingHistory.metric_name == metric)
    rows = query.all()
    result = []
    for r in rows:
        values = r.period_values
        sliced = values[start:start + limit] if isinstance(values, list) else []
        result.append({
            "metric_name": r.metric_name,
            "total_periods": r.total_periods,
            "values": sliced,
        })
    return {"items": result, "start": start, "limit": limit}


# ==================== 信息披露 (出清结果) ====================

@router.get("/out-results")
def get_out_results(
    sheet: str = "energy_price",
    row_index: Optional[int] = None,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """获取市场出清结果数据
    sheet: out.xlsx中的sheet名称
    row_index: 指定行索引，为空返回全部行
    """
    query = db.query(MarketOutResult).filter(MarketOutResult.sheet_name == sheet)
    if row_index is not None:
        query = query.filter(MarketOutResult.row_index == row_index)
    rows = query.order_by(MarketOutResult.row_index).all()
    return {
        "items": [
            {
                "sheet_name": r.sheet_name,
                "row_index": r.row_index,
                "values": r.period_values,
            }
            for r in rows
        ]
    }


# ==================== 市场交易 ====================

@router.get("/day-ahead-quotes")
def get_day_ahead_quotes(
    unit_id: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """获取日前市场报价"""
    query = db.query(MarketDayAheadQuote)
    if unit_id:
        query = query.filter(MarketDayAheadQuote.unit_id == unit_id)
    quotes = query.order_by(MarketDayAheadQuote.quote_id).all()
    return {
        "items": [
            {
                "quote_id": q.quote_id,
                "unit_id": q.unit_id,
                "market_name": q.market_name,
                "quote_time": q.quote_time,
                "quote_section": q.quote_section,
                "quote_price": q.quote_price,
                "quote_quantity": q.quote_quantity,
                "is_used": q.is_used,
            }
            for q in quotes
        ]
    }





# ==================== 结算报告 ====================

@router.get("/settlement-overview")
def get_settlement_overview(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """获取结算报告市场总览数据 - 从数据库聚合计算"""
    # 机组统计
    thermal_count = db.query(MarketThermalUnit).count()
    wind_count = db.query(MarketWindUnit).count()
    solar_count = db.query(MarketSolarUnit).count()
    plant_count = db.query(MarketThermalPlant).count()

    thermal_cap = db.query(func.sum(MarketThermalUnit.capacity)).scalar() or 0
    wind_cap = db.query(func.sum(MarketWindUnit.capacity)).scalar() or 0
    solar_cap = db.query(func.sum(MarketSolarUnit.capacity)).scalar() or 0
    total_cap = float(thermal_cap) + float(wind_cap) + float(solar_cap)

    # 从出清结果获取电价数据
    energy_rows = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "energy_price"
    ).all()

    all_prices = []
    for r in energy_rows:
        if isinstance(r.period_values, list):
            all_prices.extend([float(v) for v in r.period_values if v])

    max_price = max(all_prices) if all_prices else 0
    min_price = min(all_prices) if all_prices else 0
    avg_price = sum(all_prices) / len(all_prices) if all_prices else 0

    # 火电运行功率
    thermal_power_rows = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "thermal_tg_opera_power"
    ).all()
    total_output = 0
    for r in thermal_power_rows:
        if isinstance(r.period_values, list):
            total_output += sum(float(v) for v in r.period_values if v)

    # 成交历史供需比
    ratio_row = db.query(MarketClearingHistory).filter(
        MarketClearingHistory.metric_name == "供需比"
    ).first()
    avg_ratio = 0
    if ratio_row and isinstance(ratio_row.period_values, list) and ratio_row.period_values:
        avg_ratio = sum(ratio_row.period_values) / len(ratio_row.period_values)

    # 日前报价统计
    quote_count = db.query(MarketDayAheadQuote).count()
    avg_quote_price = db.query(func.avg(MarketDayAheadQuote.quote_price)).scalar() or 0
    total_quote_quantity = db.query(func.sum(MarketDayAheadQuote.quote_quantity)).scalar() or 0



    # 中标机组数（运行功率>0的机组）
    bid_units = 0
    for r in thermal_power_rows:
        if isinstance(r.period_values, list):
            if any(float(v) > 0 for v in r.period_values if v):
                bid_units += 1
    # 加上风电和光伏
    wind_power_rows = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "wind_wt_opera_power"
    ).all()
    solar_power_rows = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "solar_pv_opera_power"
    ).all()
    for r in wind_power_rows + solar_power_rows:
        if isinstance(r.period_values, list):
            if any(float(v) > 0 for v in r.period_values if v):
                bid_units += 1

    # 总交易额 = sum(电价 * 出力) 的近似值
    total_revenue = round(total_output * avg_price / 10000, 6) if avg_price else 0

    # 风电总出力
    wind_total_output = 0
    for r in wind_power_rows:
        if isinstance(r.period_values, list):
            wind_total_output += sum(float(v) for v in r.period_values if v)

    # 光伏总出力
    solar_total_output = 0
    for r in solar_power_rows:
        if isinstance(r.period_values, list):
            solar_total_output += sum(float(v) for v in r.period_values if v)

    # 负荷总量
    load_rows = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "load_load_bid_power"
    ).all()
    total_load = 0
    for r in load_rows:
        if isinstance(r.period_values, list):
            total_load += sum(float(v) for v in r.period_values if v)

    # 总发电量 = 火电+风电+光伏
    total_generation = total_output + wind_total_output + solar_total_output

    # 新能源弃电量
    wind_curtailment = 0  # 当前数据中无弃电
    max_re_curtailment_ratio = 0

    # 申报机组数 = 有报价的机组数
    quote_unit_count = db.query(MarketDayAheadQuote.unit_id).distinct().count()

    energy_market = {
        "total_capacity": round(total_cap, 2),
        "wind_count": wind_count,
        "wind_capacity": round(float(wind_cap), 2),
        "solar_count": solar_count,
        "solar_capacity": round(float(solar_cap), 2),
        "hydro_count": 0,
        "hydro_capacity": 0,
        "thermal_count": thermal_count,
        "thermal_capacity": round(float(thermal_cap), 2),
        "storage_count": 0,
        "pumped_storage_count": 0,
        "plant_count": plant_count,
        "total_output": round(total_output + wind_total_output + solar_total_output, 6),
        "avg_price": round(avg_price, 6),
        "supply_demand_ratio": round(avg_ratio, 6),
        "total_revenue": round(total_revenue, 6),
        "congestion": "",
        "congestion_surplus": 0,
        "quote_unit_count": quote_unit_count,
        "bid_units": bid_units,
        "quote_quantity": round(float(total_quote_quantity), 2),
        "avg_quote_price": round(float(avg_quote_price), 6),
        "max_node_price": round(max_price, 6),
        "min_node_price": round(min_price, 6),
        "transmission_loss": 0,
        "total_generation": round(total_generation, 6),
        "total_consumption": round(total_load, 6),
        "re_curtailment": round(wind_curtailment, 6),
        "max_re_curtailment_ratio": round(max_re_curtailment_ratio, 6),
        "total_load_shedding": 0,
        "max_load_loss_ratio": 0,
    }

    return {
        "energy_market": energy_market,
    }


@router.get("/settlement-detail")
def get_settlement_detail(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """获取结算详情 - 按火电厂汇总"""
    plants = db.query(MarketThermalPlant).order_by(MarketThermalPlant.id).all()

    # 获取所有火电运行数据
    opera_power = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "thermal_tg_opera_power"
    ).order_by(MarketOutResult.row_index).all()

    quote_cost = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "thermal_tg_quote_cost"
    ).order_by(MarketOutResult.row_index).all()

    start_flags = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "thermal_tg_start_flag"
    ).order_by(MarketOutResult.row_index).all()

    off_flags = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "thermal_tg_off_flag"
    ).order_by(MarketOutResult.row_index).all()

    # 获取节点电价
    energy_prices = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "energy_price"
    ).order_by(MarketOutResult.row_index).all()

    # 机组到电厂映射
    units = db.query(MarketThermalUnit).order_by(MarketThermalUnit.id).all()
    unit_plant_map = {u.unit_id: u.plant_id for u in units}
    unit_start_cost_map = {u.unit_id: u.start_cost for u in units}
    unit_stop_cost_map = {u.unit_id: u.stop_cost for u in units}

    # 按电厂聚合
    plant_data = {}
    for p in plants:
        plant_data[p.plant_id] = {
            "id": p.plant_id,
            "name": p.name,
            "opCost": 0,
            "startCost": 0,
            "stopCost": 0,
            "output": 0,
            "revenue": 0,
        }

    # 按行索引对应机组 (row_index 0 -> Thermal_1, etc.)
    for idx, row in enumerate(opera_power):
        unit_id = f"Thermal_{idx + 1}"
        plant_id = unit_plant_map.get(unit_id)
        if not plant_id or plant_id not in plant_data:
            continue
        vals = row.period_values if isinstance(row.period_values, list) else []
        total_power = sum(float(v) for v in vals if v)
        plant_data[plant_id]["output"] += total_power

    for idx, row in enumerate(quote_cost):
        unit_id = f"Thermal_{idx + 1}"
        plant_id = unit_plant_map.get(unit_id)
        if not plant_id or plant_id not in plant_data:
            continue
        vals = row.period_values if isinstance(row.period_values, list) else []
        total_cost = sum(float(v) for v in vals if v)
        plant_data[plant_id]["opCost"] += total_cost

    for idx, row in enumerate(start_flags):
        unit_id = f"Thermal_{idx + 1}"
        plant_id = unit_plant_map.get(unit_id)
        if not plant_id or plant_id not in plant_data:
            continue
        vals = row.period_values if isinstance(row.period_values, list) else []
        starts = sum(1 for v in vals if float(v) > 0)
        plant_data[plant_id]["startCost"] += starts * unit_start_cost_map.get(unit_id, 0)

    for idx, row in enumerate(off_flags):
        unit_id = f"Thermal_{idx + 1}"
        plant_id = unit_plant_map.get(unit_id)
        if not plant_id or plant_id not in plant_data:
            continue
        vals = row.period_values if isinstance(row.period_values, list) else []
        stops = sum(1 for v in vals if float(v) > 0)
        plant_data[plant_id]["stopCost"] += stops * unit_stop_cost_map.get(unit_id, 0)

    # 计算均价和收益
    avg_energy_price = 0
    if energy_prices:
        all_prices = []
        for r in energy_prices:
            if isinstance(r.period_values, list):
                all_prices.extend([float(v) for v in r.period_values if v])
        if all_prices:
            avg_energy_price = sum(all_prices) / len(all_prices)

    energy_rows = []
    for pid in [p.plant_id for p in plants]:
        d = plant_data[pid]
        revenue = d["output"] * avg_energy_price / 10000
        net = revenue - d["opCost"] - d["startCost"] - d["stopCost"]
        avg_p = avg_energy_price if d["output"] > 0 else 0
        energy_rows.append({
            "id": d["id"],
            "name": d["name"],
            "opCost": round(d["opCost"], 3),
            "startCost": round(d["startCost"], 3),
            "stopCost": round(d["stopCost"], 3),
            "output": round(d["output"], 3),
            "avgPrice": round(avg_p, 3),
            "revenue": round(revenue, 3),
            "netIncome": round(net, 3),
        })

    return {"energy_rows": energy_rows}


@router.get("/balance-chart")
def get_balance_chart(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """获取电力电量平衡图表数据"""
    # 火电总功率
    thermal_rows = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "thermal_tg_opera_power"
    ).all()
    periods = 96
    thermal_power = [0.0] * periods
    for r in thermal_rows:
        if isinstance(r.period_values, list):
            for i, v in enumerate(r.period_values[:periods]):
                thermal_power[i] += float(v) if v else 0

    # 风电消纳功率
    wind_rows = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "wind_wt_opera_power"
    ).all()
    wind_power = [0.0] * periods
    for r in wind_rows:
        if isinstance(r.period_values, list):
            for i, v in enumerate(r.period_values[:periods]):
                wind_power[i] += float(v) if v else 0

    # 光伏功率
    solar_rows = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "solar_pv_opera_power"
    ).all()
    solar_power = [0.0] * periods
    for r in solar_rows:
        if isinstance(r.period_values, list):
            for i, v in enumerate(r.period_values[:periods]):
                solar_power[i] += float(v) if v else 0

    # 水电功率
    hydro_rows = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "hydro_hp_opera_power"
    ).all()
    hydro_power = [0.0] * periods
    for r in hydro_rows:
        if isinstance(r.period_values, list):
            for i, v in enumerate(r.period_values[:periods]):
                hydro_power[i] += float(v) if v else 0

    # 负荷功率
    load_rows = db.query(MarketOutResult).filter(
        MarketOutResult.sheet_name == "load_load_bid_power"
    ).all()
    load_power = [0.0] * periods
    for r in load_rows:
        if isinstance(r.period_values, list):
            for i, v in enumerate(r.period_values[:periods]):
                load_power[i] += float(v) if v else 0

    return {
        "thermal": [round(v, 4) for v in thermal_power],
        "wind": [round(v, 4) for v in wind_power],
        "solar": [round(v, 4) for v in solar_power],
        "hydro": [round(v, 4) for v in hydro_power],
        "load": [round(v, 4) for v in load_power],
        "periods": periods,
    }
