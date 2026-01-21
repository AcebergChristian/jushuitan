#!/usr/bin/env python
"""
初始化数据库并创建默认用户
"""
import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, get_db
from backend.services import user_service
from backend.utils.auth import get_password_hash

def init_default_user():
    """初始化默认管理员用户"""
    print("正在初始化数据库...")
    init_db()
    
    print("检查是否已存在管理员用户...")
    
    with get_db() as db:
        # 检查是否已存在admin用户
        admin_user = user_service.get_user_by_username(db, "admin")
        if admin_user:
            print("管理员用户已存在，跳过创建")
            print(f"用户名: admin")
            print(f"用户ID: {admin_user.id}")
        else:
            print("创建默认管理员用户...")
            # 创建默认管理员用户
            admin_user = user_service.create_user(
                db=db,
                username="admin",
                email="admin@example.com",
                password="admin", 
                role="admin"  # 添加这个参数
            )
            print(f"默认管理员用户已创建:")
            print(f"  用户名: {admin_user.username}")
            print(f"  邮箱: {admin_user.email}")
            print(f"  用户ID: {admin_user.id}")
            print(f"  初始密码: admin")
    
    print("数据库初始化完成！")

if __name__ == "__main__":
    init_default_user()