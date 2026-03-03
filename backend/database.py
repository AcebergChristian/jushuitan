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
    """统一数据库上下文"""
    try:
        if database.is_closed():
            database.connect()
        yield database
    except Exception as e:
        logging.error(f"Database error: {e}")
        raise
    finally:
        if not database.is_closed():
            database.close()


def reconnect_db():
    if not database.is_closed():
        database.close()
    database.connect()
    logging.info("Database reconnected")