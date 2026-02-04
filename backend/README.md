# StudySync Backend

## 项目说明

StudySync 后端服务，基于 FastAPI + PostgreSQL 实现。

**推荐部署方式**：
- ✅ **本地开发（Anaconda 环境）**：适合开发调试，快速迭代
- 🐳 **Docker Compose**：适合生产环境部署，容器化管理

本文档优先介绍本地开发方式。

## 技术栈

- FastAPI - Web 框架
- PostgreSQL - 数据库（使用外部已有容器）
- SQLAlchemy - ORM
- Pydantic - 数据验证
- JWT - 用户认证

## 目录结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── database.py          # 数据库配置和连接
│   ├── models.py            # SQLAlchemy ORM 模型
│   ├── schemas.py           # Pydantic 数据验证模型
│   ├── auth.py              # JWT 认证和权限管理
│   ├── init_db.py           # 数据库初始化脚本
│   └── routes/              # API 路由模块
│       ├── auth.py          # 认证相关接口
│       ├── users.py         # 用户管理接口
│       ├── plans.py         # 学习计划接口
│       ├── checkins.py      # 打卡记录接口
│       ├── groups.py        # 群组管理接口
│       └── ai.py            # AI 学习评估接口
├── Dockerfile               # Docker 镜像构建文件
├── docker-compose.yml       # Docker Compose 配置（备选）
├── requirements.txt          # Python 依赖包
├── .env                     # 环境变量配置
└── README.md                # 项目文档
```

## 数据库连接配置

本项目使用外部已有的 PostgreSQL Docker 容器：

- **容器名称**: `learnpgsql`
- **数据库名称**: `studysync`
- **端口**: 5432

### 连接方式

#### 本地开发（Anaconda 环境）

使用 `localhost` 连接：
```
postgresql://postgres:password@localhost:5432/studysync
```

#### Docker 部署

后端通过 Docker 网络连接到 PostgreSQL 容器，连接字符串：
```
postgresql://postgres:password@learnpgsql:5432/studysync
```

### 如果 Docker 部署时无法连接数据库

如果您的 PostgreSQL 容器不在默认 Docker 网络中，您需要：

1. **方式一：让后端容器加入 PostgreSQL 所在的网络**
   ```bash
   # 找到 PostgreSQL 容器所在的网络
   docker inspect learnpgsql | grep NetworkMode
   
   # 假设网络名为 my_network
   docker network connect my_network studysync-backend
   ```

2. **方式二：使用 host.docker.internal 访问（仅限 macOS/Windows）**
   
   修改 `docker-compose.yml` 中的环境变量：
   ```yaml
   environment:
     DATABASE_URL: postgresql://postgres:password@host.docker.internal:5432/studysync
   ```

3. **方式三：使用 host 网络模式（Linux）**
   
   修改 `docker-compose.yml`：
   ```yaml
   services:
     backend:
       network_mode: host
       environment:
         DATABASE_URL: postgresql://postgres:password@localhost:5432/studysync
   ```

## 快速开始

### 方式一：本地开发（推荐，使用 Anaconda）

#### 1. 确保 PostgreSQL 容器正在运行

```bash
docker ps | grep learnpgsql
```

如果未运行，启动容器：
```bash
docker start learnpgsql
```

#### 2. 激活 Anaconda 环境

```bash
conda activate <your-env-name>
```

#### 3. 安装依赖（如果还没安装）

```bash
pip install -r requirements.txt
```

#### 4. 初始化数据库

```bash
cd app
python init_db.py
```

初始化完成后会创建默认管理员账号：
- 用户名: `admin`
- 密码: `admin123`

#### 5. 启动后端服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后：
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

### 方式二：使用 Docker Compose（备选）

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 配置数据库连接

修改 `.env` 文件：
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/studysync
SECRET_KEY=your-secret-key-change-in-production
```

注意：本地开发时使用 `localhost`，Docker 部署时容器间通信使用 `learnpgsql`。

#### 初始化数据库

```bash
cd app
python init_db.py
```

#### 启动后端服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 接口

