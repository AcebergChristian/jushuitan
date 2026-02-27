# MySQL 主机被阻止问题解决方案

## 错误信息
```
(1129, "Host '192.168.2.193' is blocked because of many connection errors; unblock with 'mysqladmin flush-hosts'")
```

## 原因
MySQL 服务器检测到来自你的 IP 地址的多次连接错误，为了安全自动阻止了该 IP。

## 解决方案

### 方案 1: 宝塔面板 - phpMyAdmin（最简单）

1. 登录宝塔面板: http://t21.nulls.cn:8888
2. 点击左侧菜单 "数据库"
3. 找到 MySQL，点击 "管理" 或 "phpMyAdmin"
4. 在 SQL 查询窗口执行：

```sql
FLUSH HOSTS;
```

5. 点击执行，完成后重新运行迁移脚本

### 方案 2: 宝塔面板 - 终端

1. 登录宝塔面板
2. 点击 "终端"
3. 执行命令：

```bash
mysql -u root -p
# 输入 MySQL root 密码
FLUSH HOSTS;
exit;
```

### 方案 3: SSH 直接连接服务器

```bash
# 连接服务器
ssh your_username@t21.nulls.cn

# 方式 A: 使用 mysqladmin
mysqladmin -u root -p flush-hosts

# 方式 B: 使用 mysql 命令
mysql -u root -p -e "FLUSH HOSTS;"
```

### 方案 4: 修改 MySQL 配置（长期解决）

在宝塔面板中：

1. 数据库 → MySQL → 配置修改
2. 找到 `[mysqld]` 部分
3. 添加或修改：

```ini
[mysqld]
max_connect_errors = 1000
```

4. 保存并重启 MySQL 服务

## 验证修复

执行以下命令测试连接：

```bash
python backend/verify_mysql.py
```

如果连接成功，重新运行迁移：

```bash
./migrate_to_mysql.sh
```

## 预防措施

1. **增加最大连接错误数**
   在 MySQL 配置中设置 `max_connect_errors = 1000`

2. **检查连接参数**
   确保数据库用户名、密码、主机地址都正确

3. **网络稳定性**
   确保网络连接稳定，避免频繁的连接中断

4. **使用连接池**
   在生产环境使用连接池管理数据库连接

## 常见问题

### Q: 为什么会被阻止？
A: 可能的原因：
- 之前的连接尝试使用了错误的密码
- 网络不稳定导致连接中断
- 防火墙或安全组配置问题
- 并发连接过多

### Q: FLUSH HOSTS 是否安全？
A: 是的，这个命令只是清除主机缓存，不会影响数据或其他配置。

### Q: 如何查看当前被阻止的主机？
A: 在 MySQL 中执行：
```sql
SELECT * FROM performance_schema.host_cache;
```

### Q: 修改后需要重启 MySQL 吗？
A: 
- `FLUSH HOSTS` 命令：不需要重启，立即生效
- 修改配置文件：需要重启 MySQL 服务

## 联系支持

如果以上方案都无法解决，请检查：
1. 宝塔面板的安全设置
2. 服务器防火墙规则
3. MySQL 用户权限设置
4. 网络连接状态
