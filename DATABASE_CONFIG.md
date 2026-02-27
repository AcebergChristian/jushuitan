# 数据库配置说明

## 当前配置

应用已配置为**默认使用 MySQL**。

## 直接启动（使用 MySQL）

```bash
cd backend
python3 run.py
```

应用会自动连接到 MySQL：
- 主机: t21.nulls.cn:3306
- 数据库: pdd
- 用户: pdd

## 切换到 SQLite（开发环境）

如果需要使用 SQLite（本地开发），设置环境变量：

```bash
export DATABASE_URL='sqlite:///database.db'
cd backend
python3 run.py
```

或创建 `backend/.env` 文件：
```
DATABASE_URL=sqlite:///database.db
```

## 配置优先级

1. 环境变量 `DATABASE_URL`（最高优先级）
2. `backend/.env` 文件
3. 代码默认值：MySQL（当前配置）

## 启动方式对比

### 方式 1: 直接启动（推荐）
```bash
cd backend
python3 run.py
```
✓ 使用默认 MySQL 配置

### 方式 2: 使用脚本
```bash
./start_with_mysql.sh
```
✓ 明确设置环境变量后启动

### 方式 3: 手动设置环境变量
```bash
export DATABASE_URL='mysql://pdd:PzNPetJFEwWkdzGD@t21.nulls.cn:3306/pdd'
cd backend
python3 run.py
```
✓ 显式指定数据库

## 验证当前配置

运行测试脚本：
```bash
python3 test_env_loading.py
```

## 注意事项

1. **首次启动**: 应用会自动在 MySQL 中创建所有表
2. **MySQL 连接问题**: 如果遇到连接被阻止，参考 `MYSQL_BLOCKED_SOLUTION.md`
3. **SQLite 已废弃**: 本地的 SQLite 数据库文件已损坏，不再使用

## 生产环境部署

生产环境无需额外配置，直接启动即可使用 MySQL。

如需修改数据库配置，在服务器上设置环境变量：
```bash
export DATABASE_URL='mysql://user:password@host:port/database'
```
