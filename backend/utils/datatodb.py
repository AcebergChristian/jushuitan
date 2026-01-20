import sqlite3
from pathlib import Path
import os
from datetime import datetime
from typing import List

class DataToDB:
    def __init__(self, db_path: str = "jushuitan.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self.init_tables()
    
    def init_tables(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建商品数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goods_id TEXT,
                name TEXT,
                price REAL,
                stock INTEGER,
                order_number TEXT,
                online_order_number TEXT,
                shop_name TEXT,
                label TEXT,
                buyer_nickname TEXT,
                supplier TEXT,
                purchase_amount REAL,
                status TEXT,
                shipping_company TEXT,
                solution TEXT,
                distributor_push_time TEXT,
                customer_quantity INTEGER,
                customer_amount REAL,
                weight REAL,
                actual_weight REAL,
                buyer_message TEXT,
                seller_remark TEXT,
                offline_remark TEXT,
                placing_time TEXT,
                payment_time TEXT,
                shipping_time TEXT,
                distributor TEXT,
                shipping_warehouse TEXT,
                platform TEXT,
                data_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建拼多多商品数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pdd_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goods_id TEXT,
                name TEXT,
                price REAL,
                stock INTEGER,
                order_number TEXT,
                shop_name TEXT,
                buyer_nickname TEXT,
                supplier TEXT,
                status TEXT,
                shipping_company TEXT,
                customer_quantity INTEGER,
                customer_amount REAL,
                buyer_message TEXT,
                seller_remark TEXT,
                placing_time TEXT,
                payment_time TEXT,
                shipping_time TEXT,
                distributor TEXT,
                shipping_warehouse TEXT,
                platform TEXT,
                data_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_jushuitan_data(self, products_data: dict):
        """
        插入聚水潭数据到数据库
        :param products_data: 包含 'regular_products' 和 'return_products' 的字典
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        all_data = []
        
        # 处理常规商品数据
        if 'regular_products' in products_data and products_data['regular_products']:
            for product in products_data['regular_products']:
                data_tuple = (
                    getattr(product, 'goods_id', ''),
                    getattr(product, 'name', ''),
                    getattr(product, 'price', 0),
                    getattr(product, 'stock', 0),
                    getattr(product, 'order_number', ''),
                    getattr(product, 'online_order_number', ''),
                    getattr(product, 'shop_name', ''),
                    getattr(product, 'label', ''),
                    getattr(product, 'buyer_nickname', ''),
                    getattr(product, 'supplier', ''),
                    getattr(product, 'purchase_amount', 0),
                    getattr(product, 'status', ''),
                    getattr(product, 'shipping_company', ''),
                    getattr(product, 'solution', ''),
                    getattr(product, 'distributor_push_time', ''),
                    getattr(product, 'customer_quantity', 0),
                    getattr(product, 'customer_amount', 0),
                    getattr(product, 'weight', 0),
                    getattr(product, 'actual_weight', 0),
                    getattr(product, 'buyer_message', ''),
                    getattr(product, 'seller_remark', ''),
                    getattr(product, 'offline_remark', ''),
                    getattr(product, 'placing_time', ''),
                    getattr(product, 'payment_time', ''),
                    getattr(product, 'shipping_time', ''),
                    getattr(product, 'distributor', ''),
                    getattr(product, 'shipping_warehouse', ''),
                    getattr(product, 'platform', 'jushuitan'),
                    'regular'
                )
                all_data.append(data_tuple)
        
        # 处理取消商品数据
        if 'return_products' in products_data and products_data['return_products']:
            for product in products_data['return_products']:
                data_tuple = (
                    getattr(product, 'goods_id', ''),
                    getattr(product, 'name', ''),
                    getattr(product, 'price', 0),
                    getattr(product, 'stock', 0),
                    getattr(product, 'order_number', ''),
                    getattr(product, 'online_order_number', ''),
                    getattr(product, 'shop_name', ''),
                    getattr(product, 'label', ''),
                    getattr(product, 'buyer_nickname', ''),
                    getattr(product, 'supplier', ''),
                    getattr(product, 'purchase_amount', 0),
                    getattr(product, 'status', ''),
                    getattr(product, 'shipping_company', ''),
                    getattr(product, 'solution', ''),
                    getattr(product, 'distributor_push_time', ''),
                    getattr(product, 'customer_quantity', 0),
                    getattr(product, 'customer_amount', 0),
                    getattr(product, 'weight', 0),
                    getattr(product, 'actual_weight', 0),
                    getattr(product, 'buyer_message', ''),
                    getattr(product, 'seller_remark', ''),
                    getattr(product, 'offline_remark', ''),
                    getattr(product, 'placing_time', ''),
                    getattr(product, 'payment_time', ''),
                    getattr(product, 'shipping_time', ''),
                    getattr(product, 'distributor', ''),
                    getattr(product, 'shipping_warehouse', ''),
                    getattr(product, 'platform', 'jushuitan'),
                    'cancelled'
                )
                all_data.append(data_tuple)
        
        # 批量插入数据
        if all_data:
            cursor.executemany('''
                INSERT INTO products (
                    goods_id, name, price, stock, order_number, online_order_number, 
                    shop_name, label, buyer_nickname, supplier, purchase_amount, 
                    status, shipping_company, solution, distributor_push_time, 
                    customer_quantity, customer_amount, weight, actual_weight, 
                    buyer_message, seller_remark, offline_remark, 
                    placing_time, payment_time, shipping_time, 
                    distributor, shipping_warehouse, platform, data_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', all_data)
        
        conn.commit()
        conn.close()
        print(f"成功插入 {len(all_data)} 条聚水潭数据到数据库")
    
    def insert_pdd_data(self, pdd_products: List):
        """
        插入拼多多数据到数据库
        :param pdd_products: 拼多多商品数据列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        all_data = []
        for product in pdd_products:
            data_tuple = (
                getattr(product, 'goods_id', ''),
                getattr(product, 'name', ''),
                getattr(product, 'price', 0),
                getattr(product, 'stock', 0),
                getattr(product, 'order_number', ''),
                getattr(product, 'shop_name', ''),
                getattr(product, 'buyer_nickname', ''),
                getattr(product, 'supplier', ''),
                getattr(product, 'status', ''),
                getattr(product, 'shipping_company', ''),
                getattr(product, 'customer_quantity', 0),
                getattr(product, 'customer_amount', 0),
                getattr(product, 'buyer_message', ''),
                getattr(product, 'seller_remark', ''),
                getattr(product, 'placing_time', ''),
                getattr(product, 'payment_time', ''),
                getattr(product, 'shipping_time', ''),
                getattr(product, 'distributor', ''),
                getattr(product, 'shipping_warehouse', ''),
                getattr(product, 'platform', 'pinduoduo'),
                getattr(product, 'data_type', 'regular')
            )
            all_data.append(data_tuple)
        
        # 批量插入数据
        if all_data:
            cursor.executemany('''
                INSERT INTO pdd_products (
                    goods_id, name, price, stock, order_number, shop_name, 
                    buyer_nickname, supplier, status, shipping_company, 
                    customer_quantity, customer_amount, buyer_message, 
                    seller_remark, placing_time, payment_time, shipping_time, 
                    distributor, shipping_warehouse, platform, data_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', all_data)
        
        conn.commit()
        conn.close()
        print(f"成功插入 {len(all_data)} 条拼多多数据到数据库")
    
    def clear_table(self, table_name: str):
        """清空指定表的数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM {table_name}')
        conn.commit()
        conn.close()
        print(f"已清空 {table_name} 表")


# 使用示例
# if __name__ == "__main__":
#     # 示例：如何使用
#     db_manager = DataToDB()
    
    # 假设你有从爬虫获取的数据
    # jushuitan_data = {
    #     'regular_products': [...],  # 常规商品数据
    #     'return_products': [...]    # 被取消商品数据
    # }
    # db_manager.insert_jushuitan_data(jushuitan_data)
    
    # pdd_products = [...]  # 拼多多商品数据
    # db_manager.insert_pdd_data(pdd_products)