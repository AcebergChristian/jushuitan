# backend/database.py

import os
import logging
from contextlib import contextmanager
from playhouse.pool import PooledMySQLDatabase
from pymysql import OperationalError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 直接用环境变量，不用 urlparse
DATABASE_NAME = os.getenv("DB_NAME", "pdd")
DATABASE_HOST = os.getenv("DB_HOST", "t21.nulls.cn")
DATABASE_PORT = int(os.getenv("DB_PORT", 3306))
DATABASE_USER = os.getenv("DB_USER", "pdd")
DATABASE_PASSWORD = os.getenv("DB_PASSWORD", "PzNPetJFEwWkdzGD")


# ✅ 全局唯一数据库实例 - 针对长时间批量操作优化
database = PooledMySQLDatabase(
    DATABASE_NAME,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    max_connections=30,  # 增加到 30 个连接，支持更多并发
    stale_timeout=600,  # 10 分钟，适应长时间批量操作
    charset="utf8mb4",
    autocommit=True,
    connect_timeout=300,  # 增加连接超时时间
    read_timeout=300,  # 5 分钟读取超时，适应大数据量查询
    write_timeout=300, # 5 分钟写入超时，适应批量插入
)


def ensure_connection():
    """确保数据库连接有效，如果无效则重连"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            if database.is_closed():
                logger.info("Database is closed, connecting...")
                database.connect(reuse_if_open=True)
            
            # 测试连接
            database.execute_sql('SELECT 1')
            return True
            
        except Exception as e:
            retry_count += 1
            logger.warning(f"Connection test failed (attempt {retry_count}/{max_retries}): {e}")
            
            try:
                if not database.is_closed():
                    database.close()
            except:
                pass
            
            if retry_count < max_retries:
                try:
                    database.connect(reuse_if_open=True)
                except Exception as conn_error:
                    logger.error(f"Reconnection failed: {conn_error}")
            else:
                logger.error("Max retries reached, connection failed")
                return False
    
    return False


@contextmanager
def get_db():
    """统一数据库上下文 - 使用 Peewee 连接池自动管理连接生命周期"""
    try:
        # 使用 Peewee 提供的 connection_context：
        # - 进入时自动获取/建立连接
        # - 退出时自动将连接归还到连接池并关闭底层连接
        with database.connection_context() as conn:
            yield database
    except OperationalError as e:
        logger.error(f"Database operational error: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Database error in context: {e}", exc_info=True)
        raise


def reconnect_db():
    """手动重连数据库"""
    try:
        if not database.is_closed():
            database.close()
        database.connect(reuse_if_open=True)
        logger.info("Database reconnected manually")
        return True
    except Exception as e:
        logger.error(f"Manual reconnection failed: {e}")
        return False