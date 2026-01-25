from playhouse.db_url import connect
from peewee import SqliteDatabase
import os
from contextlib import contextmanager

# 使用环境变量或默认值来配置数据库
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')

# 根据数据库URL类型选择适当的数据库连接
if DATABASE_URL.startswith('sqlite:///'):
    # SQLite数据库
    database = SqliteDatabase(DATABASE_URL.replace('sqlite:///', ''), pragmas={
        'foreign_keys': 1,
        'ignore_check_constraints': 0,
        'journal_mode': 'wal',
    })
else:
    # 其他数据库类型
    database = connect(DATABASE_URL)

@contextmanager
def get_db():
    """获取数据库连接的上下文管理器"""
    try:
        if database.is_closed():
            database.connect()
        yield database
    finally:
        if not database.is_closed():
            database.close()

def init_db():
    """初始化数据库，创建所有表"""
    from backend.models.database import create_tables
    create_tables()