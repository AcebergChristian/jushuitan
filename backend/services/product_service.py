from backend.models.database import Product, Store
from typing import Optional

def get_product_by_goods_id(db, goods_id: str):
    """根据goods_id获取商品"""
    try:
        return Product.get(Product.goods_id == goods_id)
    except Product.DoesNotExist:
        return None

def get_products(db, skip: int = 0, limit: int = 100):
    """获取商品列表"""
    return Product.select().offset(skip).limit(limit)

def create_product(db, goods_id: str, name: str, price: float, platform: str, **kwargs):
    """创建新商品"""
    db_product = Product.create(
        goods_id=goods_id, 
        name=name, 
        price=price, 
        platform=platform, 
        **kwargs
    )
    return db_product

def update_product(db, product_id: int, **kwargs):
    """更新商品信息"""
    try:
        db_product = Product.get(Product.id == product_id)
        for key, value in kwargs.items():
            if hasattr(db_product, key) and value is not None:
                setattr(db_product, key, value)
        db_product.save()
        return db_product
    except Product.DoesNotExist:
        return None

def delete_product(db, product_id: int):
    """删除商品"""
    try:
        db_product = Product.get(Product.id == product_id)
        db_product.is_del = True  # 逻辑删除
        db_product.save()
        return True
    except Product.DoesNotExist:
        return False

def get_store_by_store_id(db, store_id: str):
    """根据store_id获取店铺"""
    try:
        return Store.get(Store.store_id == store_id)
    except Store.DoesNotExist:
        return None

def get_stores(db, skip: int = 0, limit: int = 100):
    """获取店铺列表"""
    return Store.select().offset(skip).limit(limit)

def create_store(db, name: str, platform: str, store_id: str, **kwargs):
    """创建新店铺"""
    db_store = Store.create(
        name=name, 
        platform=platform, 
        store_id=store_id, 
        **kwargs
    )
    return db_store

def update_store(db, store_id: int, **kwargs):
    """更新店铺信息"""
    try:
        db_store = Store.get(Store.id == store_id)
        for key, value in kwargs.items():
            if hasattr(db_store, key) and value is not None:
                setattr(db_store, key, value)
        db_store.save()
        return db_store
    except Store.DoesNotExist:
        return None

def delete_store(db, store_id: int):
    """删除店铺"""
    try:
        db_store = Store.get(Store.id == store_id)
        db_store.is_del = True  # 逻辑删除
        db_store.save()
        return True
    except Store.DoesNotExist:
        return False