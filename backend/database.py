from playhouse.db_url import connect
from peewee import SqliteDatabase
from playhouse.pool import PooledMySQLDatabase
import os
from contextlib import contextmanager
from pathlib import Path
import logging

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv 未安装，跳过

from backend.models.database import create_tables

# 使用环境变量或默认值来配置数据库
# 默认使用 MySQL（生产环境）
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd')

# 根据数据库URL类型选择适当的数据库连接
if DATABASE_URL.startswith('sqlite:///'):
    # SQLite数据库
    database = SqliteDatabase(DATABASE_URL.replace('sqlite:///', ''), pragmas={
        'foreign_keys': 1,
        'ignore_check_constraints': 0,
        'journal_mode': 'wal',
    })
elif DATABASE_URL.startswith('mysql://'):
    # MySQL数据库 - 配置连接池参数
    # 解析数据库URL: mysql://user:password@host:port/database
    from urllib.parse import urlparse
    parsed = urlparse(DATABASE_URL)
    database = PooledMySQLDatabase(
        parsed.path[1:],  # database name (remove leading slash)
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=parsed.username,
        password=parsed.password,
        max_connections=20,  # 最大连接数
        stale_timeout=300,  # 连接过期时间（秒）
        charset='utf8mb4',
        autocommit=True
    )
else:
    # 其他数据库类型
    database = connect(DATABASE_URL)

@contextmanager
def get_db():
    """获取数据库连接的上下文管理器"""
    try:
        if database.is_closed():
            database.connect(reuse_if_open=True)
        yield database
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        raise
    finally:
        # 只在连接开启时才尝试关闭
        try:
            if not database.is_closed():
                database.close()
        except:
            # 如果关闭连接时出错，忽略（可能是连接已经无效）
            pass

def init_db():
    """初始化数据库，创建所有表"""
    try:
        if database.is_closed():
            database.connect()
        create_tables()
        database.close()
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise