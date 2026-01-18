from fastapi import FastAPI
from .users import router as users_router
from .products import router as products_router
from .auth import router as auth_router

def include_routers(app: FastAPI):
    """注册所有路由"""
    app.include_router(users_router, prefix="/api/v1", tags=["users"])
    app.include_router(products_router, prefix="/api/v1", tags=["products", "stores"])
    app.include_router(auth_router, prefix="/api/v1", tags=["auth"])