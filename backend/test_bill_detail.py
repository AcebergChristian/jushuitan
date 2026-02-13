#!/usr/bin/env python3
"""
测试脚本：验证账单明细表功能
"""

import sys
import os
import json
from datetime import datetime, date

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.database import database, PddBillDetail


def test_bill_detail():
    """测试账单明细表的创建和查询"""
    print("=" * 60)
    print("测试账单明细表功能")
    print("=" * 60)
    
    try:
        # 连接数据库
        if database.is_closed():
            database.connect()
        
        # 1. 测试插入数据
        print("\n1. 测试插入账单明细...")
        test_data = {
            "billId": "test_bill_001",
            "mallId": 263564789,
            "orderSn": "251229-176695580170223",
            "amount": 182,
            "createdAt": 1767353818,
            "type": 5,
            "classId": 2,
            "classIdDesc": "优惠券结算",
            "financeId": 2,
            "financeIdDesc": "优惠券补贴",
            "note": "交易成功优惠券支付金额结算",
            "billOutBizCode": "0010005",
            "billOutBizDesc": "交易收入-优惠券结算",
            "billBizCode": "5-00001"
        }
        
        # 检查是否已存在
        existing = PddBillDetail.select().where(
            PddBillDetail.bill_id == test_data["billId"]
        ).first()
        
        if existing:
            print(f"   账单 {test_data['billId']} 已存在")
        else:
            amount_fen = test_data["amount"]
            amount_yuan = amount_fen / 100.0
            
            bill = PddBillDetail.create(
                bill_id=test_data["billId"],
                mall_id=test_data["mallId"],
                order_sn=test_data["orderSn"],
                amount=amount_fen,
                amount_yuan=amount_yuan,
                created_at_timestamp=test_data["createdAt"],
                bill_type=test_data["type"],
                class_id=test_data["classId"],
                class_id_desc=test_data["classIdDesc"],
                finance_id=test_data["financeId"],
                finance_id_desc=test_data["financeIdDesc"],
                note=test_data["note"],
                bill_out_biz_code=test_data["billOutBizCode"],
                bill_out_biz_desc=test_data["billOutBizDesc"],
                bill_biz_code=test_data["billBizCode"],
                shop_profile="测试店铺",
                bill_date=date.today(),
                raw_data=json.dumps(test_data, ensure_ascii=False)
            )
            print(f"   ✅ 成功插入账单: {bill.order_sn} - {bill.amount_yuan}元")
        
        # 2. 测试查询数据
        print("\n2. 测试查询账单明细...")
        bills = PddBillDetail.select().where(
            PddBillDetail.is_del == False
        ).order_by(PddBillDetail.created_at.desc()).limit(5)
        
        print(f"   找到 {bills.count()} 条账单记录:")
        for bill in bills:
            print(f"   - 订单号: {bill.order_sn}")
            print(f"     金额: {bill.amount_yuan}元 ({bill.amount}分)")
            print(f"     类型: {bill.class_id_desc}")
            print(f"     财务: {bill.finance_id_desc}")
            print(f"     业务: {bill.bill_out_biz_desc}")
            print()
        
        # 3. 测试按订单号查询
        print("\n3. 测试按订单号查询...")
        order_sn = "251229-176695580170223"
        order_bills = PddBillDetail.select().where(
            PddBillDetail.order_sn == order_sn,
            PddBillDetail.is_del == False
        )
        
        print(f"   订单 {order_sn} 的账单记录:")
        for bill in order_bills:
            print(f"   - 金额: {bill.amount_yuan}元")
            print(f"     类型: {bill.class_id_desc}")
            print(f"     时间: {bill.created_at}")
        
        # 4. 统计信息
        print("\n4. 统计信息...")
        total_count = PddBillDetail.select().where(
            PddBillDetail.is_del == False
        ).count()
        print(f"   总账单数: {total_count}")
        
        # 按类型统计
        from peewee import fn
        type_stats = (PddBillDetail
                     .select(PddBillDetail.class_id_desc, 
                            fn.COUNT(PddBillDetail.id).alias('count'),
                            fn.SUM(PddBillDetail.amount_yuan).alias('total_amount'))
                     .where(PddBillDetail.is_del == False)
                     .group_by(PddBillDetail.class_id_desc))
        
        print("\n   按类型统计:")
        for stat in type_stats:
            print(f"   - {stat.class_id_desc}: {stat.count}条, 总额: {stat.total_amount:.2f}元")
        
        print("\n✅ 测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if not database.is_closed():
            database.close()
    
    return True


if __name__ == "__main__":
    success = test_bill_detail()
    sys.exit(0 if success else 1)
