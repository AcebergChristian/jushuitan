# MySQL 连接被阻止 - 快速解决指南

## 当前问题

你的 IP (192.168.2.193) 被 MySQL 服务器阻止了。

## 立即解决（3 步）

### 步骤 1: 登录宝塔面板

访问: http://t21.nulls.cn:8888

### 步骤 2: 执行 FLUSH HOSTS

**方式 A - phpMyAdmin（推荐）:**
1. 点击左侧 "数据库"
2. 找到 MySQL，点击 "管理" 或 "phpMyAdmin"
3. 在 SQL 窗口输入并执行：
```sql
FLUSH HOSTS;
```

**方式 B - 终端:**
1. 点击宝塔面板的 "终端"
2. 执行：
```bash
mysql -u root -p -e "FLUSH HOSTS;"
```

### 步骤 3: 测试连接

```bash
python backend/test_mysql_connection.py
```

如果显示 "✓ 连接成功"，继续迁移：

```bash
./migrate_to_mysql.sh
```

## 详细文档

- 完整解决方案: `backend/fix_mysql_blocked.md`
- 迁移指南: `backend/MIGRATION_GUIDE.md`
- 测试工具: `backend/test_mysql_connection.py`

## 预防再次被阻止

在宝塔面板修改 MySQL 配置：

1. 数据库 → MySQL → 配置修改
2. 在 `[mysqld]` 部分添加：
```ini
max_connect_errors = 1000
```
3. 保存并重启 MySQL

## 需要帮助？

查看详细文档：
```bash
cat backend/fix_mysql_blocked.md
```
