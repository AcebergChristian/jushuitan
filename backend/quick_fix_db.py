"""
快速修复数据库 - 使用 Python 内置方法
"""
import os
import sys
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

db_path = os.path.join(Path(__file__).resolve().parent, "database.db")

print("=" * 60)
print("SQLite 数据库快速修复")
print("=" * 60)

# 备份
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_path = f"{db_path}.backup_{timestamp}"
shutil.copy2(db_path, backup_path)
print(f"\n✓ 已备份到: {backup_path}")

# 方案 1: 尝试 VACUUM
print("\n尝试修复方案 1: VACUUM...")
try:
    conn = sqlite3.connect(db_path)
    conn.execute("VACUUM")
    conn.close()
    print("✓ VACUUM 成功")
    
    # 测试
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA integrity_check")
    conn.close()
    print("✓ 数据库修复成功！")
    print("\n可以重新运行: python3 backend/run.py")
    sys.exit(0)
except Exception as e:
    print(f"✗ VACUUM 失败: {str(e)}")

# 方案 2: 重建数据库
print("\n尝试修复方案 2: 导出并重建...")
try:
    # 连接到损坏的数据库
    old_conn = sqlite3.connect(db_path)
    
    # 创建新数据库
    new_db_path = f"{db_path}.new"
    new_conn = sqlite3.connect(new_db_path)
    
    # 复制数据
    for line in old_conn.iterdump():
        if 'sqlite_sequence' not in line:
            try:
                new_conn.execute(line)
            except:
                pass
    
    new_conn.commit()
    old_conn.close()
    new_conn.close()
    
    # 替换
    os.remove(db_path)
    os.rename(new_db_path, db_path)
    
    print("✓ 数据库重建成功！")
    print("\n可以重新运行: python3 backend/run.py")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ 重建失败: {str(e)}")

# 方案 3: 删除并重建
print("\n方案 3: 删除损坏的数据库，创建新的")
print("警告: 这将删除所有数据")
confirm = input("是否继续? (yes/no): ")

if confirm.lower() == 'yes':
    # 删除数据库文件
    for ext in ['', '-shm', '-wal']:
        file_path = f"{db_path}{ext}"
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✓ 已删除: {file_path}")
    
    # 创建新数据库
    from backend.models.database import create_tables
    create_tables()
    
    print("\n✓ 新数据库已创建！")
    print("\n下一步:")
    print("1. 如果有备份数据，可以导入")
    print("2. 或者直接迁移到 MySQL: ./migrate_to_mysql.sh")
else:
    print("\n已取消")
    print("\n建议:")
    print("1. 直接迁移到 MySQL（推荐）")
    print("2. 或恢复备份: cp", backup_path, db_path)
