from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas
from ..services import user_service
from ..database import get_db
from ..utils.auth import get_current_user
from ..models.database import User as UserModel

router = APIRouter()

@router.post("/users/", response_model=schemas.User)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    db_user = user_service.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    return user_service.create_user(db=db, username=user.username, email=user.email, password=user.password)

@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取用户列表"""
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """根据ID获取用户"""
    # 修复：添加正确的根据ID获取用户的方法
    db_user = user_service.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

@router.put("/users/{user_id}", response_model=schemas.User)
def update_existing_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息"""
    updated_user = user_service.update_user(db, user_id=user_id, **user.dict(exclude_unset=True))
    if updated_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return updated_user

@router.delete("/users/{user_id}")
def delete_existing_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    result = user_service.delete_user(db, user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"message": "用户删除成功"}