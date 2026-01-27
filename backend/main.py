import sys
import os
from pathlib import Path  # 推荐用 pathlib，更安全可靠

# 动态计算项目根目录（run.py 所在目录的父目录）
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 把项目根目录加入 sys.path（确保 from backend.xxx 能导入）
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from backend.api.dash import router as dash_router
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

# 包含API路由 - 必须在静态文件路由之前注册
app.include_router(dash_router, prefix="/api", tags=["dash"])
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(products_router, prefix="/api", tags=["products"])
app.include_router(auth_router, prefix="/api", tags=["auth"])





# 前端 dist 路径（你确认过的 backend/dist）
frontend_path = Path(__file__).resolve().parent.parent / "backend" / "dist"

if os.path.exists(frontend_path):
    # 挂载静态资源到 /static 路径
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    # 为前端路由提供兜底处理 - 但要确保不会影响API路由
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(request: Request, full_path: str):
        # 避免干扰API请求
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
            
        requested_path = frontend_path / full_path
        if requested_path.exists() and requested_path.is_file():
            return FileResponse(requested_path)
        
        # 对于所有其他请求，返回 index.html，让前端路由处理
        index_path = frontend_path / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        
        return JSONResponse({"detail": "Frontend index.html not found"}, status_code=500)
    
    print(f"前端静态文件已挂载到根路径: {frontend_path}")
else:
    print(f"警告: 前端 dist 目录不存在: {frontend_path}")

@app.get("/")
async def root():
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    
    # 如果前端文件没找到，返回更明显的提示
    return {
        "message": "欢迎使用聚水潭和拼多多数据管理系统！",
        "detail": "前端 index.html 未找到，请检查 backend/dist 目录下是否有 index.html"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)