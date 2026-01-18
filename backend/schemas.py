from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 用户相关模式
class UserBase(BaseModel):
    username: str
    email: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 商品相关模式
class ProductBase(BaseModel):
    goods_id: str
    name: str
    price: float
    stock: int = 0
    description: Optional[str] = None
    image_url: Optional[str] = None
    platform: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    store_id: Optional[int] = None
    
    class Config:
        orm_mode = True

# 店铺相关模式
class StoreBase(BaseModel):
    name: str
    platform: str
    store_id: str
    owner: Optional[str] = None

class StoreCreate(StoreBase):
    pass

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    owner: Optional[str] = None

class Store(StoreBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 用户商品关联模式
class UserProductBase(BaseModel):
    user_id: int
    product_id: int

class UserProductCreate(UserProductBase):
    pass

class UserProduct(UserProductBase):
    class Config:
        orm_mode = True

# 认证相关模式
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None