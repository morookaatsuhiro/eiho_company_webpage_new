# EIHO Backend - 衛宝官网后台管理系统

FastAPI 后端，提供内容管理 API 和后台管理界面。

## 功能

- ✅ 前端页面托管（同端口 8000）
- ✅ 公开 API：`/api/public/home` 获取首页数据
- ✅ 后台管理：登录、内容编辑（Hero、Services、Strengths、公司信息）
- ✅ Session 认证（Cookie）
- ✅ PBKDF2 密码哈希
- ✅ SQLite 数据库（可切换 PostgreSQL）

## 快速开始

### 1. 安装依赖

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

复制 `.env.example` 为 `.env` 并修改：

```bash
ADMIN_USER=admin
ADMIN_PASS_HASH=你的密码哈希
SECRET_KEY=随机密钥
```

生成密码哈希：
```python
python -c "from app.auth import hash_password; print(hash_password('your_password'))"
```

### 3. 启动服务

```bash
# Windows
run_windows.bat

# Linux/Mac
./run.sh

# 或手动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问

- **前端主页**：http://127.0.0.1:8000/
- **后台管理**：http://127.0.0.1:8000/admin
- **公开 API**：http://127.0.0.1:8000/api/public/home
- **健康检查**：http://127.0.0.1:8000/health

默认账号：`admin` / `admin123`

## 项目结构

```
backend/
├── app/
│   ├── __init__.py          # 包初始化
│   ├── main.py              # FastAPI 主应用
│   ├── db.py                # 数据库配置
│   ├── models.py            # SQLAlchemy 模型
│   ├── schemas.py           # Pydantic 数据模型
│   ├── crud.py              # 数据库操作
│   ├── auth.py              # 认证（密码哈希、Session）
│   ├── admin_views.py       # 后台管理路由
│   └── templates/            # Jinja2 模板
│       ├── login.html
│       └── admin_home.html
├── requirements.txt         # Python 依赖
├── .env.example             # 环境变量示例
├── pyrightconfig.json       # 类型检查配置
└── README.md
```

## API 文档

启动后访问：http://127.0.0.1:8000/docs （Swagger UI）

### 公开 API

- `GET /api/public/home` - 获取首页数据

### 后台 API（需要登录）

- `PUT /api/admin/home` - 更新首页数据

## 数据库

默认使用 SQLite（`eiho.db`），首次运行会自动创建表。

切换到 PostgreSQL：
```bash
export DATABASE_URL="postgresql://user:password@localhost/eiho"
```

## 安全建议

1. **生产环境必须修改**：
   - `SECRET_KEY`（环境变量）
   - `ADMIN_PASS_HASH`（使用强密码）
   - CORS `allow_origins`（限制域名）

2. **HTTPS**：生产环境启用 HTTPS，Cookie `secure=True`

3. **数据库**：SQLite 仅适合开发，生产环境使用 PostgreSQL

## 开发

```bash
# 代码格式化（可选）
black app/

# 类型检查
pyright app/
```

## 故障排查

- **端口被占用**：修改 `run.sh` 或 `run_windows.bat` 中的端口号
- **数据库错误**：删除 `eiho.db` 重新创建
- **静态文件 404**：检查 `BASE_DIR` 路径是否正确
