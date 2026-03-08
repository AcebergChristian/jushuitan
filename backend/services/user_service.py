from backend.models.database import User
from werkzeug.security import generate_password_hash
import json
from datetime import datetime
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_db_error(max_retries=2):
    """装饰器：数据库操作失败时自动重试"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    error_str = str(e)
                    
                    # 检查是否是连接错误
                    is_connection_error = (
                        "(0," in error_str or 
                        "Lost connection" in error_str or 
                        "gone away" in error_str or
                        "not connected" in error_str.lower()
                    )
                    
                    if is_connection_error and attempt < max_retries:
                        logger.warning(f"{func.__name__} failed (attempt {attempt + 1}), retrying...")
                        # 对于连接错误，简单依赖底层连接池的自动重连机制，
                        # 本次调用结束后会重新获取连接，不再在这里手动 close/connect。
                        continue
                    else:
                        # 不是连接错误或已达到最大重试次数
                        break
            
            # 所有重试都失败了：向上抛出最后一次错误，让接口明确返回 500 而不是静默返回 None
            logger.error(
                f"{func.__name__} failed after {max_retries + 1} attempts: {last_error}",
                exc_info=True,
            )
            if last_error:
                raise last_error
            raise Exception(f"{func.__name__} failed without explicit error")
        
        return wrapper
    return decorator


@retry_on_db_error(max_retries=2)
def get_user_by_username(db, username: str):
    """根据用户名获取用户"""
    return User.get_or_none(User.username == username)


@retry_on_db_error(max_retries=2)
def get_user_by_email(db, email: str):
    """根据邮箱获取用户"""
    return User.get_or_none(User.email == email)


@retry_on_db_error(max_retries=2)
def get_user_by_id(db, user_id: int):
    """根据ID获取用户"""
    return User.get_or_none(User.id == user_id)
        
@retry_on_db_error(max_retries=2)
def authenticate_user(db, username: str, password: str):
    """验证用户身份"""
    user = User.get_or_none(User.username == username)
    if user and check_password_hash(password, user.password_hash):
        return user
    return None


@retry_on_db_error(max_retries=2)
def create_user(db, username: str, email: str, password: str, role: str = "user"):
    """创建新用户"""
    hashed_password = generate_password_hash(password)
    user = User.create(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role
    )
    return user


@retry_on_db_error(max_retries=2)
def update_user(db, user_id: int, **kwargs):
    """更新用户信息"""
    query = User.update(**kwargs).where(User.id == user_id)
    result = query.execute()
    return result > 0


@retry_on_db_error(max_retries=2)
def delete_user(db, user_id: int):
    """删除用户"""
    user = User.get_or_none(User.id == user_id)
    if user:
        user.is_del = True
        user.save()
        return True
    return False


@retry_on_db_error(max_retries=2)
def get_all_users(db, skip: int = 0, limit: int = 10):
    """获取所有用户"""
    return User.select().offset(skip).limit(limit)

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