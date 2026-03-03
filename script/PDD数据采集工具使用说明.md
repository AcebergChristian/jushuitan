# PDD数据采集工具 - 使用说明

## 📋 目录

- [功能介绍](#功能介绍)
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [常见问题](#常见问题)
- [故障排除](#故障排除)

---

## 功能介绍

PDD数据采集工具是一个自动化数据采集程序，用于从拼多多商家后台获取：

1. **推广数据**：商品广告推广费用、点击量等数据
2. **账单数据**：退款金额、订单号等财务数据

采集的数据自动保存到 MySQL 数据库，供后续分析使用。

---

## 系统要求

### 必需软件

1. **Python 3.8+**
   - 下载地址：https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **Google Chrome 浏览器**
   - 下载地址：https://www.google.com/chrome/

3. **MySQL 数据库**
   - 需要有可访问的 MySQL 数据库
   - 数据库配置在 `models/database_config.py` 中

### 系统配置

- **操作系统**：Windows 7 或更高版本
- **内存**：建议 4GB 以上
- **磁盘空间**：至少 500MB 可用空间
- **网络**：需要稳定的网络连接

---

## 快速开始

### 方式一：使用批处理脚本（推荐）

#### 第一步：安装环境（仅首次需要）

1. 双击运行 `安装依赖.bat`
2. 等待自动完成以下操作：
   - 检查 Python 环境
   - 创建虚拟环境
   - 安装所有依赖包

#### 第二步：运行程序

1. 双击运行 `运行工具.bat`
2. 程序会自动：
   - 激活虚拟环境
   - 检查依赖
   - 启动数据采集

### 方式二：手动执行（适合开发者）

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行程序
python pdd_clawer.py
```

---

## 配置说明

### 1. 数据库配置

编辑 `models/database_config.py`：

```python
DATABASE_NAME = os.getenv("DB_NAME", "pdd")
DATABASE_HOST = os.getenv("DB_HOST", "t21.nulls.cn")
DATABASE_PORT = int(os.getenv("DB_PORT", 3306))
DATABASE_USER = os.getenv("DB_USER", "pdd")
DATABASE_PASSWORD = os.getenv("DB_PASSWORD", "PzNPetJFEwWkdzGD")
```

或创建 `.env` 文件：

```env
DB_NAME=pdd
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
```

### 2. 店铺配置

编辑 `pdddata.py`：

```python
pdddata = [
    {
        "shopid": "18386894",           # 店铺ID
        "shopname": "飞流直上三千尺",    # 店铺名称
        "username": "14797898071",      # 登录账号
        "password": "Aa556678900."      # 登录密码
    },
    # 添加更多店铺...
]
```

### 3. Chrome 配置文件路径

编辑 `pdd_clawer.py` 中的 `create_driver` 函数：

```python
# Windows 路径示例
f"--user-data-dir=C:/Users/YourName/chrome_profiles/{profile_name}"

# macOS 路径示例
f"--user-data-dir=/Users/YourName/chrome_profiles/{profile_name}"
```

---

## 使用方法

### 启动程序

1. **双击** `运行工具.bat`
2. 程序会自动打开 Chrome 浏览器
3. 按照提示完成操作

### 操作流程

#### 1. 登录店铺

- 程序会自动打开拼多多商家后台登录页
- 如果提供了账号密码，会自动填写
- 可能需要手动完成验证码验证
- 完成登录后，按回车继续

#### 2. 选择日期

- 程序会自动进入推广页面
- 在页面上手动选择要采集的日期
- 选择完成后，按回车继续

#### 3. 采集推广数据

- 程序自动翻页采集所有推广数据
- 显示采集进度和数据条数
- 采集完成后自动保存到数据库

#### 4. 采集账单数据

- 程序自动进入对账中心
- 自动设置筛选条件（时间、类型等）
- 自动翻页采集所有账单数据
- 采集完成后自动保存到数据库

#### 5. 完成

- 所有数据采集完成
- 浏览器自动关闭
- 如果配置了多个店铺，会依次处理

---

## 常见问题

### Q1: 如何查看采集的数据？

**A:** 数据保存在 MySQL 数据库中：

- **推广数据表**：`pdd_ads`
- **账单数据表**：`pdd_bill_records`

可以使用 MySQL 客户端或数据库管理工具查看。

### Q2: 可以同时采集多个店铺吗？

**A:** 可以。在 `pdddata.py` 中配置多个店铺，程序会依次处理每个店铺。

### Q3: 采集失败怎么办？

**A:** 程序会显示错误信息。常见原因：

1. 网络连接问题
2. 登录失败（账号密码错误）
3. 页面加载超时
4. 数据库连接失败

查看错误信息，根据提示解决问题后重新运行。

### Q4: 可以修改采集日期吗？

**A:** 可以。程序会提示在页面上选择日期，你可以选择任意日期。

### Q5: 数据会重复吗？

**A:** 不会。程序在保存新数据前，会先删除该店铺该日期的旧数据。

### Q6: 可以定时自动运行吗？

**A:** 可以使用 Windows 任务计划程序设置定时任务：

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（每天、每周等）
4. 操作选择"启动程序"
5. 程序选择 `运行工具.bat`

---

## 故障排除

### 问题1：找不到 Python

**错误信息**：`'python' 不是内部或外部命令`

**解决方法**：
1. 确认已安装 Python 3.8+
2. 重新安装 Python，勾选 "Add Python to PATH"
3. 或手动添加 Python 到系统环境变量

### 问题2：找不到 Chrome 浏览器

**错误信息**：`selenium.common.exceptions.WebDriverException`

**解决方法**：
1. 确认已安装 Chrome 浏览器
2. 确认 Chrome 版本与 ChromeDriver 兼容
3. selenium-wire 会自动下载 ChromeDriver

### 问题3：数据库连接失败

**错误信息**：`Can't connect to MySQL server`

**解决方法**：
1. 检查数据库配置是否正确
2. 确认 MySQL 服务正在运行
3. 检查防火墙设置
4. 测试数据库连接：
   ```bash
   mysql -h host -u user -p
   ```

### 问题4：依赖安装失败

**错误信息**：`pip install` 报错

**解决方法**：
1. 升级 pip：`python -m pip install --upgrade pip`
2. 使用国内镜像：
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```
3. 检查网络连接

### 问题5：虚拟环境激活失败

**错误信息**：`无法加载文件 activate.ps1`

**解决方法**（Windows PowerShell）：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 问题6：Chrome 配置文件路径错误

**错误信息**：`user data directory is already in use`

**解决方法**：
1. 关闭所有 Chrome 窗口
2. 修改 `pdd_clawer.py` 中的路径
3. 确保路径存在且有写入权限

### 问题7：页面元素找不到

**错误信息**：`NoSuchElementException`

**解决方法**：
1. 拼多多页面可能更新了
2. 检查 XPath 是否正确
3. 增加等待时间
4. 手动完成操作后按回车继续

---

## 文件说明

```
script/
├── pdd_clawer.py              # 主程序
├── pdddata.py                 # 店铺配置
├── requirements.txt           # Python 依赖
├── 运行工具.bat               # 运行脚本
├── 安装依赖.bat               # 环境配置脚本
├── models/                    # 数据库模型
│   ├── database_config.py    # 数据库配置
│   └── database_models.py    # 数据模型
├── venv/                      # 虚拟环境（自动创建）
└── PDD数据采集工具使用说明.md # 本文件
```

---

## 技术支持

### 日志查看

程序运行时会在控制台输出详细日志，包括：
- 操作步骤
- 数据采集进度
- 错误信息

### 调试模式

如需查看更详细的信息，可以修改代码添加调试输出。

### 联系方式

如遇到无法解决的问题，请提供：
1. 错误信息截图
2. 操作步骤
3. 系统环境信息

---

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本
- 支持推广数据采集
- 支持账单数据采集
- 支持多店铺配置
- 自动保存到数据库

---

## 许可证

本工具仅供学习和研究使用，请遵守相关法律法规和平台规则。

---

**祝使用愉快！** 🎉
