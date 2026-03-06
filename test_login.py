#!/usr/bin/env python3
"""测试登录功能"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """测试登录接口"""
    print("测试登录功能...")
    
    # 测试用户凭据
    test_users = [
        {"username": "admin", "password": "admin123"},
        {"username": "aceberg", "password": "password"},
        {"username": "tong", "password": "password"},
    ]
    
    for user in test_users:
        print(f"\n尝试登录用户: {user['username']}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/login",
                data={
                    "username": user["username"],
                    "password": user["password"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 登录成功!")
                print(f"   Token: {result['access_token'][:50]}...")
                if 'userinfo' in result:
                    print(f"   用户信息: {result['userinfo']}")
            else:
                print(f"❌ 登录失败: {response.status_code}")
                print(f"   错误: {response.json()}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_login()
