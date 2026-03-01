"""导入广东电价预测结果到数据库"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.session import get_engine, Base
from app.models.admin import AdminUser
from app.models.dataset import Dataset
from app.models.plan import Plan
from app.models.prediction_detail import PredictionDetail


def import_prediction_results():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    
    with Session(engine) as db:
        # 获取 admin 用户
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin:
            print("错误: 找不到 admin 用户")
            return
        
        # 获取广东电价数据集
        dataset = db.query(Dataset).filter(Dataset.name == "广东电价数据").first()
        if not dataset:
            print("错误: 找不到广东电价数据集，请先运行 import_guangdong_data.py")
            return
        
        # 检查是否已存在预测方案
        plan = db.query(Plan).filter(Plan.name == "广东电价预测方案").first()
        if plan:
            print(f"预测方案已存在 (id={plan.id})，正在删除旧预测数据...")
            db.query(PredictionDetail).filter(PredictionDetail.plan_id == plan.id).delete()
            db.commit()
        else:
            # 创建预测方案
            plan = Plan(
                name="广东电价预测方案",
                plan_type="电价预测",
                dataset_id=dataset.id,
                status="已完成",
                description="基于广东电价数据的TCN模型预测结果",
                created_by=admin.id,
            )
            db.add(plan)
            db.flush()
            print(f"创建预测方案 '广东电价预测方案' (id={plan.id})")
        
        # 读取 CSV 数据
        csv_path = r"..\广东电价预测结果.csv"
        print(f"正在读取 {csv_path}...")
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"共 {len(df)} 条预测记录")
        
        # 批量插入
        batch_size = 1000
        records = []
        
        for i, row in df.iterrows():
            # 解析时间
            time_str = row['date']
            try:
                record_time = datetime.strptime(time_str, "%Y/%m/%d %H:%M")
            except:
                record_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            
            record = PredictionDetail(
                plan_id=plan.id,
                record_time=record_time,
                actual_price=float(row['y_test_true']),
                predicted_price=float(row['y_test_pred']),
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
        
        print(f"导入完成！共导入 {len(df)} 条预测结果记录")


if __name__ == "__main__":
    import_prediction_results()
