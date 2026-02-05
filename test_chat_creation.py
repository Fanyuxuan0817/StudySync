import requests
import json
import time

# 测试群聊创建时自动添加其他用户的bug

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

def create_chat_room(token, name):
    """创建群聊"""
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

def get_chat_room_members(token, chat_room_id):
    """获取群聊成员"""
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

def get_user_info(token):
    """获取用户信息"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"获取用户信息响应: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取用户信息失败: {response.text}")
        return None

def create_user(username, password):
    """创建用户"""
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

def main():
    """主测试函数"""
    print("=== 开始测试群聊创建bug ===")
    
    # 1. 使用用户2登录
    username = "user2"
    
    # 2. 登录用户
    token = login(username, "password123")
    
    if not token:
        print("用户登录失败，测试终止")
        return
    
    # 3. 获取用户信息，确认用户存在
    user_info = get_user_info(token)
    
    if not user_info:
        print("获取用户信息失败，测试终止")
        return
    
    print(f"当前用户: {user_info['data']['username']}")
    
    # 4. 创建群聊
    chat_response = create_chat_room(token, f"测试群聊_{int(time.time())}")
    
    if not chat_response:
        print("创建群聊失败，测试终止")
        return
    
    chat_room_id = chat_response["data"]["chat_room_id"]
    print(f"创建的群聊ID: {chat_room_id}")
    
    # 5. 检查群聊成员
    members_response = get_chat_room_members(token, chat_room_id)
    
    if members_response:
        members = members_response["data"]["members"]
        print(f"群聊成员数量: {len(members)}")
        print("群聊成员:")
        for member in members:
            print(f"  - {member['username']} (角色: {member['role']}, 用户ID: {member['user_id']})")
        
        # 6. 检查是否只有创建者在群聊中
        usernames = [member['username'] for member in members]
        if len(members) == 1 and username in usernames:
            print(f"=== 群聊创建正常: 只有创建者用户 {username} 在群聊中 ===")
            print("=== 无需修复，群聊创建逻辑正确 ===")
        else:
            print(f"=== BUG 确认: 群聊中有非预期的成员 ===")
            print(f"=== 预期: 只有创建者 {username} ===")
            print(f"=== 实际: {len(members)} 个成员 ===")
            print("=== 需要修复群聊创建逻辑，确保只有创建者被添加 ===")
    
    print("=== 测试完成 ===")

if __name__ == "__main__":
    main()