### 认证模块
- POST `/api/auth/register` - 用户注册
- POST `/api/auth/login` - 用户登录

### 用户模块
- GET `/api/users/me` - 获取当前用户信息
- POST `/api/users/api_key` - 创建 API Key（用于 n8n）

### 计划模块
- POST `/api/plans` - 创建学习计划
- GET `/api/plans` - 获取计划列表
- PUT `/api/plans/{plan_id}` - 更新计划
- DELETE `/api/plans/{plan_id}` - 删除计划

### 打卡模块
- POST `/api/checkins` - 提交打卡
- GET `/api/checkins` - 查询打卡记录
- GET `/api/checkins/today` - 获取今日打卡状态
- GET `/api/checkins/stats` - 获取学习统计数据

### 群组模块
- POST `/api/groups` - 创建群组
- POST `/api/groups/{group_id}/join` - 加入群组
- POST `/api/groups/{group_id}/leave` - 退出群组
- GET `/api/groups` - 获取群组列表
- GET `/api/groups/{group_id}/members` - 获取群组成员
- DELETE `/api/groups/{group_id}/members/{user_id}` - 移除成员（供 n8n 调用）
- GET `/api/groups/{group_id}/checkins` - 获取群组打卡概览

### AI 模块
- GET `/api/ai/weekly_report` - 获取本周 AI 学习分析
- POST `/api/ai/generate_report` - 生成 AI 报告（供 n8n 调用）

## 环境变量

在 `.env` 文件中配置以下变量：

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/studysync
SECRET_KEY=your-secret-key-change-in-production
```

**注意**：
- 本地开发（Anaconda 环境）：使用 `localhost` 连接
- Docker 部署：`docker-compose.yml` 中配置为 `learnpgsql`（容器名）

## 数据库表结构

- `users` - 用户表
- `roles` - 角色表
- `user_roles` - 用户角色关联表
- `plans` - 学习计划表
- `checkins` - 打卡记录表
- `groups` - 学习群组表
- `group_members` - 群组成员表
- `ai_weekly_reports` - AI 周报表
- `api_keys` - API Key 表

## 开发注意事项

1. **API 认证**：大部分接口需要在请求头中携带 JWT Token
   ```
   Authorization: Bearer {access_token}
   ```

2. **n8n 自动化接口**：部分接口（如移除成员、生成 AI 报告）使用 API Key 认证
   ```
   Authorization: Bearer {api_key}
   ```

3. **数据库初始化**：首次运行需要执行 `init_db.py` 创建默认管理员账号

4. **热重载**：使用 `--reload` 参数启动，代码修改会自动重启服务

5. **调试**：在 VS Code 中可以使用调试器，配置 `.vscode/launch.json`：

   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: FastAPI",
         "type": "python",
         "request": "launch",
         "module": "uvicorn",
         "args": ["app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
       }
     ]
   }
   ```

## 常见问题

### 无法连接数据库

检查 PostgreSQL 容器是否运行：
```bash
docker ps | grep learnpgsql
```

测试数据库连接（本地）：
```bash
# 检查端口是否开放
netstat -an | grep 5432

# 或使用 psql 测试
psql -h localhost -U postgres -d studysync
```

### CORS 错误

检查 `main.py` 中的 CORS 配置，确保包含前端地址

### Token 过期

默认 Token 有效期为 7 天，过期后需要重新登录

### 端口被占用

如果 8000 端口被占用，修改启动命令使用其他端口：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 查看日志

```bash
# 查看数据库日志
docker logs learnpgsql -f
```

### 重启数据库

```bash
docker restart learnpgsql
```

检查网络连接：
```bash
# 进入后端容器测试连接
docker exec -it studysync-backend ping learnpgsql
```

### CORS 错误

检查 `main.py` 中的 CORS 配置，确保包含前端地址

### Token 过期

默认 Token 有效期为 7 天，过期后需要重新登录

### 查看容器日志

```bash
# 查看后端日志
docker logs studysync-backend -f

# 查看数据库日志
docker logs learnpgsql -f
```

## 许可证

MIT License
