# 聚水潭和拼多多数据管理系统

这是一个完整的全栈应用程序，用于爬取和管理聚水潭和拼多多平台的商品数据。

## 项目结构

```
jushuitan/
├── backend/
│   ├── main.py                 # FastAPI主应用
│   ├── database.py             # 数据库连接
│   ├── schemas.py              # Pydantic数据模型
│   ├── models/
│   │   └── database.py         # SQLAlchemy模型
│   ├── services/
│   │   ├── user_service.py     # 用户服务
│   │   └── product_service.py  # 产品服务
│   ├── api/
│   │   ├── __init__.py
│   │   ├── users.py           # 用户API路由
│   │   ├── products.py        # 产品API路由
│   │   └── auth.py            # 认证API路由
│   ├── utils/
│   │   └── auth.py            # 认证工具
│   └── spiders/
│       └── crawler.py         # 爬虫服务
├── web/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   ├── src/
│   │   ├── main.jsx
│   │   ├── index.css
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   └── Layout.jsx     # 布局组件
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx  # 仪表盘页面
│   │   │   ├── LoginPage.jsx  # 登录页面
│   │   │   ├── UsersPage.jsx  # 用户管理页面
│   │   │   └── ProductsPage.jsx # 产品管理页面
│   │   └── utils/
└── requirements.txt
└── test_api.py
```

## 技术栈

- **后端**: Python, FastAPI, SQLAlchemy, SQLite
- **前端**: React, Vite, Tailwind CSS
- **爬虫**: Playwright
- **认证**: JWT, BCrypt

## 功能特性

1. **用户管理**:
   - 用户注册/登录
   - 用户CRUD操作
   - 权限管理

2. **商品数据管理**:
   - 从聚水潭和拼多多爬取商品数据
   - 商品CRUD操作
   - 按平台分类管理

3. **数据关联**:
   - 用户与商品关联
   - 店铺与商品关联

4. **前端界面**:
   - 暗色主题设计
   - 响应式布局
   - 用户友好的管理界面

## 启动说明

### 后端启动

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 安装Playwright浏览器驱动:
```bash
playwright install chromium
```

3. 启动后端服务器:
```bash
cd backend
python main.py
```

服务器将在 `http://localhost:8000` 上运行。

### 前端启动

1. 安装Node.js依赖:
```bash
cd web
npm install
```

2. 启动开发服务器:
```bash
npm run dev
```

前端将在 `http://localhost:3000` 上运行。

## API文档

启动后端后，在 `http://localhost:8000/docs` 查看交互式API文档。

## 爬虫功能

爬虫服务位于 `backend/spiders/crawler.py`，支持以下功能：
- 聚水潭平台商品数据爬取
- 拼多多平台商品数据爬取
- 数据去重和存储

## 安全性

- 使用JWT进行身份验证
- 密码使用BCrypt加密
- 所有API端点受保护
- 输入验证和清理

## 数据库

使用SQLite作为默认数据库，存储在 `jushuitan_pdd_data.db` 文件中。