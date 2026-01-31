from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from .. import schemas
from ..services import user_service
from ..database import get_db
from .auth import get_current_user
from ..models.database import User as UserModel, Goods
from datetime import datetime
import json


router = APIRouter()

@router.post("/users/", response_model=schemas.User)
def create_new_user(user: schemas.UserCreate, current_user: UserModel = Depends(get_current_user)):
    """创建新用户"""
    # 验证当前用户权限
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以创建用户")
    
    # 获取数据库连接
    with get_db() as db_connection:
        # 检查用户名是否已存在
        db_user = user_service.get_user_by_username(db_connection, username=user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        
        # 直接使用传入的goods_stores数据
        processed_goods_stores = user.goods_stores if user.goods_stores is not None else []
        
        created_user = UserModel.create(
            username=user.username,
            email=user.email,
            hashed_password=user_service.generate_password_hash(user.password),  # 使用正确的字段名
            role=user.role or "user",
            goods_stores=json.dumps(processed_goods_stores, ensure_ascii=False)  # 以JSON字符串形式存储
        )
        
        # 使用model_to_dict_safe函数转换数据格式
        user_dict = user_service.model_to_dict_safe(created_user)
        # 确保goods_stores是列表格式
        if 'goods_stores' not in user_dict or user_dict['goods_stores'] is None:
            user_dict['goods_stores'] = []
        return user_dict


@router.get("/users")
def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query(None, min_length=1),
    current_user: UserModel = Depends(get_current_user)
):
    """
    获取用户列表（包含总数）
    """
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="只有管理员可以查看用户列表")
    
    query = UserModel.select().where(UserModel.is_del == 0)  # 主查询中过滤掉已删除的用户
    
    # 添加搜索功能
    if search:
        query = query.where(
            (UserModel.username.contains(search)) | (UserModel.email.contains(search))
        )
    
    # 获取总数
    total = query.count()
    
    # 获取分页数据
    users = query.offset(skip).limit(limit)
    
    result = []
    for user in users:
        # 获取用户数据字典
        user_dict = user_service.model_to_dict_safe(user)
        # 使用模型的get_goods_stores方法获取正确解析的goods_stores数据
        user_dict["goods_stores"] = user.get_goods_stores()
        result.append(user_dict)
    
    return {"data": result, "total": total}



@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user



@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int, 
    user_update: schemas.UserUpdate, 
    current_user: UserModel = Depends(get_current_user)
):
    """
    更新用户信息
    """
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="只有管理员可以修改用户信息")
    
    existing_user = UserModel.get_or_none(UserModel.id == user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 准备更新数据
    update_data = user_update.dict(exclude_unset=True)
    
    # 特别处理goods_stores字段 - 直接追加和去重
    if 'goods_stores' in update_data:
        # 获取新的goods_stores
        new_goods_stores = update_data['goods_stores']
        
        # 去重：基于整个对象进行去重
        seen = set()
        unique_goods_stores = []
        for item in new_goods_stores:
            item_str = json.dumps(item, sort_keys=True)  # 将对象转换为排序后的字符串作为唯一标识
            if item_str not in seen:
                seen.add(item_str)
                unique_goods_stores.append(item)
        
        # 直接更新用户goods_stores字段，完全替换原有数据
        existing_user.goods_stores = json.dumps(unique_goods_stores, ensure_ascii=False)
        existing_user.save()
        del update_data['goods_stores']  # 从更新数据中移除，因为我们直接处理了
    
    # 特别处理密码字段
    if 'password' in update_data and update_data['password']:
        update_data['hashed_password'] = user_service.generate_password_hash(update_data['password'])
        del update_data['password']  # 从更新数据中移除密码字段
    
    # 更新其他字段（如果有）
    if update_data:
        query = UserModel.update(**update_data).where(UserModel.id == user_id)
        query.execute()
    
    # 获取更新后的用户数据
    updated_user = UserModel.get_or_none(UserModel.id == user_id)
    user_dict = user_service.model_to_dict_safe(updated_user)
    # 确保goods_stores是列表格式
    if 'goods_stores' not in user_dict or user_dict['goods_stores'] is None:
        user_dict['goods_stores'] = []
    
    return user_dict





    
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



# 添加一个新API来更新用户关联的商品和店铺信息
@router.put("/users/{user_id}/goods-stores")
def update_user_goods_stores(
    user_id: int, 
    goods_stores_data: dict,
    current_user: UserModel = Depends(get_current_user)
):
    """
    更新用户关联的商品和店铺信息
    """
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="只有管理员可以修改用户信息")
    
    user = UserModel.get_or_none(UserModel.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    goods_stores_list = goods_stores_data.get('goods_stores', [])
    
    # 验证数据格式
    for item in goods_stores_list:
        if not isinstance(item, dict) or 'good_id' not in item or 'store_id' not in item:
            raise HTTPException(status_code=400, detail="商品店铺关联数据格式错误，应为[{good_id:'', store_id:''}, ...]")
    
    user.set_goods_stores(goods_stores_list)
    user.updated_at = datetime.now()
    user.save()
    
    return {"message": "用户商品店铺关联信息更新成功"}


# 添加一个API来获取特定用户的所有关联商品信息
@router.get("/users/{user_id}/goods")
def get_user_goods(user_id: int, current_user: UserModel = Depends(get_current_user)):
    """
    获取特定用户关联的所有商品信息
    """
    if current_user.role != 'admin' and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="没有权限访问该用户信息")
    
    user = UserModel.get_or_none(UserModel.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    goods_stores_list = user.get_goods_stores()
    if not goods_stores_list:
        return {"data": [], "total": 0}
    
    # 从商品ID列表中获取详细的商品信息
    good_ids = [item['good_id'] for item in goods_stores_list if item.get('good_id')]
    if good_ids:
        goods = Goods.select().where(Goods.id.in_(good_ids))
        goods_list = [
            {
                "id": good.id,
                "goods_id": good.goods_id,
                "goods_name": good.goods_name,
                "store_id": good.store_id,
                "store_name": good.store_name,
                "order_id": good.order_id,
                "payment_amount": good.payment_amount,
                "sales_amount": good.sales_amount,
                "sales_cost": good.sales_cost,
                "gross_profit_1_occurred": good.gross_profit_1_occurred,
                "gross_profit_1_rate": good.gross_profit_1_rate,
                "advertising_expenses": good.advertising_expenses,
                "advertising_rate": good.advertising_rate,
                "gross_profit_3": good.gross_profit_3,
                "gross_profit_3_rate": good.gross_profit_3_rate,
                "gross_profit_4": good.gross_profit_4,
                "gross_profit_4_rate": good.gross_profit_4_rate,
                "net_profit": good.net_profit,
                "net_profit_rate": good.net_profit_rate,
                "creator": good.creator,
                "created_at": good.created_at,
                "updated_at": good.updated_at
            }
            for good in goods
        ]
    else:
        goods_list = []
    
    return {"data": goods_list, "total": len(goods_list)}