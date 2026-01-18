from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联商品
    products = relationship("Product", secondary="user_products", back_populates="users")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    goods_id = Column(String, unique=True, index=True, nullable=False)  # 商品唯一标识
    name = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    platform = Column(String, index=True, nullable=False)  # 平台来源：jushuitan/pinduoduo
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联用户
    users = relationship("User", secondary="user_products", back_populates="products")


class UserProduct(Base):
    __tablename__ = "user_products"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)


class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # 店铺名称
    platform = Column(String, index=True, nullable=False)  # 平台：jushuitan/pinduoduo
    store_id = Column(String, unique=True, index=True, nullable=False)  # 店铺ID
    owner = Column(String, nullable=True)  # 店主
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联商品
    products = relationship("Product", back_populates="store")


# 在Product类后添加关系
Product.store = relationship("Store", back_populates="products")