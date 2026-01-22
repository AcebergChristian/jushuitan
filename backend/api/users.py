from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import schemas
from ..services import user_service
from ..database import get_db
from .auth import get_current_user
from ..models.database import User as UserModel
from datetime import datetime

router = APIRouter()

@router.post("/users/", response_model=schemas.User)
def create_new_user(user: schemas.UserCreate, current_user: UserModel = Depends(get_current_user)):
    """创建新用户"""
    # 验证当前用户权限
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以创建用户")
    
    with get_db() as db:
        db_user = user_service.get_user_by_username(db, username=user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        created_user = user_service.create_user(
            db=db, 
            username=user.username, 
            email=user.email, 
            password=user.password,
            role=user.role,
            good_id=user.good_id
        )
        # 使用model_to_dict_safe函数转换数据格式
        return user_service.model_to_dict_safe(created_user)

@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, current_user: UserModel = Depends(get_current_user)):
    """获取用户列表，admin用户不能看到自己"""
    with get_db() as db:
        users = user_service.get_users(db, skip=skip, limit=limit)
        # 如果当前用户是admin，则过滤掉自己
        if current_user.role == "admin":
            filtered_users = [user for user in users if user.id != current_user.id]
        else:
            filtered_users = list(users)
        return [user_service.model_to_dict_safe(u) for u in filtered_users]

@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, current_user: UserModel = Depends(get_current_user)):
    """根据ID获取用户"""
    with get_db() as db:
        db_user = user_service.get_user_by_id(db, user_id=user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        # 如果当前用户是admin，不允许查看自己的用户信息
        if current_user.role == "admin" and db_user.id == current_user.id:
            raise HTTPException(status_code=403, detail="管理员不能查看自己的用户信息")
        return db_user

@router.put("/users/{user_id}", response_model=schemas.User)
def update_existing_user(user_id: int, user: schemas.UserUpdate, current_user: UserModel = Depends(get_current_user)):
    """更新用户信息"""
    # 验证权限
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以更新用户")
    
    # 禁止admin更新自己的用户信息
    if current_user.role == "admin" and user_id == current_user.id:
        raise HTTPException(status_code=403, detail="管理员不能更新自己的用户信息")
    
    with get_db() as db:
        updated_user = user_service.update_user(db, user_id=user_id, **user.dict(exclude_unset=True))
        if updated_user is None:
            raise HTTPException(status_code=404, detail="用户不存在")
            # 使用model_to_dict_safe函数转换数据格式
        return user_service.model_to_dict_safe(updated_user)

        

@router.delete("/users/{user_id}")
def delete_existing_user(user_id: int, current_user: UserModel = Depends(get_current_user)):
    """删除用户"""
    # 验证权限
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以删除用户")
    
    # 禁止admin删除自己的用户信息
    if current_user.role == "admin" and user_id == current_user.id:
        raise HTTPException(status_code=403, detail="管理员不能删除自己的用户信息")
    
    with get_db() as db:
        result = user_service.delete_user(db, user_id=user_id)
        if not result:
            raise HTTPException(status_code=404, detail="用户不存在")
        return {"message": "用户删除成功"}