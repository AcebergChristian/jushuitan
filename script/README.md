# PDD数据采集工具 - 完整解决方案

## 📁 文件夹结构

```
script/
├── 🌟 运行工具.bat                 # 主入口：运行数据采集工具
├── 安装依赖.bat                    # 环境配置：创建虚拟环境并安装依赖
├── 快速开始指南.txt                # 快速开始指南
├── PDD数据采集工具使用说明.md      # 详细使用说明
│
├── pdd_clawer.py                  # 数据采集主程序
├── pdddata.py                     # 店铺配置文件
├── requirements.txt               # Python 依赖列表
│
├── models/                        # 数据库模型（独立版本）
│   ├── __init__.py
│   ├── database_config.py        # 数据库配置
│   └── database_models.py        # 数据模型（PddTable, PddBillRecord）
│
├── venv/                          # 虚拟环境（自动创建）
│
├── 一键打包.bat                   # 便携式打包方案
├── setup_portable.bat             # 设置便携式 Python 环境
├── build_portable.bat             # 使用便携式 Python 打包
├── python_portable/               # 便携式 Python（首次运行自动创建）
│
└── 打包相关文件...                # 其他打包脚本和文档
```

## ✨ 两种使用方式

### 方式一：直接运行（推荐，适合有 Python 环境）

**特点**：
- ✅ 使用系统已安装的 Python
- ✅ 创建独立的虚拟环境
- ✅ 快速启动，易于调试
- ✅ 适合开发和日常使用

**使用步骤**：

1. **安装环境**（仅首次需要）
   ```
   双击 "安装依赖.bat"
   ```

2. **配置店铺**
   ```
   编辑 pdddata.py，添加店铺信息
   ```

3. **运行程序**
   ```
   双击 "运行工具.bat"
   ```

详细说明：[PDD数据采集工具使用说明.md](PDD数据采集工具使用说明.md)

### 方式二：打包成 EXE（适合分发）

**特点**：
- ✅ 无需安装 Python
- ✅ 打包成独立的 .exe 文件
- ✅ 可在任何 Windows 系统运行
- ✅ 适合分发给其他用户

**使用步骤**：

1. **一键打包**
   ```
   双击 "一键打包.bat"
   ```

2. **获取可执行文件**
   ```
   在 dist 文件夹找到 "PDD数据采集工具.exe"
   ```

详细说明：[PORTABLE_README.md](PORTABLE_README.md)

## 🚀 快速开始

### 最简单的方式

1. **双击** `安装依赖.bat`（首次运行）
2. **编辑** `pdddata.py`（配置店铺信息）
3. **双击** `运行工具.bat`（开始采集）

### 配置说明

### 数据库配置

数据库配置在 `models/database_config.py` 中，默认从环境变量读取：

```python
DATABASE_NAME = os.getenv("DB_NAME", "pdd")
DATABASE_HOST = os.getenv("DB_HOST", "t21.nulls.cn")
DATABASE_PORT = int(os.getenv("DB_PORT", 3306))
DATABASE_USER = os.getenv("DB_USER", "pdd")
DATABASE_PASSWORD = os.getenv("DB_PASSWORD", "PzNPetJFEwWkdzGD")
```

如需修改，可以：
1. 直接修改 `models/database_config.py` 中的默认值
2. 或在系统中设置环境变量

### 店铺配置

在 `pdd_api_enhanced.py` 的 `SHOP_PROFILES` 列表中配置店铺信息：

```python
SHOP_PROFILES = [
    {
        "shopid": "18386894",
        "shopname": "飞流直上三千尺",
        "username": "14797898071",
        "password": "Aa556678900."
    },
    # 添加更多店铺...
]
```

## 🔧 开发说明

### 修改代码后重新打包

1. 修改 `pdd_api_enhanced.py` 或 `models/` 下的文件
2. 运行 `build.bat` 或 `python build_exe_console.py`
3. 新的 `.exe` 文件会在 `dist/` 文件夹生成

### 添加新的依赖

如果需要添加新的 Python 包：

1. 在 `requirements_build.txt` 中添加包名
2. 在打包脚本中添加 `--hidden-import=包名`
3. 重新打包

## ⚠️ 注意事项

1. **Chrome 浏览器**：运行时需要系统安装 Chrome 浏览器
2. **ChromeDriver**：首次运行时会自动下载
3. **数据库连接**：确保能连接到配置的 MySQL 数据库
4. **文件大小**：打包后的 `.exe` 约 50-100MB（包含 Python 解释器和所有依赖）

## 📊 数据表说明

### pdd_ads 表（广告推广数据）
- `ad_id`: 广告ID
- `goods_id`: 商品ID
- `store_id`: 店铺ID
- `orderSpendNetCostPerOrder`: 推广费
- `data_date`: 数据日期

### pdd_bill_records 表（账单退款数据）
- `shop_id`: 店铺ID
- `order_sn`: 订单号
- `amount`: 金额（元）
- `bill_date`: 账单日期

## 🐛 故障排除

### 打包失败

1. 确保已安装所有依赖：`pip install -r requirements_build.txt`
2. 检查 Python 版本（建议 3.8+）
3. 查看错误信息，可能缺少某些系统库

### 运行失败

1. 检查数据库连接配置
2. 确保 Chrome 浏览器已安装
3. 查看控制台输出的错误信息

### 数据库连接失败

1. 检查 `models/database_config.py` 中的配置
2. 确保 MySQL 服务正在运行
3. 检查防火墙设置

## 📞 技术支持

详细的打包说明请查看 `BUILD_README.md`
