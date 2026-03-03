import logging
from backend.database import database
from backend.models.database import User, JushuitanProduct, Goods, Store, PddTable, PddBillRecord


def init_db():
    try:
        # 1️⃣ 建立连接
        if database.is_closed():
            database.connect()
            logging.info("Database connected")

        # 2️⃣ 创建表（不存在才创建）
        database.create_tables([
            User,
        JushuitanProduct,
        Goods,
        Store,
        PddTable,
        PddBillRecord
        ], safe=True)

        logging.info("Database initialized successfully")

    except Exception as e:
        logging.error(f"Database init failed: {e}")
        raise