from app.db.session import get_engine
from sqlalchemy.orm import Session
from sqlalchemy import text

engine = get_engine()
with Session(engine) as session:
    # 检查数据集
    result = session.execute(text("SELECT id, name FROM dataset"))
    datasets = result.fetchall()
    print("数据集列表:")
    for ds in datasets:
        print(f"  ID: {ds[0]}, Name: {ds[1]}")
    
    # 检查指定日期范围的数据
    result = session.execute(text(
        "SELECT COUNT(*) FROM dataset_record WHERE dataset_id = 3 AND record_time >= '2024-07-19' AND record_time <= '2024-07-25 23:59:59'"
    ))
    count = result.fetchone()[0]
    print(f"\n2024-07-19到2024-07-25的记录数: {count}")
    
    # 检查样例数据
    result = session.execute(text(
        "SELECT record_time, price_kwh FROM dataset_record WHERE dataset_id = 3 AND record_time >= '2024-07-25' LIMIT 5"
    ))
    rows = result.fetchall()
    print("\n样例数据:")
    for r in rows:
        print(f"  {r[0]} - {r[1]}")
