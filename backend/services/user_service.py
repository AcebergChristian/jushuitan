from backend.models.database import User
from werkzeug.security import generate_password_hash
import json
from datetime import datetime

def get_user_by_username(db, username: str):
    """根据用户名获取用户"""
    try:
        return User.get_or_none(User.username == username)
    except Exception as e:
        print(f"Error getting user by username: {e}")
        return None

def get_user_by_email(db, email: str):
    """根据邮箱获取用户"""
    try:
        return User.get_or_none(User.email == email)
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

def get_user_by_id(db, user_id: int):
    """根据ID获取用户"""
    try:
        return User.get_or_none(User.id == user_id)
    except Exception as e:
        print(f"Error getting user by id: {e}")
        return None
        
def authenticate_user(db, username: str, password: str):
    """验证用户身份"""
    try:
        user = User.get_or_none(User.username == username)
        if user and check_password_hash(password, user.password_hash):
            return user
        return None
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None

def create_user(db, username: str, email: str, password: str, role: str = "user"):
    """创建新用户"""
    try:
        hashed_password = generate_password_hash(password)
        user = User.create(
            username=username,
            email=email,
            hashed_password=hashed_password,  # 使用正确的字段名
            role=role
        )
        return user
    except Exception as e:
        print(f"Error creating user: {e}")
        raise e

def update_user(db, user_id: int, **kwargs):
    """更新用户信息"""
    try:
        query = User.update(**kwargs).where(User.id == user_id)
        result = query.execute()
        return result > 0
    except Exception as e:
        print(f"Error updating user: {e}")
        raise e

def delete_user(db, user_id: int):
    """删除用户"""
    try:
        user = User.get_or_none(User.id == user_id)
        if user:
            user.is_del = True  # 软删除，标记为已删除
            user.save()
            return True
        return False
    except Exception as e:
        print(f"Error deleting user: {e}")
        raise e
        
def get_all_users(db, skip: int = 0, limit: int = 10):
    """获取所有用户"""
    try:
        return User.select().offset(skip).limit(limit)
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []

def model_to_dict_safe(model_instance):
    """安全地将模型实例转换为字典，特别处理JSON字段"""
    if model_instance is None:
        return None
    
    result = {}
    for field_name in model_instance._meta.fields.keys():
        field_value = getattr(model_instance, field_name)
        
        # 特殊处理goods_stores字段，将其从JSON字符串转换为Python对象
        if field_name == 'goods_stores':
            if isinstance(field_value, str):
                try:
                    result[field_name] = json.loads(field_value) if field_value else []
                except json.JSONDecodeError:
                    result[field_name] = []
            else:
                result[field_name] = field_value
        # 特殊处理hashed_password字段，不返回密码信息
        elif field_name == 'hashed_password':
            # 不包含密码字段
            continue
        # 对于日期时间字段，转换为ISO字符串格式
        elif isinstance(field_value, datetime):
            result[field_name] = field_value.isoformat()
        # 对于其他字段，直接赋值
        else:
            result[field_name] = field_value
    
    return result

def generate_password_hash(password: str) -> str:
    """生成密码哈希"""
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)

def check_password_hash(password: str, password_hash: str) -> bool:
    """检查密码哈希"""
    from werkzeug.security import check_password_hash
    return check_password_hash(password_hash, password)