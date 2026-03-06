# backend/database.py

import os
import logging
from contextlib import contextmanager

from playhouse.pool import PooledMySQLDatabase


# 直接用环境变量，不用 urlparse
DATABASE_NAME = os.getenv("DB_NAME", "pdd")
DATABASE_HOST = os.getenv("DB_HOST", "t21.nulls.cn")
DATABASE_PORT = int(os.getenv("DB_PORT", 3306))
DATABASE_USER = os.getenv("DB_USER", "pdd")
DATABASE_PASSWORD = os.getenv("DB_PASSWORD", "PzNPetJFEwWkdzGD")


# ✅ 全局唯一数据库实例
database = PooledMySQLDatabase(
    DATABASE_NAME,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    max_connections=10,
    stale_timeout=300,
    charset="utf8mb4",
    autocommit=True,
)


@contextmanager
def get_db():
    """统一数据库上下文 - 改进版，处理连接超时"""
    try:
        # 确保连接是活跃的
        if database.is_closed():
            database.connect()
        else:
            # 测试连接是否有效，如果无效则重连
            try:
                database.execute_sql('SELECT 1')
            except Exception:
                logging.warning("Database connection stale, reconnecting...")
                database.close()
                database.connect()
        
        yield database
    except Exception as e:
        logging.error(f"Database error: {e}")
        # 如果是连接错误，尝试重连
        if "Lost connection" in str(e) or "gone away" in str(e):
            try:
                database.close()
                database.connect()
                logging.info("Database reconnected after error")
            except Exception as reconnect_error:
                logging.error(f"Failed to reconnect: {reconnect_error}")
        raise
    # 注意：不要在 finally 中关闭连接，让连接池管理


def reconnect_db():
    if not database.is_closed():
        database.close()
    database.connect()
    logging.info("Database reconnected")