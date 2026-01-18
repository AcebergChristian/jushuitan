from sqlalchemy.orm import Session
from backend.models.database import Product, Store
from typing import Optional

def get_product_by_goods_id(db: Session, goods_id: str):
    """根据goods_id获取商品"""
    return db.query(Product).filter(Product.goods_id == goods_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    """获取商品列表"""
    return db.query(Product).offset(skip).limit(limit).all()

def create_product(db: Session, goods_id: str, name: str, price: float, platform: str, **kwargs):
    """创建新商品"""
    db_product = Product(goods_id=goods_id, name=name, price=price, platform=platform, **kwargs)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, **kwargs):
    """更新商品信息"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    for key, value in kwargs.items():
        if hasattr(db_product, key) and value is not None:
            setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    """删除商品"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False

def get_store_by_store_id(db: Session, store_id: str):
    """根据store_id获取店铺"""
    return db.query(Store).filter(Store.store_id == store_id).first()

def get_stores(db: Session, skip: int = 0, limit: int = 100):
    """获取店铺列表"""
    return db.query(Store).offset(skip).limit(limit).all()

def create_store(db: Session, name: str, platform: str, store_id: str, **kwargs):
    """创建新店铺"""
    db_store = Store(name=name, platform=platform, store_id=store_id, **kwargs)
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

def update_store(db: Session, store_id: int, **kwargs):
    """更新店铺信息"""
    db_store = db.query(Store).filter(Store.id == store_id).first()
    for key, value in kwargs.items():
        if hasattr(db_store, key) and value is not None:
            setattr(db_store, key, value)
    db.commit()
    db.refresh(db_store)
    return db_store

def delete_store(db: Session, store_id: int):
    """删除店铺"""
    db_store = db.query(Store).filter(Store.id == store_id).first()
    if db_store:
        db.delete(db_store)
        db.commit()
        return True
    return False