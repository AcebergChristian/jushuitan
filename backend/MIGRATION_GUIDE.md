# SQLite 到 MySQL 迁移指南

## 迁移步骤

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

这会安装 `pymysql` MySQL 驱动。

### 2. 确认 MySQL 数据库配置

确保宝塔上的 MySQL 数据库已创建：
- 数据库名: `pdd`
- 用户名: `pdd`
- 密码: `PzNPetJFEwWkdzGD`
- 主机: `t21.nulls.cn`
- 端口: `3306`

### 3. 运行迁移脚本

```bash
# 从项目根目录运行
python backend/migrate_to_mysql.py
```

脚本会：
1. 连接到 SQLite 数据库 (`backend/database.db`)
2. 连接到 MySQL 数据库
3. 在 MySQL 中创建所有表结构
4. 批量迁移所有数据（每批 1000 条）
5. 验证迁移结果

### 4. 配置环境变量

迁移完成后，配置应用使用 MySQL：

**方式 1: 使用 .env 文件（推荐）**

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，确保 DATABASE_URL 设置正确
```

**方式 2: 设置系统环境变量**

```bash
# Linux/Mac
export DATABASE_URL='mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd'

# Windows
set DATABASE_URL=mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd
```

### 5. 重启应用

```bash
cd backend
python run.py
```

应用现在会连接到 MySQL 数据库。

## 验证迁移

### 检查数据完整性

```python
# 运行 Python 交互式环境
python

# 执行以下代码
import os
os.environ['DATABASE_URL'] = 'mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd'

from backend.models.database import User, Goods, Store, PddTable, PddBillRecord, JushuitanProduct

print(f"Users: {User.select().count()}")
print(f"Goods: {Goods.select().count()}")
print(f"Stores: {Store.select().count()}")
print(f"PDD Ads: {PddTable.select().count()}")
print(f"PDD Bills: {PddBillRecord.select().count()}")
print(f"Jushuitan Products: {JushuitanProduct.select().count()}")
```

### 测试 API

```bash
# 测试登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'

# 测试获取商品列表
curl http://localhost:8000/api/products/goods
```

## 回滚到 SQLite

如果需要回滚到 SQLite：

```bash
# 删除或注释 .env 中的 DATABASE_URL
# 或设置为 SQLite
export DATABASE_URL='sqlite:///database.db'

# 重启应用
python backend/run.py
```

## 注意事项

1. **字符集**: MySQL 使用 `utf8mb4` 字符集，支持完整的 Unicode（包括 emoji）
2. **时区**: 确保 MySQL 服务器时区设置正确
3. **备份**: 迁移前建议备份 SQLite 数据库文件
4. **性能**: MySQL 在大数据量下性能更好，但需要适当的索引优化
5. **连接池**: 生产环境建议配置连接池参数

## 数据库连接字符串格式

```
mysql://用户名:密码@主机:端口/数据库名
```

示例：
```
mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd
```

## 常见问题

### 1. 主机被阻止 (错误 1129)

错误信息：`Host 'xxx' is blocked because of many connection errors`

**快速解决：**
```bash
# 测试连接
python backend/test_mysql_connection.py

# 如果被阻止，查看详细解决方案
cat backend/fix_mysql_blocked.md
```

**在宝塔面板执行：**
1. 登录宝塔面板
2. 数据库 → MySQL → 管理 → phpMyAdmin
3. 执行 SQL: `FLUSH HOSTS;`

### 2. 连接失败

检查：
- MySQL 服务是否运行
- 防火墙是否开放 3306 端口
- 用户权限是否正确
- 主机地址是否可访问

**测试连接：**
```bash
python backend/test_mysql_connection.py
```

### 2. 字符编码问题

确保 MySQL 数据库使用 `utf8mb4` 字符集：

```sql
ALTER DATABASE pdd CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 迁移中断

脚本支持事务，如果中断可以重新运行。建议先清空 MySQL 表再重新迁移。

## 性能优化建议

1. **索引优化**: 已在模型中定义关键索引
2. **连接池**: 配置合适的连接池大小
3. **查询优化**: 使用 `.select()` 时只选择需要的字段
4. **批量操作**: 使用 `insert_many()` 和 `bulk_update()`

## 支持

如有问题，请检查：
1. 日志文件
2. MySQL 错误日志
3. 应用程序日志
