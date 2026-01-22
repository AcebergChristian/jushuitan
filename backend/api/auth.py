from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import timedelta, datetime
import json
from typing import Optional
from .. import schemas
from ..services import user_service
from ..database import get_db
from ..utils.auth import verify_password, create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter()

def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        # 检查必要字段是否存在
        if username is None or user_id is None:
            raise credentials_exception
            
        token_data = schemas.TokenData(username=username)
        
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户信息
    with get_db() as db:
        user = user_service.get_user_by_id(db, user_id=user_id)
    
    # 验证用户是否存在且仍然活跃
    if user is None or not user.is_active:
        raise credentials_exception
        
    return user

def get_current_active_user(current_user: schemas.User = Depends(get_current_user)) -> schemas.User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户账户已停用")
    return current_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录接口"""
    with get_db() as db:
        # 首先尝试通过用户名查找用户
        user = user_service.get_user_by_username(db, username=form_data.username)
        
        # 如果用户名未找到，尝试通过邮箱查找
        if not user:
            user = user_service.get_user_by_email(db, email=form_data.username)
        
        # 验证用户存在且密码正确
        if not user or not user.is_active or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名/邮箱或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建访问令牌，包含用户ID和角色信息
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "exp": datetime.utcnow() + access_token_expires
        }
        
        access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        return {"access_token": access_token, "token_type": "bearer", "userinfo": json.dumps(token_data, ensure_ascii=False, indent=2).encode('utf-8').decode('utf-8')}

@router.post("/logout")
def logout():
    """用户登出接口"""
    # FastAPI的OAuth2方案没有服务器端会话管理，所以这里只是通知客户端清除本地存储的token
    return {"message": "登出成功"}

@router.get("/profile", response_model=schemas.User)
def get_user_profile(current_user: schemas.User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user

@router.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    """获取当前用户信息（兼容旧版）"""
    return current_user