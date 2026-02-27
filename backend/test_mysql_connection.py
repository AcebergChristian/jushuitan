"""
快速测试 MySQL 连接
"""
import pymysql
import sys

MYSQL_CONFIG = {
    'host': 't21.nulls.cn',
    'port': 3306,
    'user': 'pdd',
    'password': 'PzNPetJFEwWkdzGD',
    'database': 'pdd',
    'connect_timeout': 10
}

print("测试 MySQL 连接...")
print(f"主机: {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}")
print(f"数据库: {MYSQL_CONFIG['database']}")
print(f"用户: {MYSQL_CONFIG['user']}")
print()

try:
    conn = pymysql.connect(**MYSQL_CONFIG)
    print("✓ 连接成功！")
    
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"✓ MySQL 版本: {version[0]}")
    
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"✓ 数据库中有 {len(tables)} 个表")
    
    cursor.close()
    conn.close()
    
    print("\n数据库连接正常，可以开始迁移！")
    sys.exit(0)
    
except pymysql.err.OperationalError as e:
    error_code, error_msg = e.args
    print(f"✗ 连接失败 (错误代码: {error_code})")
    print(f"   {error_msg}")
    print()
    
    if error_code == 1129:
        print("解决方案: 主机被阻止")
        print("请查看: backend/fix_mysql_blocked.md")
    elif error_code == 1045:
        print("解决方案: 用户名或密码错误")
        print("请检查数据库配置")
    elif error_code == 2003:
        print("解决方案: 无法连接到服务器")
        print("1. 检查服务器地址是否正确")
        print("2. 检查防火墙是否开放 3306 端口")
        print("3. 检查 MySQL 服务是否运行")
    
    sys.exit(1)
    
except Exception as e:
    print(f"✗ 未知错误: {str(e)}")
    sys.exit(1)
