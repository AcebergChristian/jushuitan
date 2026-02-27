#!/usr/bin/env python3
"""
修复损坏的数据库
"""

import sys
import os
import sqlite3
import shutil
from datetime import datetime

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def repair_database():
    """修复数据库"""
    
    db_path = os.path.join(os.path.dirname(__file__), "database.db")
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"🔧 开始修复数据库: {db_path}\n")
    
    # 1. 备份数据库
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"📦 备份数据库到: {backup_path}")
    shutil.copy2(db_path, backup_path)
    print("✅ 备份完成\n")
    
    try:
        # 2. 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 3. 检查数据库完整性
        print("🔍 检查数据库完整性...")
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchall()
        print(f"   结果: {result[0][0]}\n")
        
        # 4. 删除损坏的索引
        print("🗑️  删除可能损坏的索引...")
        try:
            cursor.execute("DROP INDEX IF EXISTS pddtable_ad_id")
            print("   ✅ 删除 pddtable_ad_id")
        except Exception as e:
            print(f"   ⚠️ 删除失败: {e}")
        
        try:
            cursor.execute("DROP INDEX IF EXISTS pdd_ads_ad_id")
            print("   ✅ 删除 pdd_ads_ad_id")
        except Exception as e:
            print(f"   ⚠️ 删除失败: {e}")
        
        # 5. 重建所有索引
        print("\n🔨 重建索引...")
        cursor.execute("REINDEX")
        print("   ✅ 重建完成")
        
        # 6. 清理
        print("\n🧹 清理数据库...")
        cursor.execute("VACUUM")
        print("   ✅ 清理完成")
        
        conn.commit()
        conn.close()
        
        print("\n✅ 数据库修复完成！")
        print(f"💡 备份文件保存在: {backup_path}")
        
    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        
        print(f"\n💡 建议:")
        print(f"   1. 恢复备份: mv {backup_path} {db_path}")
        print(f"   2. 或者删除数据库重新开始: rm {db_path}")

if __name__ == "__main__":
    repair_database()
