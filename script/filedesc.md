# Script 文件夹 - 完整文件说明

## 📋 文件分类

### 🎯 数据采集相关（主要功能）

| 文件名 | 说明 | 用途 |
|--------|------|------|
| `pdd_clawer.py` | 数据采集主程序 | 自动采集拼多多推广和账单数据 |
| `pdddata.py` | 店铺配置文件 | 配置要采集的店铺信息 |
| `requirements.txt` | 运行依赖列表 | 数据采集所需的 Python 包 |
| `运行工具.bat` | 🌟 运行脚本 | 一键运行数据采集工具 |
| `安装依赖.bat` | 环境配置脚本 | 创建虚拟环境并安装依赖 |

### 📦 打包相关（生成 EXE）

| 文件名 | 说明 | 用途 |
|--------|------|------|
| `pdd_api_enhanced.py` | 打包版主程序 | 用于打包成 EXE 的版本 |
| `一键打包.bat` | 🌟 一键打包脚本 | 自动完成所有打包步骤 |
| `setup_portable.bat` | 便携式环境设置 | 下载并配置便携式 Python |
| `build_portable.bat` | 便携式打包脚本 | 使用便携式 Python 打包 |
| `build.bat` | 传统打包脚本 | 使用系统 Python 打包 |
| `build_exe.py` | 打包脚本（无控制台） | PyInstaller 打包配置 |
| `build_exe_console.py` | 打包脚本（带控制台） | PyInstaller 打包配置 |
| `requirements_build.txt` | 打包依赖列表 | 打包所需的 Python 包 |

### 📚 文档相关

| 文件名 | 说明 | 内容 |
|--------|------|------|
| `README.md` | 主说明文档 | 完整的使用说明和配置指南 |
| `PDD数据采集工具使用说明.md` | 详细使用说明 | 数据采集工具的完整文档 |
| `快速开始指南.txt` | 快速开始 | 简明的使用步骤 |
| `快速开始.txt` | 打包快速开始 | 打包功能的快速指南 |
| `PORTABLE_README.md` | 便携式方案说明 | 便携式打包的详细文档 |
| `BUILD_README.md` | 打包详细说明 | 传统打包方式的文档 |
| `文件说明.md` | 本文件 | 所有文件的说明 |

### 🗂️ 数据库模型

| 文件/文件夹 | 说明 | 内容 |
|------------|------|------|
| `models/` | 数据库模型文件夹 | 包含所有数据库相关代码 |
| `models/__init__.py` | Python 包标识 | 空文件，标识为 Python 包 |
| `models/database_config.py` | 数据库配置 | MySQL 连接配置 |
| `models/database_models.py` | 数据模型 | PddTable 和 PddBillRecord 模型 |

### 🔧 配置文件

| 文件名 | 说明 | 用途 |
|--------|------|------|
| `.env.example` | 环境变量示例 | 数据库配置模板 |
| `.gitignore` | Git 忽略文件 | 指定不提交的文件 |

### 📁 自动生成的文件夹

| 文件夹 | 说明 | 何时创建 |
|--------|------|---------|
| `venv/` | 虚拟环境 | 运行 `安装依赖.bat` 时创建 |
| `python_portable/` | 便携式 Python | 运行 `一键打包.bat` 时创建 |
| `dist/` | 打包输出 | 打包完成后创建 |
| `build/` | 打包临时文件 | 打包过程中创建 |
| `__pycache__/` | Python 缓存 | Python 运行时创建 |

---

## 🎯 使用场景

### 场景1：日常数据采集

**需要的文件**：
- `pdd_clawer.py`
- `pdddata.py`
- `requirements.txt`
- `运行工具.bat`
- `安装依赖.bat`
- `models/` 文件夹

**操作步骤**：
1. 运行 `安装依赖.bat`（首次）
2. 编辑 `pdddata.py`
3. 运行 `运行工具.bat`

### 场景2：打包成 EXE 分发

**需要的文件**：
- `pdd_api_enhanced.py`
- `一键打包.bat`
- `setup_portable.bat`
- `build_portable.bat`
- `build_exe_console.py`
- `requirements_build.txt`
- `models/` 文件夹

**操作步骤**：
1. 运行 `一键打包.bat`
2. 在 `dist/` 文件夹获取 EXE 文件

### 场景3：开发和调试

**需要的文件**：
- 所有 `.py` 文件
- `requirements.txt`
- `models/` 文件夹

**操作步骤**：
1. 创建虚拟环境：`python -m venv venv`
2. 激活虚拟环境：`venv\Scripts\activate`
3. 安装依赖：`pip install -r requirements.txt`
4. 运行程序：`python pdd_clawer.py`

---

## 📊 文件依赖关系

```
pdd_clawer.py
├── models/database_config.py
├── models/database_models.py
└── pdddata.py

pdd_api_enhanced.py
├── models/database_config.py
└── models/database_models.py

运行工具.bat
├── requirements.txt
└── pdd_clawer.py

一键打包.bat
├── setup_portable.bat
├── build_portable.bat
└── build_exe_console.py
```

---

## 🔄 文件更新说明

### 需要定期更新的文件

1. **pdddata.py**
   - 添加新店铺时更新
   - 修改店铺信息时更新

2. **models/database_config.py**
   - 数据库地址变更时更新
   - 数据库账号密码变更时更新

### 不建议修改的文件

1. **models/database_models.py**
   - 数据库表结构定义
   - 除非数据库结构变更，否则不要修改

2. **批处理脚本（.bat 文件）**
   - 自动化脚本
   - 除非了解脚本逻辑，否则不要修改

---

## 🗑️ 可以删除的文件

### 如果只需要数据采集功能

可以删除以下打包相关文件：
- `pdd_api_enhanced.py`
- `一键打包.bat`
- `setup_portable.bat`
- `build_portable.bat`
- `build.bat`
- `build_exe.py`
- `build_exe_console.py`
- `requirements_build.txt`
- `PORTABLE_README.md`
- `BUILD_README.md`
- `快速开始.txt`

### 如果只需要打包功能

可以删除以下运行相关文件：
- `pdd_clawer.py`
- `pdddata.py`
- `运行工具.bat`
- `安装依赖.bat`
- `requirements.txt`
- `PDD数据采集工具使用说明.md`
- `快速开始指南.txt`

---

## 📝 文件大小参考

| 类型 | 大小 |
|------|------|
| Python 脚本 | 几十 KB |
| 文档文件 | 几十 KB |
| 虚拟环境 | 约 100-200 MB |
| 便携式 Python | 约 30-50 MB |
| 打包后的 EXE | 约 50-100 MB |

---

## 🎓 学习建议

### 新手用户

建议阅读顺序：
1. `快速开始指南.txt`
2. `PDD数据采集工具使用说明.md`
3. `README.md`

### 高级用户

建议阅读顺序：
1. `README.md`
2. `PORTABLE_README.md`
3. 源代码文件

---

**提示**：所有文档都使用 Markdown 格式，可以使用任何文本编辑器或 Markdown 阅读器打开。
