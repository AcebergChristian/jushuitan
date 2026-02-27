"""
修复损坏的 SQLite 数据库
"""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import sqlite3

def backup_database(db_path):
    """备份数据库"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{db_path}.backup_{timestamp}"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✓ 数据库已备份到: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"✗ 备份失败: {str(e)}")
        return None


def repair_database(db_path):
    """尝试修复数据库"""
    print(f"\n开始修复数据库: {db_path}")
    
    # 1. 备份原数据库
    backup_path = backup_database(db_path)
    if not backup_path:
        return False
    
    # 2. 尝试导出数据
    temp_sql = f"{db_path}.dump.sql"
    new_db = f"{db_path}.new"
    
    try:
        print("\n步骤 1: 导出数据...")
        # 使用 sqlite3 命令行工具导出
        os.system(f'sqlite3 "{db_path}" .dump > "{temp_sql}"')
        
        if not os.path.exists(temp_sql):
            print("✗ 导出失败")
            return False
        
        print("✓ 数据导出成功")
        
        print("\n步骤 2: 创建新数据库...")
        # 删除旧的新数据库（如果存在）
        if os.path.exists(new_db):
            os.remove(new_db)
        
        # 导入到新数据库
        os.system(f'sqlite3 "{new_db}" < "{temp_sql}"')
        
        if not os.path.exists(new_db):
            print("✗ 创建新数据库失败")
            return False
        
        print("✓ 新数据库创建成功")
        
        print("\n步骤 3: 验证新数据库...")
        # 验证新数据库
        conn = sqlite3.connect(new_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()
        
        if result[0] != 'ok':
            print(f"✗ 数据库验证失败: {result[0]}")
            return False
        
        print("✓ 数据库验证通过")
        
        print("\n步骤 4: 替换旧数据库...")
        # 删除旧数据库
        os.remove(db_path)
        # 重命名新数据库
        os.rename(new_db, db_path)
        
        # 清理临时文件
        if os.path.exists(temp_sql):
            os.remove(temp_sql)
        
        print("✓ 数据库修复完成！")
        return True
        
    except Exception as e:
        print(f"\n✗ 修复失败: {str(e)}")
        
        # 恢复备份
        if backup_path and os.path.exists(backup_path):
            print("\n尝试恢复备份...")
            if os.path.exists(db_path):
                os.remove(db_path)
            shutil.copy2(backup_path, db_path)
            print("✓ 已恢复备份")
        
        return False
    finally:
        # 清理临时文件
        for temp_file in [temp_sql, new_db]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass


def rebuild_database():
    """重建空数据库"""
    print("\n选项 2: 重建空数据库")
    print("警告: 这将删除所有现有数据！")
    
    confirm = input("确认重建空数据库? (yes/no): ")
    if confirm.lower() != 'yes':
        print("已取消")
        return False
    
    db_path = os.path.join(Path(__file__).resolve().parent, "database.db")
    
    # 备份
    backup_database(db_path)
    
    # 删除旧数据库
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # 删除相关文件
    for ext in ['-shm', '-wal']:
        wal_file = f"{db_path}{ext}"
        if os.path.exists(wal_file):
            os.remove(wal_file)
    
    print("✓ 旧数据库已删除")
    
    # 创建新数据库
    from backend.models.database import create_tables
    create_tables()
    
    print("✓ 新数据库已创建")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("SQLite 数据库修复工具")
    print("=" * 60)
    
    db_path = os.path.join(Path(__file__).resolve().parent, "database.db")
    
    if not os.path.exists(db_path):
        print(f"\n数据库文件不存在: {db_path}")
        print("将创建新数据库...")
        from backend.models.database import create_tables
        create_tables()
        print("✓ 新数据库已创建")
        return
    
    print(f"\n数据库路径: {db_path}")
    print(f"数据库大小: {os.path.getsize(db_path) / 1024 / 1024:.2f} MB")
    
    print("\n请选择操作:")
    print("1) 尝试修复数据库（保留数据）")
    print("2) 重建空数据库（删除所有数据）")
    print("3) 直接迁移到 MySQL（推荐）")
    print("4) 退出")
    
    choice = input("\n请输入选项 (1-4): ")
    
    if choice == '1':
        if repair_database(db_path):
            print("\n✓ 修复成功！可以重新启动应用")
        else:
            print("\n✗ 修复失败，建议选择选项 2 或 3")
    
    elif choice == '2':
        if rebuild_database():
            print("\n✓ 重建成功！可以重新启动应用")
    
    elif choice == '3':
        print("\n推荐直接迁移到 MySQL:")
        print("1. 先解决 MySQL 连接问题（执行 FLUSH HOSTS）")
        print("2. 运行: ./migrate_to_mysql.sh")
        print("\n这样可以避免 SQLite 的问题")
    
    else:
        print("\n已退出")


if __name__ == '__main__':
    main()
