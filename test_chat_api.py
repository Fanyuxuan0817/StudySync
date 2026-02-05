import requests
import json

# 测试群聊API的Python脚本

BASE_URL = "http://localhost:8001/api"

# 首先登录获取token
def login():
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["data"]["access_token"]
            print(f"登录成功，获取token: {token[:20]}...")
            return token
        else:
            print(f"登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"登录请求失败: {e}")
        return None

# 测试创建群聊
def create_chat_room(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    chat_data = {
        "name": "测试群聊",
        "description": "这是一个测试群聊",
        "is_public": True,
        "max_members": 100
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat-rooms", json=chat_data, headers=headers)
        print(f"创建群聊响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"创建成功！群聊ID: {result['data']['chat_id']}")
            return result['data']['chat_room_id']
        else:
            print(f"创建失败: {response.text}")
            return None
    except Exception as e:
        print(f"创建群聊请求失败: {e}")
        return None

# 测试搜索群聊
def search_chat_rooms(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/chat-rooms/search", headers=headers)
        print(f"搜索群聊响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"找到 {len(result['data']['chat_rooms'])} 个群聊")
            for room in result['data']['chat_rooms']:
                print(f"  - {room['name']} (ID: {room['chat_id']})")
        else:
            print(f"搜索失败: {response.text}")
    except Exception as e:
        print(f"搜索群聊请求失败: {e}")

# 测试通过ID搜索群聊
def search_by_chat_id(token, chat_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/chat-rooms/search-by-id?chat_id={chat_id}", headers=headers)
        print(f"通过ID搜索群聊响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"找到群聊: {result['data']['name']} (ID: {result['data']['chat_id']})")
        else:
            print(f"通过ID搜索失败: {response.text}")
    except Exception as e:
        print(f"通过ID搜索群聊请求失败: {e}")

# 测试获取群聊成员
def get_chat_room_members(token, chat_room_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/chat-rooms/{chat_room_id}/members", headers=headers)
        print(f"获取群聊成员响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"群聊有 {result['data']['total_members']} 个成员")
            for member in result['data']['members']:
                print(f"  - {member['username']} (角色: {member['role']})")
        else:
            print(f"获取群聊成员失败: {response.text}")
    except Exception as e:
        print(f"获取群聊成员请求失败: {e}")

# 测试发送加入申请
def create_join_request(token, chat_room_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    request_data = {
        "message": "我想加入这个群聊一起学习！"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat-rooms/{chat_room_id}/join-request", json=request_data, headers=headers)
        print(f"发送加入申请响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"申请发送成功！申请ID: {result['data']['request_id']}")
        else:
            print(f"发送申请失败: {response.text}")
    except Exception as e:
        print(f"发送加入申请请求失败: {e}")

# 测试获取加入申请
def get_join_requests(token, chat_room_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/chat-rooms/{chat_room_id}/join-requests", headers=headers)
        print(f"获取加入申请响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"有 {len(result['data'])} 个加入申请")
            for request in result['data']:
                print(f"  - {request['username']}: {request['status']}")
        else:
            print(f"获取加入申请失败: {response.text}")
    except Exception as e:
        print(f"获取加入申请请求失败: {e}")

# 主测试函数
def main():
    print("=== 开始测试群聊API ===")
    
    # 1. 登录获取token
    token = login()
    if not token:
        print("无法获取token，测试终止")
        return
    
    print("\n=== 测试创建群聊 ===")
    chat_room_id = create_chat_room(token)
    
    if chat_room_id:
        print(f"\n=== 测试搜索群聊 ===")
        search_chat_rooms(token)
        
        print(f"\n=== 测试通过ID搜索群聊 ===")
        # 这里需要获取实际的chat_id
        # search_by_chat_id(token, "ABC123")
        
        print(f"\n=== 测试获取群聊成员 ===")
        get_chat_room_members(token, chat_room_id)
        
        print(f"\n=== 测试发送加入申请 ===")
        create_join_request(token, chat_room_id)
        
        print(f"\n=== 测试获取加入申请 ===")
        get_join_requests(token, chat_room_id)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()