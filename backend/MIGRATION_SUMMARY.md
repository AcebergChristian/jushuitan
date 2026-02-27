# 数据库迁移总结

## 已完成的修改

### 1. 依赖更新
- ✅ 添加 `pymysql==1.1.0` 到 `requirements.txt`

### 2. 代码修改

#### backend/models/database.py
- ✅ 支持通过环境变量 `DATABASE_URL` 配置数据库
- ✅ 自动识别 SQLite 和 MySQL 连接字符串
- ✅ 保持所有表结构和业务逻辑不变

#### backend/database.py
- ✅ 添加 MySQL 数据库支持
- ✅ 保持向后兼容 SQLite

### 3. 新增文件

#### 迁移工具
- ✅ `backend/migrate_to_mysql.py` - 数据迁移脚本
  - 批量迁移数据（每批 1000 条）
  - 事务保护
  - 进度显示
  - 数据验证

#### 验证工具
- ✅ `backend/verify_mysql.py` - MySQL 连接和数据验证
  - 连接测试
  - 数据完整性检查
  - CRUD 操作测试

#### 配置文件
- ✅ `backend/.env.example` - 环境变量示例
- ✅ `backend/switch_database.sh` - 数据库切换脚本

#### 文档
- ✅ `backend/MIGRATION_GUIDE.md` - 详细迁移指南
- ✅ 更新 `README.md` - 添加迁移说明

## MySQL 配置信息

```
主机: t21.nulls.cn
端口: 3306
数据库: pdd
用户: pdd
密码: PzNPetJFEwWkdzGD
```

连接字符串：
```
mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd
```

## 迁移步骤（简化版）

```bash
# 1. 安装依赖
cd backend
pip install -r requirements.txt

# 2. 运行迁移
python backend/migrate_to_mysql.py

# 3. 配置环境变量
export DATABASE_URL='mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd'

# 4. 验证迁移
python backend/verify_mysql.py

# 5. 启动应用
python backend/run.py
```

## 数据库表结构

所有表结构保持不变：

1. **users** - 用户表
2. **jushuitan_products** - 聚水潭产品表
3. **goods** - 商品表
4. **stores** - 店铺表
5. **pdd_ads** - 拼多多广告表
6. **pdd_bill_records** - 拼多多账单表

## 特性

### 自动切换
代码会根据 `DATABASE_URL` 环境变量自动选择数据库：
- `sqlite:///database.db` → SQLite
- `mysql://...` → MySQL

### 向后兼容
- 不设置环境变量时，默认使用 SQLite
- 所有业务逻辑代码无需修改
- API 接口保持不变

### 数据安全
- 迁移脚本使用事务保护
- 批量操作提高性能
- 保留原 SQLite 数据库作为备份

## 注意事项

1. **字符集**: MySQL 使用 `utf8mb4`，完全支持中文和 emoji
2. **索引**: 所有索引已在模型中定义，自动创建
3. **时区**: 确保 MySQL 服务器时区正确
4. **备份**: 迁移前 SQLite 文件会保留，可随时回滚
5. **性能**: MySQL 在大数据量下性能更优

## 回滚方案

如需回滚到 SQLite：

```bash
# 方式 1: 删除环境变量
unset DATABASE_URL

# 方式 2: 设置为 SQLite
export DATABASE_URL='sqlite:///database.db'

# 重启应用
python backend/run.py
```

## 生产环境部署建议

1. **使用 .env 文件**
   ```bash
   cd backend
   cp .env.example .env
   # 编辑 .env 文件
   ```

2. **配置连接池**（可选，用于高并发）
   ```python
   # 在 database.py 中添加
   database = MySQLDatabase(
       'pdd',
       user='pdd',
       password='PzNPetJFEwWkdzGD',
       host='t21.nulls.cn',
       port=3306,
       max_connections=20,
       stale_timeout=300
   )
   ```

3. **监控和日志**
   - 启用 MySQL 慢查询日志
   - 监控连接数和查询性能
   - 定期备份数据库

## 测试清单

- [ ] 安装 pymysql 依赖
- [ ] 运行迁移脚本
- [ ] 验证数据完整性
- [ ] 测试用户登录
- [ ] 测试商品查询
- [ ] 测试数据创建
- [ ] 测试数据更新
- [ ] 测试数据删除
- [ ] 检查 API 响应时间
- [ ] 验证中文数据显示正常

## 支持

如遇问题，请检查：
1. MySQL 服务是否运行
2. 网络连接是否正常
3. 用户权限是否正确
4. 防火墙是否开放 3306 端口
5. 查看应用日志和 MySQL 错误日志
