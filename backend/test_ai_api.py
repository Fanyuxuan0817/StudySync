import requests
import json
from datetime import date, timedelta

# 添加认证令牌
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzcwODc4MzkwfQ.zbAlVbittNXaeNlPbPJxTfdbMLsETobe8W_QQ2OFHJY"
}

# 测试 /ai/learning_coach 接口的流式返回
print("=== 测试 /ai/learning_coach 接口的流式返回 ===")
url = "http://localhost:8001/api/ai/learning_coach"

payload = {
    "learning_goal": "考研数学",
    "weekly_total_hours": 10,
    "average_daily_hours": 1.5,
    "target_daily_hours": 2,
    "consecutive_checkin_days": 5,
    "missed_checkin_days": 2
}

print("请求数据:", json.dumps(payload, ensure_ascii=False))
print("\n响应内容:")
print("=" * 50)

response = requests.post(url, json=payload, headers=headers, stream=True)

if response.status_code == 200:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode('utf-8'), end='')
    print("\n" + "=" * 50)
    print("测试完成！")
else:
    print(f"错误: {response.status_code}")
    print(response.text)

print("\n" + "=" * 80 + "\n")

# 测试 /ai/checkin_analysis 接口
print("=== 测试 /ai/checkin_analysis 接口 ===")
url = "http://localhost:8001/api/ai/checkin_analysis"

# 设置日期范围（最近30天）
today = date.today()
start_date = today - timedelta(days=30)
end_date = today

payload = {
    "start_date": start_date.isoformat(),
    "end_date": end_date.isoformat()
}

print("请求数据:", json.dumps(payload, ensure_ascii=False))
print("\n响应内容:")
print("=" * 50)

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    print("\n" + "=" * 50)
    print("测试完成！")
else:
    print(f"错误: {response.status_code}")
    print(response.text)
