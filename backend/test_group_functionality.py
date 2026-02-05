#!/usr/bin/env python3
"""
群组模块功能验证脚本
用于验证群组模块的核心功能是否正常工作
"""

import urllib.request as requests
import json
from datetime import date

def test_group_apis():
    """测试群组API接口"""
    
    base_url = "http://localhost:8001/api"
    headers = {
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json"
    }
    
    print("=== 群组模块功能验证 ===\n")
    
    # 1. 测试创建群组
    print("1. 测试创建群组...")
    group_data = {
        "name": "测试学习群组",
        "description": "这是一个测试群组",
        "daily_checkin_required": True
    }
    
    try:
        response = requests.post(f"{base_url}/groups", json=group_data, headers=headers)
        if response.status_code == 200:
            group_info = response.json()["data"]
            group_id = group_info["group_id"]
            print(f"✅ 创建群组成功: {group_info['name']} (ID: {group_id})")
        else:
            print(f"❌ 创建群组失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建群组异常: {e}")
        return False
    
    # 2. 测试获取群组列表
    print("\n2. 测试获取群组列表...")
    try:
        response = requests.get(f"{base_url}/groups", headers=headers)
        if response.status_code == 200:
            groups_data = response.json()["data"]
            print(f"✅ 获取群组列表成功: 创建{len(groups_data.get('created', []))}个, 加入{len(groups_data.get('joined', []))}个")
        else:
            print(f"❌ 获取群组列表失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 获取群组列表异常: {e}")
    
    # 3. 测试获取群组成员
    print("\n3. 测试获取群组成员...")
    try:
        response = requests.get(f"{base_url}/groups/{group_id}/members", headers=headers)
        if response.status_code == 200:
            members_data = response.json()["data"]
            print(f"✅ 获取群组成员成功: {members_data['total_members']} 名成员")
            print(f"   群组名称: {members_data['name']}")
            print(f"   是否要求每日打卡: {members_data.get('daily_checkin_required', '未知')}")
        else:
            print(f"❌ 获取群组成员失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 获取群组成员异常: {e}")
    
    # 4. 测试获取群组统计
    print("\n4. 测试获取群组统计...")
    try:
        response = requests.get(f"{base_url}/groups/{group_id}/stats", headers=headers)
        if response.status_code == 200:
            stats_data = response.json()["data"]
            print(f"✅ 获取群组统计成功:")
            print(f"   总成员数: {stats_data['total_members']}")
            print(f"   今日打卡人数: {stats_data['today_checked_in_count']}")
            print(f"   打卡率: {stats_data['checkin_rate']}%")
            print(f"   个人统计数量: {len(stats_data.get('personal_stats', []))}")
            if 'my_stats' in stats_data and stats_data['my_stats']:
                my_stats = stats_data['my_stats']
                print(f"   我的统计: 本周打卡{my_stats.get('week_checkin_days', 0)}天, 平均{my_stats.get('avg_hours_per_day', 0)}小时/天")
        else:
            print(f"❌ 获取群组统计失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 获取群组统计异常: {e}")
    
    # 5. 测试群主转让功能
    print("\n5. 测试群主转让功能...")
    transfer_data = {
        "new_owner_id": 2  # 假设用户ID为2
    }
    try:
        response = requests.post(f"{base_url}/groups/{group_id}/transfer", json=transfer_data, headers=headers)
        if response.status_code == 200:
            transfer_info = response.json()["data"]
            print(f"✅ 群主转让成功: {transfer_info['previous_owner_id']} -> {transfer_info['new_owner_id']}")
        else:
            print(f"⚠️  群主转让失败（可能是测试用户不存在）: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 群主转让异常: {e}")
    
    # 6. 测试群组解散功能
    print("\n6. 测试群组解散功能...")
    try:
        response = requests.delete(f"{base_url}/groups/{group_id}", headers=headers)
        if response.status_code == 200:
            print(f"✅ 群组解散成功")
        else:
            print(f"⚠️  群组解散失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 群组解散异常: {e}")
    
    print("\n=== 群组模块功能验证完成 ===")
    return True

def test_error_handling():
    """测试错误处理"""
    print("\n=== 错误处理测试 ===\n")
    
    base_url = "http://localhost:8001/api"
    headers = {
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json"
    }
    
    # 测试创建空名称群组
    print("1. 测试创建空名称群组...")
    group_data = {
        "name": "",
        "description": "空名称测试",
        "daily_checkin_required": True
    }
    
    try:
        response = requests.post(f"{base_url}/groups", json=group_data, headers=headers)
        if response.status_code == 400:
            error_data = response.json()
            if "群组名称不能为空" in error_data.get("detail", ""):
                print("✅ 空名称验证成功")
            else:
                print(f"⚠️  空名称验证响应: {error_data}")
        else:
            print(f"⚠️  空名称测试返回: {response.status_code}")
    except Exception as e:
        print(f"❌ 空名称测试异常: {e}")
    
    # 测试加入不存在的群组
    print("\n2. 测试加入不存在的群组...")
    try:
        response = requests.post(f"{base_url}/groups/999/join", headers=headers)
        if response.status_code == 404:
            error_data = response.json()
            if "群组不存在" in error_data.get("detail", ""):
                print("✅ 不存在的群组验证成功")
            else:
                print(f"⚠️  不存在的群组验证响应: {error_data}")
        else:
            print(f"⚠️  不存在的群组测试返回: {response.status_code}")
    except Exception as e:
        print(f"❌ 不存在的群组测试异常: {e}")
    
    print("\n=== 错误处理测试完成 ===")

if __name__ == "__main__":
    print("开始验证群组模块功能...")
    
    # 首先检查服务是否运行
    try:
        response = requests.get("http://localhost:8001/api/docs")
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            test_group_apis()
            test_error_handling()
        else:
            print(f"❌ 后端服务响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        print("请确保后端服务正在运行: cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001")