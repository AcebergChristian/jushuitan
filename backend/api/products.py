from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas
from ..services import product_service
from ..database import get_db
from ..utils.auth import get_current_user
from ..models.database import User as UserModel, Product as ProductModel, Store as StoreModel

router = APIRouter()

# 产品相关路由
@router.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """创建新商品"""
    db_product = product_service.get_product_by_goods_id(db, goods_id=product.goods_id)
    if db_product:
        raise HTTPException(status_code=400, detail="商品ID已存在")
    return product_service.create_product(
        db=db,
        goods_id=product.goods_id,
        name=product.name,
        price=product.price,
        platform=product.platform,
        stock=product.stock,
        description=product.description,
        image_url=product.image_url
    )

@router.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取商品列表"""
    products = product_service.get_products(db, skip=skip, limit=limit)
    return products

@router.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """根据ID获取商品"""
    # 这里需要通过ID获取产品，但目前服务只提供通过goods_id获取
    # 我们直接查询数据库
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    return db_product

@router.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    """更新商品信息"""
    updated_product = product_service.update_product(db, product_id=product_id, **product.dict(exclude_unset=True))
    if updated_product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    return updated_product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """删除商品"""
    result = product_service.delete_product(db, product_id=product_id)
    if not result:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {"message": "商品删除成功"}

# 店铺相关路由
@router.post("/stores/", response_model=schemas.Store)
def create_store(store: schemas.StoreCreate, db: Session = Depends(get_db)):
    """创建新店铺"""
    db_store = product_service.get_store_by_store_id(db, store_id=store.store_id)
    if db_store:
        raise HTTPException(status_code=400, detail="店铺ID已存在")
    return product_service.create_store(
        db=db,
        name=store.name,
        platform=store.platform,
        store_id=store.store_id,
        owner=store.owner
    )

@router.get("/stores/", response_model=List[schemas.Store])
def read_stores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取店铺列表"""
    stores = product_service.get_stores(db, skip=skip, limit=limit)
    return stores

@router.get("/stores/{store_id}", response_model=schemas.Store)
def read_store(store_id: int, db: Session = Depends(get_db)):
    """根据ID获取店铺"""
    # 直接查询数据库
    db_store = db.query(StoreModel).filter(StoreModel.id == store_id).first()
    if db_store is None:
        raise HTTPException(status_code=404, detail="店铺不存在")
    return db_store

@router.put("/stores/{store_id}", response_model=schemas.Store)
def update_store(store_id: int, store: schemas.StoreUpdate, db: Session = Depends(get_db)):
    """更新店铺信息"""
    updated_store = product_service.update_store(db, store_id=store_id, **store.dict(exclude_unset=True))
    if updated_store is None:
        raise HTTPException(status_code=404, detail="店铺不存在")
    return updated_store

@router.delete("/stores/{store_id}")
def delete_store(store_id: int, db: Session = Depends(get_db)):
    """删除店铺"""
    result = product_service.delete_store(db, store_id=store_id)
    if not result:
        raise HTTPException(status_code=404, detail="店铺不存在")
    return {"message": "店铺删除成功"}