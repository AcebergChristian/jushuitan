# SQLite 数据库损坏 - 解决方案

## 问题

```
peewee.DatabaseError: malformed database schema (pddtable_ad_id) - invalid rootpage
```

SQLite 数据库文件损坏了。

## 推荐方案：直接迁移到 MySQL

既然 SQLite 已经损坏，这是迁移到 MySQL 的好时机！

### 步骤 1: 解决 MySQL 连接问题

在宝塔面板执行：
```sql
FLUSH HOSTS;
```

详细步骤见: `MYSQL_BLOCKED_SOLUTION.md`

### 步骤 2: 测试 MySQL 连接

```bash
python3 backend/test_mysql_connection.py
```

### 步骤 3: 直接使用 MySQL 启动

不需要迁移数据（因为 SQLite 已损坏），直接配置使用 MySQL：

```bash
# 设置环境变量
export DATABASE_URL='mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd'

# 启动应用（会自动创建表）
cd backend
python3 run.py
```

或者创建 .env 文件：

```bash
cd backend
echo "DATABASE_URL=mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd" > .env
python3 run.py
```

## 备选方案：修复 SQLite

如果你需要保留 SQLite 中的数据：

### 方案 1: 快速修复（推荐）

```bash
python3 backend/quick_fix_db.py
```

这个脚本会：
1. 自动备份数据库
2. 尝试 VACUUM 修复
3. 如果失败，尝试导出重建
4. 如果都失败，提供删除重建选项

### 方案 2: 手动修复

```bash
# 备份
cp backend/database.db backend/database.db.backup

# 导出数据
sqlite3 backend/database.db .dump > backup.sql

# 创建新数据库
rm backend/database.db
sqlite3 backend/database.db < backup.sql

# 测试
python3 backend/run.py
```

### 方案 3: 删除并重建空数据库

```bash
# 备份（可选）
cp backend/database.db backend/database.db.backup

# 删除损坏的数据库
rm backend/database.db
rm backend/database.db-shm
rm backend/database.db-wal

# 启动应用会自动创建新数据库
cd backend
python3 run.py
```

## 为什么会损坏？

常见原因：
1. 应用异常终止时正在写入
2. 磁盘空间不足
3. 文件系统错误
4. 并发写入冲突

## 预防措施

迁移到 MySQL 可以避免这些问题：
- 更好的并发处理
- 更强的数据完整性
- 更好的错误恢复
- 适合生产环境

## 快速决策

**如果数据不重要或可以重新生成：**
→ 直接使用 MySQL（推荐）

**如果需要保留数据：**
→ 运行 `python3 backend/quick_fix_db.py`

**如果修复失败：**
→ 删除 SQLite，使用 MySQL 重新开始
