"""
验证 MySQL 连接和数据的脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 设置 MySQL 连接
os.environ['DATABASE_URL'] = 'mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd'

from backend.models.database import (
    User, JushuitanProduct, Goods, Store, PddTable, PddBillRecord,
    database
)


def verify_connection():
    """验证数据库连接"""
    print("=" * 60)
    print("MySQL 连接验证")
    print("=" * 60)
    
    try:
        database.connect()
        print("✓ 数据库连接成功")
        print(f"  数据库类型: {type(database).__name__}")
        print(f"  数据库: {database.database}")
        
        # 验证表是否存在
        tables = database.get_tables()
        print(f"\n✓ 找到 {len(tables)} 个表:")
        for table in tables:
            print(f"  - {table}")
        
        return True
    except Exception as e:
        print(f"✗ 连接失败: {str(e)}")
        return False
    finally:
        if not database.is_closed():
            database.close()


def verify_data():
    """验证数据完整性"""
    print("\n" + "=" * 60)
    print("数据完整性验证")
    print("=" * 60)
    
    models = [
        ('用户表 (users)', User),
        ('聚水潭产品表 (jushuitan_products)', JushuitanProduct),
        ('商品表 (goods)', Goods),
        ('店铺表 (stores)', Store),
        ('拼多多广告表 (pdd_ads)', PddTable),
        ('拼多多账单表 (pdd_bill_records)', PddBillRecord),
    ]
    
    try:
        database.connect()
        
        for name, model in models:
            try:
                total = model.select().count()
                active = model.select().where(model.is_del == False).count()
                deleted = model.select().where(model.is_del == True).count()
                
                print(f"\n{name}:")
                print(f"  总记录数: {total}")
                print(f"  活跃记录: {active}")
                print(f"  已删除: {deleted}")
                
                # 显示最新的一条记录
                if total > 0:
                    latest = model.select().order_by(model.created_at.desc()).first()
                    if latest:
                        print(f"  最新记录时间: {latest.created_at}")
            except Exception as e:
                print(f"  ✗ 查询失败: {str(e)}")
        
        print("\n✓ 数据验证完成")
        
    except Exception as e:
        print(f"\n✗ 验证失败: {str(e)}")
    finally:
        if not database.is_closed():
            database.close()


def test_crud_operations():
    """测试基本的 CRUD 操作"""
    print("\n" + "=" * 60)
    print("CRUD 操作测试")
    print("=" * 60)
    
    try:
        database.connect()
        
        # 测试查询
        print("\n1. 测试查询操作...")
        user_count = User.select().count()
        print(f"   ✓ 查询成功，用户数: {user_count}")
        
        # 测试插入（使用测试数据）
        print("\n2. 测试插入操作...")
        test_user = User.create(
            username=f'test_user_{os.urandom(4).hex()}',
            email='test@example.com',
            hashed_password='test_hash',
            role='user'
        )
        print(f"   ✓ 插入成功，用户ID: {test_user.id}")
        
        # 测试更新
        print("\n3. 测试更新操作...")
        test_user.email = 'updated@example.com'
        test_user.save()
        print(f"   ✓ 更新成功")
        
        # 测试删除（逻辑删除）
        print("\n4. 测试删除操作...")
        test_user.is_del = True
        test_user.save()
        print(f"   ✓ 逻辑删除成功")
        
        # 物理删除测试数据
        test_user.delete_instance()
        print(f"   ✓ 物理删除成功")
        
        print("\n✓ CRUD 操作测试通过")
        
    except Exception as e:
        print(f"\n✗ CRUD 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if not database.is_closed():
            database.close()


def main():
    """主函数"""
    print("\nMySQL 数据库验证工具\n")
    
    # 1. 验证连接
    if not verify_connection():
        print("\n请检查 MySQL 配置和网络连接")
        sys.exit(1)
    
    # 2. 验证数据
    verify_data()
    
    # 3. 测试 CRUD
    test_crud_operations()
    
    print("\n" + "=" * 60)
    print("验证完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
