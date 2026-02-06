# StudySync

## 项目简介

StudySync 是一个学习管理应用：
- **前端**: Vue 3 + Vite
- **后端**: FastAPI + PostgreSQL
- **AI 服务**: DeepSeek API

---

## 快速部署（Docker Compose）

### 1. 安装 Docker

确保已安装 Docker 和 Docker Compose：

```bash
docker --version
docker-compose --version
```

### 2. 创建部署文件

在项目根目录创建以下文件：

**backend/Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
WORKDIR /app/app

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**frontend/Dockerfile**

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**frontend/nginx.conf**

```nginx
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
```

**docker-compose.yml**（项目根目录）

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
      POSTGRES_DB: studysync
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    environment:
      DB_HOST: db
      DB_PORT: 5432
      DB_USER: postgres
      DB_PASSWORD: postgres123
      DB_NAME: studysync
      SECRET_KEY: your-secret-key-here
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
DEEPSEEK_API_KEY=your-deepseek-api-key
```

### 4. 启动服务

```bash
# 构建并启动
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 5. 访问应用

- 前端: http://localhost
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

## 开发环境部署

### 后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cd app
python init_db.py
uvicorn main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 端口被占用 | 修改 `docker-compose.yml` 中的端口映射 |
| 数据库连接失败 | 等待数据库健康检查通过 |
| 构建失败 | 执行 `docker-compose build --no-cache` |

---

**注意**: 生产环境请修改默认密码和密钥。
