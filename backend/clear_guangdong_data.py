"""清除广东电价数据"""
from app.db.session import get_engine
from sqlalchemy.orm import Session
from sqlalchemy import text

engine = get_engine()
with Session(engine) as session:
    # 查找广东电价数据集
    result = session.execute(text("SELECT id, name FROM dataset WHERE name LIKE '%广东%'"))
    datasets = result.fetchall()
    print('找到的数据集:')
    for ds in datasets:
        print(f'  ID: {ds[0]}, Name: {ds[1]}')
    
    # 删除相关数据
    for ds in datasets:
        ds_id = ds[0]
        # 删除dataset_record
        session.execute(text(f'DELETE FROM dataset_record WHERE dataset_id = {ds_id}'))
        # 删除prediction_detail (如果有关联的plan)
        session.execute(text(f'DELETE FROM prediction_detail WHERE plan_id IN (SELECT id FROM plan WHERE dataset_id = {ds_id})'))
        # 删除plan
        session.execute(text(f'DELETE FROM plan WHERE dataset_id = {ds_id}'))
        # 删除dataset_file
        session.execute(text(f'DELETE FROM dataset_file WHERE dataset_id = {ds_id}'))
        # 删除dataset
        session.execute(text(f'DELETE FROM dataset WHERE id = {ds_id}'))
        print(f'已删除数据集 {ds[1]} (ID: {ds_id}) 及其所有关联数据')
    
    session.commit()
    print('清除完成!')
