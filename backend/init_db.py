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
        admin_user = user_service.get_user_by_username(db, "aceberg")
        if admin_user:
            print("管理员用户已存在，跳过创建")
            print(f"用户名: admin")
            print(f"用户ID: {admin_user.id}")
        else:
            print("创建默认管理员用户...")
            # 创建默认管理员用户
            # admin_user = user_service.create_user(
            #     db=db,
            #     username="admin",
            #     email="admin@example.com",
            #     password="admin", 
            #     role="admin"  # 添加这个参数
            # )
            admin_user = user_service.create_user(
                db=db,
                username="aceberg",
                email="aceberg@example.com",
                password="aceberg", 
                role="sales"  # 添加这个参数
            )
            print(f"默认管理员用户已创建:")
            print(f"  用户名: {admin_user.username}")
            print(f"  邮箱: {admin_user.email}")
            print(f"  用户ID: {admin_user.id}")
            print(f"  初始密码: admin")
    
    print("数据库初始化完成!")


def init_default_goods():
    """初始化默认商品数据"""
    print("正在初始化商品表...")
    init_db()  # 确保数据库和表已经创建
    
    from backend.models.database import Goods
    
    with get_db() as db:
        # 检查是否已经有商品数据
        goods_count = Goods.select().count()
        if goods_count > 0:
            print(f"商品表中已有 {goods_count} 条记录，跳过初始化")
            return
        
        print("开始插入默认商品数据...")
        
        # 创建一些默认商品数据
        default_goods = [
            Goods.create(
                goods_id="G001",
                goods_name="测试商品1",
                store_id="S001",
                store_name="旗舰店",
                payment_amount=100.00,
                sales_amount=120.00,
                refund_amount=40.00,
                sales_cost=80.00,
                gross_profit_1_occurred=(120.00 - 80.00),
                gross_profit_1_rate=((120.00 - 80.00) / 120.00) * 100,
                advertising_expenses=10.00,
                advertising_ratio=(10.00 / 120.00) * 100,
                gross_profit_3=(120.00 - 80.00 - 10.00),
                gross_profit_3_rate=((120.00 - 80.00 - 10.00) / 120.00) * 100,
                gross_profit_4=(120.00 - 80.00 - 10.00),
                gross_profit_4_rate=((120.00 - 80.00 - 10.00) / 120.00) * 100,
                net_profit=(120.00 - 80.00 - 10.00),
                net_profit_rate=((120.00 - 80.00 - 10.00) / 120.00) * 100,
                creator="system",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Goods.create(
                goods_id="G002",
                goods_name="测试商品2",
                store_id="S002",
                store_name="分店A",
                payment_amount=200.00,
                sales_amount=250.00,
                refund_amount=50.00,
                sales_cost=150.00,
                gross_profit_1_occurred=(250.00 - 150.00),
                gross_profit_1_rate=((250.00 - 150.00) / 250.00) * 100,
                advertising_expenses=15.00,
                advertising_ratio=(15.00 / 250.00) * 100,
                gross_profit_3=(250.00 - 150.00 - 15.00),
                gross_profit_3_rate=((250.00 - 150.00 - 15.00) / 250.00) * 100,
                gross_profit_4=(250.00 - 150.00 - 15.00),
                gross_profit_4_rate=((250.00 - 150.00 - 15.00) / 250.00) * 100,
                net_profit=(250.00 - 150.00 - 15.00),
                net_profit_rate=((250.00 - 150.00 - 15.00) / 250.00) * 100,
                creator="system",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Goods.create(
                goods_id="G003",
                goods_name="测试商品3",
                store_id="S003",
                store_name="分店B",
                payment_amount=150.00,
                sales_amount=180.00,
                refund_amount=30.00,
                sales_cost=100.00,
                gross_profit_1_occurred=(180.00 - 100.00),
                gross_profit_1_rate=((180.00 - 100.00) / 180.00) * 100,
                advertising_expenses=8.00,
                advertising_ratio=(8.00 / 180.00) * 100,
                gross_profit_3=(180.00 - 100.00 - 8.00),
                gross_profit_3_rate=((180.00 - 100.00 - 8.00) / 180.00) * 100,
                gross_profit_4=(180.00 - 100.00 - 8.00),
                gross_profit_4_rate=((180.00 - 100.00 - 8.00) / 180.00) * 100,
                net_profit=(180.00 - 100.00 - 8.00),
                net_profit_rate=((180.00 - 100.00 - 8.00) / 180.00) * 100,
                creator="system",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        print(f"成功插入 {len(default_goods)} 条商品记录")
        print("商品表初始化完成!")


def init_stores_table():
    """初始化店铺表"""
    print("正在初始化店铺表...")
    init_db()  # 确保数据库和表已经创建
    
    
    with get_db() as db:
        print("店铺表已准备就绪!")
        
if __name__ == "__main__":
    # init_default_user()
    init_default_goods()
    init_stores_table()