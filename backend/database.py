from peewee import *
from contextlib import contextmanager
import os
from .models.database import database, create_tables

def init_db():
    """初始化数据库，创建所有表"""
    create_tables()

@contextmanager
def get_db():
    """获取数据库连接的上下文管理器"""
    database.connect()
    try:
        yield database
    finally:
        if not database.is_closed():
            database.close()