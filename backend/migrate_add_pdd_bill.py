"""
数据库迁移脚本：添加 pdd_bill_records 表
"""
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import database, PddBillRecord

def migrate():
    """执行迁移"""
    print("🚀 开始迁移数据库...")
    
    try:
        with database:
            # 创建 pdd_bill_records 表
            if not database.table_exists('pdd_bill_records'):
                database.create_tables([PddBillRecord])
                print("✅ 成功创建 pdd_bill_records 表")
            else:
                print("⚠️ pdd_bill_records 表已存在，跳过创建")
        
        print("✅ 迁移完成")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate()
