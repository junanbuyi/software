"""CSV文件解析服务"""
from __future__ import annotations

from datetime import datetime
from io import StringIO
from typing import List, Dict, Any
import csv


def parse_csv_file(file_content: bytes, encoding: str = 'utf-8') -> List[Dict[str, Any]]:
    """
    解析CSV文件内容。
    
    期望的CSV格式（如广东电价数据.csv）：
    - 第一行为表头
    - 列：时间, 电价(元/kWh), 负荷(kW), 温度(℃), 风速(m/s), 云量(%)
    
    Args:
        file_content: CSV文件的字节内容
        encoding: 文件编码，默认utf-8，也支持gbk
    
    Returns:
        解析后的记录列表
    """
    # 尝试不同编码
    text_content = None
    for enc in [encoding, 'gbk', 'utf-8-sig', 'latin1']:
        try:
            text_content = file_content.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    
    if text_content is None:
        raise ValueError("无法解析文件编码")
    
    reader = csv.reader(StringIO(text_content))
    headers = next(reader)
    headers = [h.strip() for h in headers]
    
    records = []
    for row in reader:
        if not any(row):
            continue
        
        record = {}
        for col_idx, cell in enumerate(row):
            if col_idx >= len(headers):
                continue
            
            header = headers[col_idx].lower()
            cell = cell.strip()
            
            # 映射列名到字段名
            if "时间" in header or "time" in header or "date" in header:
                if cell:
                    try:
                        record["record_time"] = datetime.strptime(cell, "%Y/%m/%d %H:%M")
                    except ValueError:
                        try:
                            record["record_time"] = datetime.strptime(cell, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            try:
                                record["record_time"] = datetime.strptime(cell, "%Y-%m-%d %H:%M")
                            except ValueError:
                                try:
                                    record["record_time"] = datetime.strptime(cell, "%Y-%m-%d")
                                except ValueError:
                                    record["record_time"] = None
            
            elif "电价" in header or "price" in header:
                record["price_kwh"] = float(cell) if cell else 0.0
            
            elif "负荷" in header or "load" in header:
                record["load_kw"] = float(cell) if cell else 0.0
            
            elif "温度" in header or "temp" in header:
                record["temperature"] = float(cell) if cell else None
            
            elif "风速" in header or "wind" in header:
                record["wind_speed"] = float(cell) if cell else None
            
            elif "云量" in header or "cloud" in header:
                cloud = float(cell) if cell else 0
                record["cloud_cover"] = cloud
                # 根据云量判断天气类型
                if cloud <= 30:
                    record["weather_type"] = "晴"
                elif cloud >= 70:
                    record["weather_type"] = "阴"
                else:
                    record["weather_type"] = "多云"
            
            elif "天气" in header or "weather" in header:
                record["weather_type"] = cell if cell else "unknown"
            
            elif "发电" in header or "generation" in header:
                record["generation_kwh"] = float(cell) if cell else 0.0
            
            elif "节假日" in header or "holiday" in header:
                record["is_holiday"] = cell.lower() in ("是", "yes", "true", "1")
            
            elif "预测" in header or "predict" in header:
                record["predicted_price"] = float(cell) if cell else None
        
        # 只添加有效记录
        if record.get("record_time"):
            records.append(record)
    
    return records


def validate_csv_structure(file_content: bytes) -> tuple[bool, str]:
    """
    验证CSV文件结构是否符合要求。
    
    Args:
        file_content: CSV文件的字节内容
    
    Returns:
        (是否有效, 错误信息)
    """
    try:
        # 尝试不同编码
        text_content = None
        for enc in ['utf-8', 'gbk', 'utf-8-sig', 'latin1']:
            try:
                text_content = file_content.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        
        if text_content is None:
            return False, "无法解析文件编码"
        
        reader = csv.reader(StringIO(text_content))
        headers = next(reader)
        headers = [h.strip().lower() for h in headers]
        
        # 检查是否有数据
        first_row = next(reader, None)
        if first_row is None:
            return False, "CSV文件至少需要包含表头和一行数据"
        
        # 检查必要列
        required_fields = ["时间", "电价"]
        found_fields = []
        
        for header in headers:
            if "时间" in header or "time" in header or "date" in header:
                found_fields.append("时间")
            elif "电价" in header or "price" in header:
                found_fields.append("电价")
        
        missing = set(required_fields) - set(found_fields)
        if missing:
            return False, f"缺少必要的列: {', '.join(missing)}"
        
        return True, ""
    
    except Exception as e:
        return False, f"解析CSV文件失败: {str(e)}"
