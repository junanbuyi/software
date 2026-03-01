"""导入广东电价数据到数据库"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.session import get_engine, Base
from app.models.admin import AdminUser
from app.models.dataset import Dataset
from app.models.dataset_record import DatasetRecord


def import_guangdong_data():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    
    with Session(engine) as db:
        # 检查是否已存在广东电价数据集
        existing = db.query(Dataset).filter(Dataset.name == "广东电价数据").first()
        if existing:
            print(f"数据集 '广东电价数据' 已存在 (id={existing.id})，正在删除旧记录...")
            db.query(DatasetRecord).filter(DatasetRecord.dataset_id == existing.id).delete()
            db.commit()
            dataset = existing
        else:
            # 获取 admin 用户
            admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
            if not admin:
                print("错误: 找不到 admin 用户，请先启动后端服务初始化数据库")
                return
            
            # 创建新数据集
            dataset = Dataset(
                name="广东电价数据",
                description="广东电价数据 - 包含电价、负荷、温度、风速等信息",
                created_by=admin.id,
            )
            db.add(dataset)
            db.flush()
            print(f"创建数据集 '广东电价数据' (id={dataset.id})")
        
        # 读取 CSV 数据
        csv_path = r"../广东电价数据.csv"
        print(f"正在读取 {csv_path}...")
        df = pd.read_csv(csv_path, encoding='gbk')
        print(f"共 {len(df)} 条记录")
        
        # 批量插入
        batch_size = 1000
        records = []
        
        for i, row in df.iterrows():
            # 解析时间
            time_str = row['时间']
            try:
                record_time = datetime.strptime(time_str, "%Y/%m/%d %H:%M")
            except:
                record_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            
            # 根据云量判断天气类型
            cloud = float(row['云量(%)'])
            if cloud <= 30:
                weather_type = "晴"
            elif cloud >= 70:
                weather_type = "阴"
            else:
                weather_type = "多云"
            
            record = DatasetRecord(
                dataset_id=dataset.id,
                record_time=record_time,
                price_kwh=float(row['电价(元/kWh)']),
                generation_kwh=0.0,  # CSV 中没有发电量数据
                load_kw=float(row['负荷(kW)']),
                weather_type=weather_type,
                temperature=float(row['温度(℃)']),
                wind_speed=float(row['风速(m/s)']),
                cloud_cover=cloud,
                is_holiday=0,
            )
            records.append(record)
            
            # 批量提交
            if len(records) >= batch_size:
                db.add_all(records)
                db.commit()
                print(f"已导入 {i + 1} 条记录...")
                records = []
        
        # 提交剩余记录
        if records:
            db.add_all(records)
            db.commit()
        
        print(f"导入完成！共导入 {len(df)} 条广东电价数据记录")


if __name__ == "__main__":
    import_guangdong_data()
