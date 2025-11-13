#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三个核心场景测试脚本
"""

import requests
import json
import time

API_BASE_URL = 'http://localhost:9000/api'

def test_api_health():
    """测试API健康状态"""
    try:
        response = requests.get(f'{API_BASE_URL}/health')
        print(f"✅ API健康检查: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API健康检查失败: {e}")
        return False

def test_scenario_1_query():
    """场景一：查询员工账号"""
    print("\n🔍 场景一：查询员工账号测试")
    
    # 测试AI对话查询
    test_messages = [
        "查询张三的人事账号",
        "搜索李四的信息",
        "找王五的资料"
    ]
    
    for message in test_messages:
        try:
            response = requests.post(f'{API_BASE_URL}/ai/chat', 
                                   json={'message': message})
            result = response.json()
            print(f"用户: {message}")
            if result['success']:
                print(f"AI: {result['data']['response']}")
            else:
                print(f"❌ 错误: {result['message']}")
            print("-" * 50)
        except Exception as e:
            print(f"❌ 请求失败: {e}")

def test_scenario_2_create():
    """场景二：新增员工账号"""
    print("\n➕ 场景二：新增员工账号测试")
    
    test_messages = [
        "新增一个员工王小敏，部门是市场部",
        "添加员工赵六到技术部",
        "创建员工孙七，部门财务部"
    ]
    
    for message in test_messages:
        try:
            response = requests.post(f'{API_BASE_URL}/ai/chat', 
                                   json={'message': message})
            result = response.json()
            print(f"用户: {message}")
            if result['success']:
                print(f"AI: {result['data']['response']}")
            else:
                print(f"❌ 错误: {result['message']}")
            print("-" * 50)
        except Exception as e:
            print(f"❌ 请求失败: {e}")

def test_scenario_3_update():
    """场景三：修改员工部门"""
    print("\n✏️ 场景三：修改员工部门测试")
    
    test_messages = [
        "把李四的部门改为行政部",
        "修改张三的部门为人事部",
        "将王五调到市场部"
    ]
    
    for message in test_messages:
        try:
            response = requests.post(f'{API_BASE_URL}/ai/chat', 
                                   json={'message': message})
            result = response.json()
            print(f"用户: {message}")
            if result['success']:
                print(f"AI: {result['data']['response']}")
            else:
                print(f"❌ 错误: {result['message']}")
            print("-" * 50)
        except Exception as e:
            print(f"❌ 请求失败: {e}")

def test_api_endpoints():
    """测试REST API端点"""
    print("\n🔧 REST API端点测试")
    
    # 测试获取员工列表
    try:
        response = requests.get(f'{API_BASE_URL}/employees')
        result = response.json()
        if result['success']:
            print(f"✅ 员工列表: 共{len(result['data']['employees'])}名员工")
        else:
            print(f"❌ 获取员工列表失败: {result['message']}")
    except Exception as e:
        print(f"❌ 员工列表请求失败: {e}")
    
    # 测试获取统计信息
    try:
        response = requests.get(f'{API_BASE_URL}/stats')
        result = response.json()
        if result['success']:
            stats = result['data']['stats']
            print(f"✅ 统计信息: 总员工{stats['total_employees']}人，在职{stats['active_employees']}人")
        else:
            print(f"❌ 获取统计信息失败: {result['message']}")
    except Exception as e:
        print(f"❌ 统计信息请求失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始HR系统核心场景测试")
    print("=" * 60)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 健康检查
    if not test_api_health():
        print("❌ API服务不可用，测试终止")
        return
    
    # 测试REST API
    test_api_endpoints()
    
    # 测试三个核心场景
    test_scenario_1_query()
    test_scenario_2_create()
    test_scenario_3_update()
    
    print("\n🎉 测试完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()