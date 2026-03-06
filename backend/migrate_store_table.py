"""
数据库迁移脚本：为 Store 表添加 order_date 字段
"""
from models.database import database, Store
from peewee import DateField
import sys

def migrate():
    """执行迁移"""
    print("开始迁移 Store 表...")
    
    try:
        with database:
            # 1. 添加 order_date 字段
            print("1. 添加 order_date 字段...")
            
            # 检查字段是否已存在
            cursor = database.execute_sql("SHOW COLUMNS FROM stores LIKE 'order_date'")
            if cursor.fetchone():
                print("   order_date 字段已存在，跳过")
            else:
                # 添加字段
                database.execute_sql(
                    "ALTER TABLE stores ADD COLUMN order_date DATE NULL AFTER store_name"
                )
                print("   ✅ order_date 字段添加成功")
            
            # 2. 从 store_id 中提取日期并填充 order_date
            print("2. 从 store_id 提取日期填充 order_date...")
            stores = Store.select()
            updated_count = 0
            
            for store in stores:
                if '_' in store.store_id:
                    # 格式: shopId_YYYYMMDD
                    parts = store.store_id.split('_')
                    if len(parts) > 1:
                        date_str = parts[1]  # YYYYMMDD
                        if len(date_str) == 8:
                            # 转换为 YYYY-MM-DD
                            order_date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                            try:
                                from datetime import datetime
                                order_date = datetime.strptime(order_date_str, '%Y-%m-%d').date()
                                
                                # 更新 order_date
                                Store.update(order_date=order_date).where(
                                    Store.id == store.id
                                ).execute()
                                
                                # 更新 store_id（去掉日期后缀）
                                real_store_id = parts[0]
                                Store.update(store_id=real_store_id).where(
                                    Store.id == store.id
                                ).execute()
                                
                                updated_count += 1
                            except Exception as e:
                                print(f"   ⚠️ 处理记录 {store.id} 失败: {e}")
            
            print(f"   ✅ 更新了 {updated_count} 条记录")
            
            # 3. 删除旧的唯一索引
            print("3. 删除旧的唯一索引...")
            try:
                database.execute_sql("ALTER TABLE stores DROP INDEX store_id")
                print("   ✅ 旧索引删除成功")
            except Exception as e:
                print(f"   ⚠️ 删除旧索引失败（可能不存在）: {e}")
            
            # 4. 添加新的复合唯一索引
            print("4. 添加新的复合唯一索引...")
            try:
                database.execute_sql(
                    "ALTER TABLE stores ADD UNIQUE INDEX idx_store_id_order_date (store_id, order_date)"
                )
                print("   ✅ 新索引添加成功")
            except Exception as e:
                print(f"   ⚠️ 添加新索引失败: {e}")
            
            # 5. 添加 order_date 索引
            print("5. 添加 order_date 索引...")
            try:
                database.execute_sql(
                    "ALTER TABLE stores ADD INDEX idx_order_date (order_date)"
                )
                print("   ✅ order_date 索引添加成功")
            except Exception as e:
                print(f"   ⚠️ 添加 order_date 索引失败（可能已存在）: {e}")
            
            print("\n✅ 迁移完成！")
            return True
            
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def rollback():
    """回滚迁移"""
    print("开始回滚...")
    
    try:
        with database:
            # 删除 order_date 字段
            print("删除 order_date 字段...")
            database.execute_sql("ALTER TABLE stores DROP COLUMN order_date")
            
            # 恢复旧的唯一索引
            print("恢复旧的唯一索引...")
            database.execute_sql("ALTER TABLE stores ADD UNIQUE INDEX store_id (store_id)")
            
            print("✅ 回滚完成！")
            return True
            
    except Exception as e:
        print(f"❌ 回滚失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()
