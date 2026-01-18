"""
测试脚本 - 验证API功能
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("开始测试API...")
    
    # 测试根路径
    response = requests.get(f"{BASE_URL}/")
    print(f"根路径响应: {response.status_code} - {response.json()}")
    
    # 测试用户相关API
    print("\n测试用户相关API...")
    
    # 获取用户列表（如果没有认证，这可能会失败，这是正常的）
    try:
        response = requests.get(f"{BASE_URL}/api/v1/users/")
        print(f"获取用户列表: {response.status_code}")
    except Exception as e:
        print(f"获取用户列表失败: {e}")
    
    # 测试产品相关API
    print("\n测试产品相关API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/products/")
        print(f"获取产品列表: {response.status_code}")
    except Exception as e:
        print(f"获取产品列表失败: {e}")
    
    print("\nAPI测试完成！")

if __name__ == "__main__":
    test_api()