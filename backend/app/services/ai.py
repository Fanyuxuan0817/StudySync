from openai import OpenAI

# 👉 关键：把 timeout 调大
deepseek_client = OpenAI(
    api_key="sk-6c4b398b52ad47589ee338a676b43c99",
    base_url="https://api.deepseek.com",
    timeout=30.0   # ⬅️ 从默认 10s 改成 30s
)
