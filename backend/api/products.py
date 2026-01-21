from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import schemas
from ..services import product_service
from ..database import get_db
from ..models.database import User as UserModel, Product as ProductModel, Store as StoreModel, JushuitanProduct as JushuitanProductModel
import sqlite3
import os

router = APIRouter()


# 聚水潭数据相关路由
@router.get("/jushuitan_products/")
def read_jushuitan_products(skip: int = 0, limit: int = 100):
    """获取聚水潭商品数据列表"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="数据库不存在")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM jushuitan_products WHERE is_del = 0 LIMIT ? OFFSET ?', (limit, skip))
    records = cursor.fetchall()
    
    # 获取列名
    column_names = [description[0] for description in cursor.description]
    
    # 将结果转换为字典列表
    result = []
    for row in records:
        record_dict = {}
        for i, col_name in enumerate(column_names):
            record_dict[col_name] = row[i]
        result.append(record_dict)
    
    conn.close()
    return result

@router.get("/jushuitan_products/{record_id}")
def read_jushuitan_product(record_id: int):
    """根据ID获取聚水潭商品数据"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="数据库不存在")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM jushuitan_products WHERE id = ? AND is_del = 0', (record_id,))
    record = cursor.fetchone()
    
    if record is None:
        conn.close()
        raise HTTPException(status_code=404, detail="聚水潭数据不存在")
    
    # 获取列名
    column_names = [description[0] for description in cursor.description]
    
    # 将结果转换为字典
    record_dict = {}
    for i, col_name in enumerate(column_names):
        record_dict[col_name] = record[i]
    
    conn.close()
    return record_dict

@router.get("/jushuitan_products/type/{data_type}")
def read_jushuitan_products_by_type(data_type: str, skip: int = 0, limit: int = 100):
    """根据数据类型获取聚水潭商品数据"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="数据库不存在")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM jushuitan_products WHERE data_type = ? AND is_del = 0 LIMIT ? OFFSET ?', (data_type, limit, skip))
    records = cursor.fetchall()
    
    # 获取列名
    column_names = [description[0] for description in cursor.description]
    
    # 将结果转换为字典列表
    result = []
    for row in records:
        record_dict = {}
        for i, col_name in enumerate(column_names):
            record_dict[col_name] = row[i]
        result.append(record_dict)
    
    conn.close()
    return result

# 拼多多数据相关路由
@router.get("/pdd_products/")
def read_pdd_products(skip: int = 0, limit: int = 100):
    """获取拼多多商品数据列表"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="数据库不存在")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM pdd_products WHERE is_del = 0 LIMIT ? OFFSET ?', (limit, skip))
    records = cursor.fetchall()
    
    # 获取列名
    column_names = [description[0] for description in cursor.description]
    
    # 将结果转换为字典列表
    result = []
    for row in records:
        record_dict = {}
        for i, col_name in enumerate(column_names):
            record_dict[col_name] = row[i]
        result.append(record_dict)
    
    conn.close()
    return result

# 产品相关路由
@router.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100):
    """获取产品列表"""
    with get_db() as db:
        products = product_service.get_products(db, skip=skip, limit=limit)
        return list(products)

@router.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int):
    """根据ID获取产品"""
    with get_db() as db:
        product = product_service.get_product_by_goods_id(db, str(product_id))  # 注意：这里假设用ID作为goods_id
        if product is None:
            raise HTTPException(status_code=404, detail="产品不存在")
        return product

@router.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate):
    """创建新产品"""
    with get_db() as db:
        db_product = product_service.get_product_by_goods_id(db, product.goods_id)
        if db_product:
            raise HTTPException(status_code=400, detail="商品ID已存在")
        return product_service.create_product(
            db=db, 
            goods_id=product.goods_id, 
            name=product.name, 
            price=product.price, 
            platform=product.platform
        )

@router.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductUpdate):
    """更新产品信息"""
    with get_db() as db:
        updated_product = product_service.update_product(db, product_id=product_id, **product.dict(exclude_unset=True))
        if updated_product is None:
            raise HTTPException(status_code=404, detail="产品不存在")
        return updated_product

@router.delete("/products/{product_id}")
def delete_product(product_id: int):
    """删除产品"""
    with get_db() as db:
        result = product_service.delete_product(db, product_id=product_id)
        if not result:
            raise HTTPException(status_code=404, detail="产品不存在")
        return {"message": "产品删除成功"}

# 店铺相关路由
@router.get("/stores/", response_model=List[schemas.Store])
def read_stores(skip: int = 0, limit: int = 100):
    """获取店铺列表"""
    with get_db() as db:
        stores = product_service.get_stores(db, skip=skip, limit=limit)
        return list(stores)

@router.get("/stores/{store_id}", response_model=schemas.Store)
def read_store(store_id: str):
    """根据ID获取店铺"""
    with get_db() as db:
        store = product_service.get_store_by_store_id(db, store_id)
        if store is None:
            raise HTTPException(status_code=404, detail="店铺不存在")
        return store

@router.post("/stores/", response_model=schemas.Store)
def create_store(store: schemas.StoreCreate):
    """创建新店铺"""
    with get_db() as db:
        db_store = product_service.get_store_by_store_id(db, store.store_id)
        if db_store:
            raise HTTPException(status_code=400, detail="店铺ID已存在")
        return product_service.create_store(
            db=db, 
            name=store.name, 
            platform=store.platform, 
            store_id=store.store_id
        )

@router.put("/stores/{store_id}", response_model=schemas.Store)
def update_store(store_id: str, store: schemas.StoreUpdate):
    """更新店铺信息"""
    with get_db() as db:
        updated_store = product_service.update_store(db, store_id=store_id, **store.dict(exclude_unset=True))
        if updated_store is None:
            raise HTTPException(status_code=404, detail="店铺不存在")
        return updated_store

@router.delete("/stores/{store_id}")
def delete_store(store_id: str):
    """删除店铺"""
    with get_db() as db:
        result = product_service.delete_store(db, store_id=store_id)
        if not result:
            raise HTTPException(status_code=404, detail="店铺不存在")
        return {"message": "店铺删除成功"}