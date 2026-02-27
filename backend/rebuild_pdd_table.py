#!/usr/bin/env python3
"""
重建 pdd_ads 表（导出数据 -> 删除表 -> 重新创建 -> 导入数据）
"""

import sys
import os
import sqlite3
import json
from datetime import datetime

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def rebuild_pdd_table():
    """重建 pdd_ads 表"""
    
    db_path = os.path.join(os.path.dirname(__file__), "database.db")
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"🔧 开始重建 pdd_ads 表...\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 导出数据
        print("📤 导出现有数据...")
        try:
            cursor.execute("SELECT * FROM pdd_ads")
            rows = cursor.fetchall()
            
            # 获取列名
            cursor.execute("PRAGMA table_info(pdd_ads)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # 转换为字典列表
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))
            
            print(f"   ✅ 导出了 {len(data)} 条记录")
            
            # 保存到文件
            backup_file = f"pdd_ads_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            print(f"   ✅ 数据已备份到: {backup_file}\n")
            
        except Exception as e:
            print(f"   ⚠️ 导出失败: {e}")
            print("   表可能不存在或已损坏，将创建新表\n")
            data = []
        
        # 2. 删除旧表
        print("🗑️  删除旧表...")
        try:
            cursor.execute("DROP TABLE IF EXISTS pdd_ads")
            print("   ✅ 删除完成\n")
        except Exception as e:
            print(f"   ⚠️ 删除失败: {e}\n")
        
        # 3. 创建新表
        print("🔨 创建新表...")
        cursor.execute("""
            CREATE TABLE pdd_ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_id VARCHAR(255) NOT NULL,
                ad_name VARCHAR(255),
                goods_id VARCHAR(255),
                store_id VARCHAR(255),
                goods_name VARCHAR(255),
                orderSpendNetCostPerOrder REAL,
                data_date DATE,
                raw_data TEXT,
                is_del INTEGER DEFAULT 0,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        print("   ✅ 表创建完成\n")
        
        # 4. 创建索引
        print("📋 创建索引...")
        
        cursor.execute("CREATE INDEX pdd_ads_ad_id ON pdd_ads(ad_id)")
        print("   ✅ ad_id 索引")
        
        cursor.execute("CREATE INDEX pdd_ads_goods_id ON pdd_ads(goods_id)")
        print("   ✅ goods_id 索引")
        
        cursor.execute("CREATE INDEX pdd_ads_store_id ON pdd_ads(store_id)")
        print("   ✅ store_id 索引")
        
        cursor.execute("CREATE INDEX pdd_ads_data_date ON pdd_ads(data_date)")
        print("   ✅ data_date 索引")
        
        cursor.execute("CREATE INDEX pdd_ads_store_date ON pdd_ads(store_id, data_date)")
        print("   ✅ (store_id, data_date) 索引")
        
        cursor.execute("CREATE UNIQUE INDEX pdd_ads_ad_id_data_date ON pdd_ads(ad_id, data_date)")
        print("   ✅ (ad_id, data_date) 唯一索引\n")
        
        # 5. 导入数据
        if data:
            print(f"📥 导入数据 ({len(data)} 条)...")
            
            # 准备插入语句
            columns_str = ', '.join(data[0].keys())
            placeholders = ', '.join(['?' for _ in data[0].keys()])
            insert_sql = f"INSERT INTO pdd_ads ({columns_str}) VALUES ({placeholders})"
            
            # 批量插入
            imported = 0
            skipped = 0
            for row in data:
                try:
                    cursor.execute(insert_sql, list(row.values()))
                    imported += 1
                except Exception as e:
                    skipped += 1
                    if skipped <= 5:  # 只显示前5个错误
                        print(f"   ⚠️ 跳过记录: {e}")
            
            print(f"   ✅ 导入成功: {imported} 条")
            if skipped > 0:
                print(f"   ⚠️ 跳过: {skipped} 条\n")
        
        conn.commit()
        conn.close()
        
        print("✅ pdd_ads 表重建完成！\n")
        print("💡 说明:")
        print("   - 表结构已重新创建")
        print("   - 所有索引已重建")
        print("   - (ad_id, data_date) 复合唯一约束已添加")
        
    except Exception as e:
        print(f"\n❌ 重建失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    rebuild_pdd_table()
