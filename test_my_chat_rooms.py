import requests
import json

BASE_URL = "http://localhost:8001/api"

def login(username, password):
    """登录获取token"""
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"登录用户 {username} 响应: {response.status_code}")
    if response.status_code == 200:
        return response.json()["data"]["access_token"]
    else:
        print(f"登录失败: {response.text}")
        return None

def get_my_chat_rooms(token):
    """获取我的群聊列表"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/chat-rooms/my-rooms", headers=headers)
    print(f"获取我的群聊列表响应: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取失败: {response.text}")
        return None

def get_pending_approvals(token):
    """获取待审批的入群申请"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/chat-rooms/join-requests/pending", headers=headers)
    print(f"获取待审批列表响应: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取失败: {response.text}")
        return None

def main():
    """主测试函数"""
    print("=== 开始测试获取我的群聊列表 ===")
    
    # 1. 登录用户
    token = login("user2", "password123")
    
    if not token:
        print("用户登录失败，测试终止")
        return
    
    # 2. 获取我的群聊列表
    print("\n--- 测试获取我的群聊列表 ---")
    rooms_response = get_my_chat_rooms(token)
    
    if rooms_response:
        data = rooms_response["data"]
        created = data.get("created", [])
        joined = data.get("joined", [])
        
        print(f"我创建的群聊数量: {len(created)}")
        for room in created:
            print(f"  - {room['name']} (ID: {room['room_id']}, 成员: {room['member_count']})")
        
        print(f"我加入的群聊数量: {len(joined)}")
        for room in joined:
            print(f"  - {room['name']} (ID: {room['room_id']}, 成员: {room['member_count']})")
    
    # 3. 获取待审批列表
    print("\n--- 测试获取待审批列表 ---")
    approvals_response = get_pending_approvals(token)
    
    if approvals_response:
        data = approvals_response["data"]
        approvals = data.get("approvals", [])
        print(f"待审批申请数量: {len(approvals)}")
        for approval in approvals:
            print(f"  - 用户 {approval['user_name']} 申请加入 {approval['room_name']}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
