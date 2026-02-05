import requests
import json

# 测试群聊创建时自动添加其他用户的bug

BASE_URL = "http://localhost:8001/api"

# 首先创建两个测试用户
def create_user(username, password):
    user_data = {
        "username": username,
        "email": f"{username}@example.com",
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"创建用户 {username} 响应: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"创建用户失败: {response.text}")
        return None

# 登录获取token
def login(username, password):
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

# 创建群聊
def create_chat_room(token, name):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    chat_data = {
        "name": name,
        "description": "测试群聊",
        "is_public": True,
        "max_members": 100
    }
    
    response = requests.post(f"{BASE_URL}/chat-rooms", json=chat_data, headers=headers)
    print(f"创建群聊 {name} 响应: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"创建群聊失败: {response.text}")
        return None

# 获取群聊成员
def get_chat_room_members(token, chat_room_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/chat-rooms/{chat_room_id}/members", headers=headers)
    print(f"获取群聊成员响应: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取群聊成员失败: {response.text}")
        return None

# 主测试函数
def main():
    print("=== 开始测试群聊创建bug ===")
    
    # 1. 创建两个测试用户
    user1 = create_user("user1", "password123")
    user2 = create_user("user2", "password123")
    
    if not user1 or not user2:
        print("创建测试用户失败，测试终止")
        return
    
    # 2. 登录两个用户获取token
    token1 = login("user1", "password123")
    token2 = login("user2", "password123")
    
    if not token1 or not token2:
        print("登录失败，测试终止")
        return
    
    # 3. 用户1创建群聊
    chat_response = create_chat_room(token1, "测试群聊1")
    
    if not chat_response:
        print("创建群聊失败，测试终止")
        return
    
    chat_room_id = chat_response["data"]["chat_room_id"]
    print(f"创建的群聊ID: {chat_room_id}")
    
    # 4. 检查群聊成员
    members_response = get_chat_room_members(token1, chat_room_id)
    
    if members_response:
        members = members_response["data"]["members"]
        print(f"群聊成员数量: {len(members)}")
        print("群聊成员:")
        for member in members:
            print(f"  - {member['username']} (角色: {member['role']})")
        
        # 5. 检查是否有非预期的成员
        usernames = [member['username'] for member in members]
        if "user2" in usernames:
            print("=== BUG 确认: 用户2被自动加入了用户1创建的群聊 ===")
        else:
            print("=== 群聊创建正常: 只有创建者用户1在群聊中 ===")
    
    print("=== 测试完成 ===")

if __name__ == "__main__":
    main()
