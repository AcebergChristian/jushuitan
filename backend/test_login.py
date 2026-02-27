"""
测试登录功能和数据库连接
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 设置环境变量
os.environ['DATABASE_URL'] = 'mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd'

print("=" * 60)
print("测试登录功能")
print("=" * 60)

try:
    # 测试数据库连接
    print("\n1. 测试数据库连接...")
    from backend.models.database import database, User
    
    database.connect()
    print(f"   ✓ 数据库连接成功: {type(database).__name__}")
    
    # 检查用户表
    print("\n2. 检查用户表...")
    user_count = User.select().count()
    print(f"   ✓ 用户表有 {user_count} 条记录")
    
    if user_count > 0:
        # 获取第一个用户
        first_user = User.select().first()
        print(f"   ✓ 第一个用户: {first_user.username}")
        print(f"   - Email: {first_user.email}")
        print(f"   - Role: {first_user.role}")
        print(f"   - Active: {first_user.is_active}")
    else:
        print("   ⚠ 用户表为空，需要创建管理员账户")
        print("\n   创建默认管理员账户...")
        from backend.utils.auth import get_password_hash
        
        admin_user = User.create(
            username='admin',
            email='admin@example.com',
            hashed_password=get_password_hash('admin123'),
            role='admin',
            is_active=True
        )
        print(f"   ✓ 管理员账户已创建")
        print(f"   - 用户名: admin")
        print(f"   - 密码: admin123")
    
    # 测试密码验证
    print("\n3. 测试密码验证...")
    from backend.utils.auth import verify_password
    
    test_user = User.select().where(User.username == 'admin').first()
    if test_user:
        # 测试正确密码
        is_valid = verify_password('admin123', test_user.hashed_password)
        print(f"   ✓ 密码验证功能正常: {is_valid}")
    
    database.close()
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    print("\n可以使用以下账户登录:")
    print("  用户名: admin")
    print("  密码: admin123")
    
except Exception as e:
    print(f"\n✗ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
