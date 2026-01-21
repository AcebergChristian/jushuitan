from backend.models.database import User
from backend.utils.auth import get_password_hash
from typing import Optional
from datetime import datetime

def get_user_by_username(db, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    try:
        return User.get(User.username == username)
    except User.DoesNotExist:
        return None

def get_user_by_id(db, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    try:
        return User.get(User.id == user_id)
    except User.DoesNotExist:
        return None

def get_user_by_email(db, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    try:
        return User.get(User.email == email)
    except User.DoesNotExist:
        return None

def get_users(db, skip: int = 0, limit: int = 100):
    """获取用户列表"""
    return User.select().where(User.is_del == False).offset(skip).limit(limit)

def create_user(db, username: str, email: str, password: str, role: str = "sales", good_id: Optional[int] = None):
    """创建新用户"""
    hashed_password = get_password_hash(password)
    db_user = User.create(
        username=username, 
        email=email, 
        hashed_password=hashed_password,
        role=role,
        good_id=good_id
    )
    return db_user

def update_user(db, user_id: int, **kwargs):
    """更新用户信息"""
    try:
        db_user = User.get(User.id == user_id)
        for key, value in kwargs.items():
            if hasattr(db_user, key):
                if value is not None:
                    setattr(db_user, key, value)
                elif key == 'good_id':  # 允许设置为None
                    setattr(db_user, key, value)
        db_user.updated_at = datetime.now()  # 更新时间戳
        db_user.save()
        return db_user
    except User.DoesNotExist:
        return None

def delete_user(db, user_id: int):
    """删除用户"""
    try:
        db_user = User.get(User.id == user_id)
        db_user.is_del = True  # 逻辑删除
        db_user.save()
        return True
    except User.DoesNotExist:
        return False


# 将模型对象转换为字典，并处理日期类型
def model_to_dict_safe(model):
    data = {}
    for field in model._meta.fields.values():
        value = getattr(model, field.name)
        if isinstance(value, datetime):
            value = value.strftime("%Y-%m-%d %H:%M:%S")
        data[field.name] = value
    return data
