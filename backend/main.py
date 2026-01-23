import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.users import router as users_router
from backend.api.products import router as products_router
from backend.api.auth import router as auth_router
from backend.database import init_db

# 初始化数据库，创建所有表
init_db()

app = FastAPI(title="聚水潭和拼多多数据管理系统", version="1.0.0")

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 包含API路由
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(products_router, prefix="/api", tags=["products"])
app.include_router(auth_router, prefix="/api", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Welcome to 聚水潭和拼多多数据管理系统!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    