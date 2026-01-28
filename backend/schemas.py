from pydantic import BaseModel
from typing import Optional, List
import json


# 用户相关模式
class UserBase(BaseModel):
    username: str
    email: str
    role: Optional[str] = "user"
    is_active: Optional[bool] = True
    is_del: Optional[bool] = False

class UserCreate(UserBase):
    password: str
    goods_stores: Optional[List[dict]] = []

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    goods_stores: Optional[List[dict]] = []


class User(UserBase):
    id: int
    role: Optional[str] = None
    created_at: str
    updated_at: str
    goods_stores: Optional[List[dict]] = []
    
    class Config:
        from_attributes = True   # Peewee兼容性配置

    @classmethod
    def validate_goods_stores(cls, v):
        """验证并转换goods_stores字段"""
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v if v is not None else []


# 商品相关模式
class ProductBase(BaseModel):
    goods_id: str
    name: str
    price: float
    platform: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    platform: Optional[str] = None

class Product(ProductBase):
    id: int
    is_del: bool = False
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True  # Peewee兼容性配置

# 店铺相关模式
class StoreBase(BaseModel):
    name: str
    platform: str
    store_id: str

class StoreCreate(StoreBase):
    pass

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    platform: Optional[str] = None

class Store(StoreBase):
    id: int
    is_del: bool = False
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True  # Peewee兼容性配置

# 认证相关模式
class Token(BaseModel):
    access_token: str
    token_type: str
    userinfo: str

class TokenData(BaseModel):
    username: Optional[str] = None