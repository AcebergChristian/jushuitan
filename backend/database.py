from playhouse.db_url import connect
from peewee import SqliteDatabase
from playhouse.pool import PooledMySQLDatabase
import os
from contextlib import contextmanager
from pathlib import Path
import logging
from models.database import BaseModel

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
    # MySQL数据库 - 配置连接池参数，解决连接丢失问题
    # 解析数据库URL: mysql://user:password@host:port/database
    from urllib.parse import urlparse
    parsed = urlparse(DATABASE_URL)
    database = PooledMySQLDatabase(
        parsed.path[1:],  # database name (remove leading slash)
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=parsed.username,
        password=parsed.password,
        max_connections=8,  # 减少最大连接数，避免连接过多
        stale_timeout=300,  # 连接过期时间（秒）设置为5分钟
        charset='utf8mb4',
        # 添加MySQL连接参数以防止连接超时
        sql_mode="PIPES_AS_CONCAT",
        init_command="SET SESSION sql_mode='PIPES_AS_CONCAT'",
        connect_timeout=20,
        read_timeout=60,  # 增加读取超时时间
        write_timeout=300, # 增加写入超时时间
        autocommit=True,
    )

    BaseModel._meta.database = database
else:
    # 其他数据库类型
    database = connect(DATABASE_URL)

@contextmanager
def get_db():
    """获取数据库连接的上下文管理器"""
    db_conn = database
    try:
        # 确保连接有效
        if db_conn.is_closed():
            db_conn.connect()
        else:
            # 测试连接是否有效
            try:
                db_conn.execute_sql('SELECT 1')
            except Exception as e:
                logging.warning(f"Database connection test failed: {e}")
                # 如果连接失效，重新连接
                if not db_conn.is_closed():
                    db_conn.close()
                db_conn.connect()

        yield db_conn

    except Exception as e:
        logging.error(f"Database operation error: {e}")
        # 发生错误时尝试重新连接
        try:
            if not db_conn.is_closed():
                db_conn.close()
            db_conn.connect()
        except Exception as reconnect_error:
            logging.error(f"Reconnection failed: {reconnect_error}")
            raise
        raise
    finally:
        # 不要在这里关闭连接，让连接池管理连接
        pass





def init_db():
    """初始化数据库，创建所有表"""
    try:
        if database.is_closed():
            database.connect()
        create_tables()
        # 不在初始化完成后关闭连接，保持连接池活跃
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise

def reconnect_db():
    """重新连接数据库"""
    try:
        if not database.is_closed():
            database.close()
        database.connect()
        logging.info("Database reconnected successfully")
    except Exception as e:
        logging.error(f"Failed to reconnect database: {e}")
        raise