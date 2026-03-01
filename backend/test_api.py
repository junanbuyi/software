import urllib.request
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2OTEwODMwOH0.YhuZ05ko18HZCWjtAywh7KVK86e6ITcCGMeqJbBZVR0"

# 测试获取数据集
print("1. 测试获取数据集列表...")
try:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/datasets?page=1&size=1",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"  Status: {resp.status}")
        print(f"  数据集: {data}")
except Exception as e:
    print(f"  Error: {e}")

# 测试图表API
print("\n2. 测试图表预测API...")
try:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/chart/prediction?dataset_id=3&start_time=2024-07-19T00:00:00&end_time=2024-07-25T23:59:59",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"  Status: {resp.status}")
        print(f"  Total items: {data.get('total', 0)}")
        if data.get('items'):
            print(f"  First item: {data['items'][0]}")
except Exception as e:
    print(f"  Error: {e}")
