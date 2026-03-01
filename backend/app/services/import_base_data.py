"""导入基础数据到数据库"""
from __future__ import annotations

import csv
import os
from datetime import datetime
from io import StringIO

from sqlalchemy.orm import Session

from app.models.base_prediction_data import BasePredictionData
from app.models.base_price_data import BasePriceData
from app.models.tcn_prediction import TcnProbPrediction


def parse_datetime(date_str: str) -> datetime:
    """解析日期时间字符串"""
    formats = [
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析日期: {date_str}")


def read_csv_file(csv_path: str) -> str:
    """读取CSV文件，自动检测编码"""
    for encoding in ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'gb18030']:
        try:
            with open(csv_path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"无法解码文件: {csv_path}")


def import_base_price_data(db: Session, csv_path: str) -> int:
    """
    导入基础电价数据
    CSV格式: 时间,电价(元/kWh),负荷(kW),温度(℃),风速(m/s),云量(%)
    """
    if not os.path.exists(csv_path):
        print(f"[警告] 文件不存在: {csv_path}")
        return 0
    
    # 检查是否已有数据
    existing_count = db.query(BasePriceData).count()
    if existing_count > 0:
        print(f"[跳过] 基础电价数据已存在 ({existing_count} 条)")
        return existing_count
    
    # 读取CSV文件
    try:
        content = read_csv_file(csv_path)
    except ValueError as e:
        print(f"[错误] {e}")
        return 0
    
    reader = csv.reader(StringIO(content))
    rows = list(reader)
    
    if len(rows) < 2:
        print("[警告] CSV文件数据不足")
        return 0
    
    count = 0
    batch_size = 1000
    for row in rows[1:]:  # 跳过表头
        if len(row) < 6:
            continue
        try:
            record = BasePriceData(
                record_time=parse_datetime(row[0]),
                price_kwh=float(row[1]) if row[1] else 0.0,
                load_kw=float(row[2]) if row[2] else 0.0,
                temperature=float(row[3]) if row[3] else None,
                wind_speed=float(row[4]) if row[4] else None,
                cloud_cover=float(row[5]) if row[5] else None,
            )
            db.add(record)
            count += 1
            if count % batch_size == 0:
                db.commit()
        except Exception as e:
            print(f"[警告] 解析行失败: {row}, 错误: {e}")
            continue
    
    db.commit()
    print(f"[成功] 导入基础电价数据 {count} 条")
    return count


def import_base_prediction_data(db: Session, csv_path: str) -> int:
    """
    导入基础预测数据
    CSV格式: date,y_test_true,y_test_pred
    """
    if not os.path.exists(csv_path):
        print(f"[警告] 文件不存在: {csv_path}")
        return 0
    
    # 检查是否已有数据
    existing_count = db.query(BasePredictionData).count()
    if existing_count > 0:
        print(f"[跳过] 基础预测数据已存在 ({existing_count} 条)")
        return existing_count
    
    # 读取CSV文件
    try:
        content = read_csv_file(csv_path)
    except ValueError as e:
        print(f"[错误] {e}")
        return 0
    
    reader = csv.reader(StringIO(content))
    rows = list(reader)
    
    if len(rows) < 2:
        print("[警告] CSV文件数据不足")
        return 0
    
    count = 0
    batch_size = 1000
    for row in rows[1:]:  # 跳过表头
        if len(row) < 3:
            continue
        try:
            record = BasePredictionData(
                record_time=parse_datetime(row[0]),
                actual_price=float(row[1]) if row[1] else 0.0,
                predicted_price=float(row[2]) if row[2] else 0.0,
            )
            db.add(record)
            count += 1
            # 分批提交
            if count % batch_size == 0:
                db.commit()
        except Exception as e:
            print(f"[警告] 解析行失败: {row}, 错误: {e}")
            continue
    
    db.commit()
    print(f"[成功] 导入基础预测数据 {count} 条")
    return count


def import_tcn_prob_data(db: Session, csv_path: str) -> int:
    """
    导入TCN概率预测数据
    CSV格式: real,QR-0.005,QR-0.025,QR-0.05,QR-0.5,QR-0.95,QR-0.975,QR-0.995
    无时间列，使用base_prediction_data的时间对齐（每小时取一个点）
    """
    if not os.path.exists(csv_path):
        print(f"[警告] TCN文件不存在: {csv_path}")
        return 0

    existing_count = db.query(TcnProbPrediction).count()
    if existing_count > 0:
        print(f"[跳过] TCN概率预测数据已存在 ({existing_count} 条)")
        return existing_count

    # 获取base_prediction_data的时间序列（每小时取一个点）
    from sqlalchemy import func
    hourly_times = (
        db.query(BasePredictionData.record_time)
        .order_by(BasePredictionData.record_time.asc())
        .all()
    )
    # 每小时取一个点（每4条15分钟数据取第1条）
    hourly_time_list = []
    seen_hours = set()
    for (rt,) in hourly_times:
        hour_key = rt.replace(minute=0, second=0, microsecond=0)
        if hour_key not in seen_hours:
            seen_hours.add(hour_key)
            hourly_time_list.append(hour_key)

    try:
        content = read_csv_file(csv_path)
    except ValueError as e:
        print(f"[错误] {e}")
        return 0

    reader = csv.reader(StringIO(content))
    header = next(reader)
    rows = list(reader)

    count = 0
    batch_size = 500
    for i, row in enumerate(rows):
        if len(row) < 8:
            continue
        # 使用对齐的时间，如果超出范围则按小时递增
        if i < len(hourly_time_list):
            record_time = hourly_time_list[i]
        else:
            from datetime import timedelta
            last_time = hourly_time_list[-1] if hourly_time_list else datetime(2024, 3, 22)
            record_time = last_time + timedelta(hours=i - len(hourly_time_list) + 1)

        try:
            record = TcnProbPrediction(
                record_time=record_time,
                real=float(row[0]),
                qr_005=float(row[1]),
                qr_025=float(row[2]),
                qr_05=float(row[3]),
                qr_50=float(row[4]),
                qr_95=float(row[5]),
                qr_975=float(row[6]),
                qr_995=float(row[7]),
            )
            db.add(record)
            count += 1
            if count % batch_size == 0:
                db.commit()
        except Exception as e:
            print(f"[警告] TCN行解析失败: {row}, 错误: {e}")
            continue

    db.commit()
    print(f"[成功] 导入TCN概率预测数据 {count} 条")
    return count


def import_all_base_data(db: Session, base_dir: str = None) -> dict:
    """导入所有基础数据"""
    if base_dir is None:
        # 默认使用项目根目录
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    price_csv = os.path.join(base_dir, "广东电价数据.csv")
    prediction_csv = os.path.join(base_dir, "广东电价预测结果.csv")
    tcn_csv = os.path.join(
        base_dir, "epf", "results", "sxinput_20260128_213253",
        "tcn", "predictions", "tcn_predictions_len1.csv"
    )
    
    return {
        "price_data": import_base_price_data(db, price_csv),
        "prediction_data": import_base_prediction_data(db, prediction_csv),
        "tcn_prob_data": import_tcn_prob_data(db, tcn_csv),
    }
