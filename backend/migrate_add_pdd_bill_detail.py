#!/usr/bin/env python3
"""
数据库迁移脚本：添加 pdd_bill_details 表
用于存储拼多多账单明细数据
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.database import database, PddBillDetail


def migrate():
    """执行数据库迁移"""
    print("开始数据库迁移...")
    
    try:
        # 连接数据库
        if database.is_closed():
            database.connect()
        
        # 检查表是否已存在
        if PddBillDetail.table_exists():
            print("⚠️ 表 pdd_bill_details 已存在，跳过创建")
        else:
            # 创建新表
            database.create_tables([PddBillDetail])
            print("✅ 成功创建表 pdd_bill_details")
        
        # 显示表结构
        print("\n表结构:")
        print("- bill_id: 账单ID (唯一)")
        print("- mall_id: 商家ID")
        print("- order_sn: 订单号 (索引)")
        print("- amount: 金额(分)")
        print("- amount_yuan: 金额(元)")
        print("- created_at_timestamp: 账单创建时间戳")
        print("- bill_type: 账单类型")
        print("- class_id: 分类ID")
        print("- class_id_desc: 分类描述")
        print("- finance_id: 财务ID")
        print("- finance_id_desc: 财务描述")
        print("- note: 备注")
        print("- bill_out_biz_code: 业务代码")
        print("- bill_out_biz_desc: 业务描述")
        print("- bill_biz_code: 账单业务代码")
        print("- shop_profile: 店铺配置名")
        print("- bill_date: 账单日期")
        print("- raw_data: 原始JSON数据")
        print("- is_del: 是否删除")
        print("- created_at: 创建时间")
        print("- updated_at: 更新时间")
        
        print("\n✅ 迁移完成！")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if not database.is_closed():
            database.close()
    
    return True


if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
