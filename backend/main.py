from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import include_routers
from backend.database import engine
from backend.models.database import Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

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
include_routers(app)

@app.get("/")
async def root():
    return {"message": "Welcome to 聚水潭和拼多多数据管理系统!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)