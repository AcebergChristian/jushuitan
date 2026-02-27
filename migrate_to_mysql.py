"""
SQLite to MySQL 数据迁移脚本
使用方法：
1. 确保已安装 pymysql: pip install pymysql
2. 设置环境变量 DATABASE_URL 为 MySQL 连接字符串
3. 运行脚本: python backend/migrate_to_mysql.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from peewee import SqliteDatabase, MySQLDatabase
from playhouse.migrate import migrate as peewee_migrate
import pymysql

# 导入模型
from backend.models.database import (
    User, JushuitanProduct, Goods, Store, PddTable, PddBillRecord,
    BaseModel
)


def create_mysql_connection(host, port, user, password, database):
    """创建 MySQL 数据库连接"""
    return MySQLDatabase(
        database,
        user=user,
        password=password,
        host=host,
        port=port,
        charset='utf8mb4',
        connect_timeout=10,
        read_timeout=30,
        write_timeout=30
    )


def create_sqlite_connection(db_path):
    """创建 SQLite 数据库连接"""
    return SqliteDatabase(db_path)


def migrate_table_data(source_db, target_db, model_class, batch_size=1000):
    """
    迁移单个表的数据
    
    Args:
        source_db: 源数据库连接
        target_db: 目标数据库连接
        model_class: Peewee 模型类
        batch_size: 批量插入大小
    """
    table_name = model_class._meta.table_name
    print(f"\n开始迁移表: {table_name}")
    
    # 临时绑定到源数据库
    model_class._meta.database = source_db
    
    try:
        # 获取源数据总数
        total_count = model_class.select().where(model_class.is_del == False).count()
        print(f"  源数据库记录数: {total_count}")
        
        if total_count == 0:
            print(f"  表 {table_name} 没有数据，跳过")
            return
        
        # 切换到目标数据库
        model_class._meta.database = target_db
        
        # 批量迁移数据
        migrated_count = 0
        batch_data = []
        
        # 重新绑定到源数据库读取数据
        model_class._meta.database = source_db
        
        for record in model_class.select().where(model_class.is_del == False).iterator():
            # 获取记录的所有字段数据
            record_data = {}
            for field_name in model_class._meta.fields.keys():
                if field_name != 'id':  # 跳过自增ID
                    record_data[field_name] = getattr(record, field_name)
            
            batch_data.append(record_data)
            
            # 达到批量大小时插入
            if len(batch_data) >= batch_size:
                model_class._meta.database = target_db
                with target_db.atomic():
                    model_class.insert_many(batch_data).execute()
                migrated_count += len(batch_data)
                print(f"  已迁移: {migrated_count}/{total_count}")
                batch_data = []
                model_class._meta.database = source_db
        
        # 插入剩余数据
        if batch_data:
            model_class._meta.database = target_db
            with target_db.atomic():
                model_class.insert_many(batch_data).execute()
            migrated_count += len(batch_data)
        
        print(f"  ✓ 表 {table_name} 迁移完成: {migrated_count} 条记录")
        
    except Exception as e:
        print(f"  ✗ 表 {table_name} 迁移失败: {str(e)}")
        raise
    finally:
        # 恢复数据库绑定
        model_class._meta.database = source_db


def main():
    """主迁移流程"""
    print("=" * 60)
    print("SQLite to MySQL 数据迁移工具")
    print("=" * 60)
    
    # MySQL 配置
    MYSQL_CONFIG = {
        'host': 't21.nulls.cn',
        'port': 3306,
        'user': 'pdd',
        'password': 'PzNPetJFEwWkdzGD',
        'database': 'pdd'
    }
    
    # SQLite 数据库路径
    sqlite_db_path = os.path.join(
        Path(__file__).resolve().parent,
        'database.db'
    )
    
    if not os.path.exists(sqlite_db_path):
        print(f"错误: SQLite 数据库文件不存在: {sqlite_db_path}")
        sys.exit(1)
    
    print(f"\n源数据库 (SQLite): {sqlite_db_path}")
    print(f"目标数据库 (MySQL): {MYSQL_CONFIG['user']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}")
    
    # 确认迁移
    confirm = input("\n确认开始迁移? (yes/no): ")
    if confirm.lower() != 'yes':
        print("迁移已取消")
        sys.exit(0)
    
    # 创建数据库连接
    print("\n连接数据库...")
    source_db = create_sqlite_connection(sqlite_db_path)
    target_db = create_mysql_connection(**MYSQL_CONFIG)
    
    try:
        # 测试连接
        source_db.connect()
        print("✓ SQLite 连接成功")
        
        # 尝试连接 MySQL，提供更详细的错误信息
        try:
            target_db.connect()
            print("✓ MySQL 连接成功")
        except Exception as e:
            error_msg = str(e)
            if '1129' in error_msg or 'blocked' in error_msg.lower():
                print("\n✗ MySQL 连接失败: 主机被阻止")
                print("\n原因: MySQL 服务器因为太多连接错误而阻止了你的 IP")
                print("\n解决方案:")
                print("1. 登录宝塔面板")
                print("2. 进入数据库管理 → MySQL → 管理")
                print("3. 执行 SQL: FLUSH HOSTS;")
                print("\n或者通过 SSH:")
                print(f"   mysqladmin -u root -p flush-hosts")
                print("\n或者修改 MySQL 配置 (my.cnf):")
                print("   [mysqld]")
                print("   max_connect_errors = 1000")
                print("   然后重启 MySQL 服务")
                sys.exit(1)
            else:
                raise
        
        # 在目标数据库创建表结构
        print("\n创建 MySQL 表结构...")
        models = [User, JushuitanProduct, Goods, Store, PddTable, PddBillRecord]
        
        for model in models:
            model._meta.database = target_db
        
        target_db.create_tables(models, safe=True)
        print("✓ 表结构创建完成")
        
        # 迁移数据
        print("\n开始数据迁移...")
        start_time = datetime.now()
        
        for model in models:
            migrate_table_data(source_db, target_db, model)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print(f"✓ 数据迁移完成！耗时: {duration:.2f} 秒")
        print("=" * 60)
        
        # 验证数据
        print("\n验证迁移结果:")
        for model in models:
            model._meta.database = target_db
            count = model.select().count()
            print(f"  {model._meta.table_name}: {count} 条记录")
        
        print("\n迁移成功！")
        print("\n下一步:")
        print("1. 设置环境变量: export DATABASE_URL='mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd'")
        print("2. 或在 .env 文件中添加: DATABASE_URL=mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd")
        print("3. 重启应用程序")
        
    except Exception as e:
        print(f"\n✗ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if not source_db.is_closed():
            source_db.close()
        if not target_db.is_closed():
            target_db.close()


if __name__ == '__main__':
    main()
