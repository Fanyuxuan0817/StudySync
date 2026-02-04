# StudySync API 接口文档

## 基础信息

**Base URL**: `http://localhost:8000/api`

**认证方式**: Bearer Token (JWT)

**请求格式**: JSON

**响应格式**: JSON

---

## 通用响应格式

### 成功响应
```jsonA
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "error message",
  "detail": "detailed error info"
}
```

---

## 一、用户认证模块

### 1.1 用户注册

**接口地址**: `POST /auth/register`

**请求参数**:
```json
{
  "username": "string (必填, 3-20字符)",
  "email": "string (必填, 邮箱格式)",
  "password": "string (必填, 6-20字符)"
}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "user_id": "integer",
    "username": "string",
    "email": "string",
    "created_at": "datetime"
  }
}
```

---

### 1.2 用户登录

**接口地址**: `POST /auth/login`

**请求参数**:
```json
{
  "username": "string (必填)",
  "password": "string (必填)"
}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "string",
    "token_type": "bearer",
    "user": {
      "user_id": "integer",
      "username": "string",
      "email": "string"
    }
  }
}
```

---

### 1.3 获取当前用户信息

**接口地址**: `GET /users/me`

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_id": "integer",
    "username": "string",
    "email": "string",
    "created_at": "datetime",
    "avatar": "string (可选)"
  }
}
```

---

## 二、学习计划模块

### 2.1 创建学习计划

**接口地址**: `POST /plans`

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "title": "string (必填, 计划标题)",
  "description": "string (可选, 计划描述)",
  "daily_goal_hours": "float (必填, 每日目标小时数, 最小0.1)",
  "start_date": "string (必填, YYYY-MM-DD格式)",
  "end_date": "string (可选, YYYY-MM-DD格式)"
}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "计划创建成功",
  "data": {
    "plan_id": "integer",
    "user_id": "integer",
    "title": "string",
    "description": "string",
    "daily_goal_hours": "float",
    "start_date": "date",
    "end_date": "date (可选)",
    "status": "active",
    "created_at": "datetime"
  }
}
```

---

### 2.2 获取我的学习计划列表

**接口地址**: `GET /plans`

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
- `status`: string (可选) - 计划状态: `active`, `completed`, `archived`
- `page`: integer (可选, 默认1) - 页码
- `page_size`: integer (可选, 默认20) - 每页数量

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": "integer",
    "page": "integer",
    "page_size": "integer",
    "items": [
      {
        "plan_id": "integer",
        "title": "string",
        "description": "string",
        "daily_goal_hours": "float",
        "start_date": "date",
        "end_date": "date (可选)",
        "status": "string",
        "created_at": "datetime",
        "progress": {
          "total_hours": "float",
          "completion_rate": "float"
        }
      }
    ]
  }
}
```

---

### 2.3 更新学习计划

**接口地址**: `PUT /plans/{plan_id}`

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `plan_id`: integer - 计划ID

**请求参数**:
```json
{
  "title": "string (可选)",
  "description": "string (可选)",
  "daily_goal_hours": "float (可选)",
  "end_date": "string (可选, YYYY-MM-DD格式)",
  "status": "string (可选, active/completed/archived)"
}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "计划更新成功",
  "data": {
    "plan_id": "integer",
    "title": "string",
    "description": "string",
    "daily_goal_hours": "float",
    "start_date": "date",
    "end_date": "date",
    "status": "string",
    "updated_at": "datetime"
  }
}
```

---

### 2.4 删除学习计划

**接口地址**: `DELETE /plans/{plan_id}`

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `plan_id`: integer - 计划ID

**响应数据**:
```json
{
  "code": 200,
  "message": "计划删除成功",
  "data": null
}
```

---

## 三、打卡记录模块

### 3.1 提交打卡

**接口地址**: `POST /checkins`

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "plan_id": "integer (必填, 计划ID)",
  "hours": "float (必填, 学习时长小时数, 最小0.1)",
  "content": "string (必填, 学习内容)",
  "date": "string (可选, YYYY-MM-DD格式, 默认今天)"
}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "打卡成功",
  "data": {
    "checkin_id": "integer",
    "user_id": "integer",
    "plan_id": "integer",
    "hours": "float",
    "content": "string",
    "date": "date",
    "created_at": "datetime"
  }
}
```

---

### 3.2 查询打卡记录

**接口地址**: `GET /checkins`

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
- `plan_id`: integer (可选) - 计划ID
- `date`: string (可选) - 日期 YYYY-MM-DD 格式
- `start_date`: string (可选) - 开始日期 YYYY-MM-DD 格式
- `end_date`: string (可选) - 结束日期 YYYY-MM-DD 格式
- `page`: integer (可选, 默认1) - 页码
- `page_size`: integer (可选, 默认20) - 每页数量

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": "integer",
    "page": "integer",
    "page_size": "integer",
    "items": [
      {
        "checkin_id": "integer",
        "user_id": "integer",
        "plan_id": "integer",
        "plan_title": "string",
        "hours": "float",
        "content": "string",
        "date": "date",
        "created_at": "datetime"
      }
    ]
  }
}
```

---

### 3.3 获取今日打卡状态

**接口地址**: `GET /checkins/today`

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "date": "date",
    "checked_in": "boolean",
    "total_hours": "float",
    "checkins": [
      {
        "checkin_id": "integer",
        "plan_id": "integer",
        "plan_title": "string",
        "hours": "float",
        "content": "string",
        "created_at": "datetime"
      }
    ]
  }
}
```

---

### 3.4 获取学习统计数据

**接口地址**: `GET /checkins/stats`

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
- `period`: string (可选, 默认week) - 统计周期: `week`, `month`, `year`
- `plan_id`: integer (可选) - 计划ID

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "period": "string",
    "total_hours": "float",
    "total_days": "integer",
    "checkin_count": "integer",
    "avg_hours_per_day": "float",
    "checkin_rate": "float",
    "daily_stats": [
      {
        "date": "date",
        "hours": "float",
        "checkin_count": "integer"
      }
    ]
  }
}
```

---

## 四、学习群组模块

### 4.1 创建学习群组

**接口地址**: `POST /groups`

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求参数**:
```json
{
  "name": "string (必填, 群组名称)",
  "description": "string (可选, 群组描述)",
  "daily_checkin_rule": {
    "min_checkins_per_day": "integer (必填, 每日最少打卡次数, 默认1)"
  },
  "auto_remove_days": "integer (可选, 超过未打卡天数自动移出, 默认3)"
}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "群组创建成功",
  "data": {
    "group_id": "integer",
    "name": "string",
    "description": "string",
    "creator_id": "integer",
    "daily_checkin_rule": {
      "min_checkins_per_day": "integer"
    },
    "auto_remove_days": "integer",
    "member_count": "integer",
    "created_at": "datetime"
  }
}
```

---

### 4.2 加入学习群组

**接口地址**: `POST /groups/{group_id}/join`

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `group_id`: integer - 群组ID

**响应数据**:
```json
{
  "code": 200,
  "message": "成功加入群组",
  "data": {
    "group_id": "integer",
    "user_id": "integer",
    "joined_at": "datetime",
    "role": "member"
  }
}
```

---

### 4.3 退出学习群组

**接口地址**: `POST /groups/{group_id}/leave`

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `group_id`: integer - 群组ID

**响应数据**:
```json
{
  "code": 200,
  "message": "已退出群组",
  "data": null
}
```

---

### 4.4 获取我的群组列表

**接口地址**: `GET /groups`

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "created": [
      {
        "group_id": "integer",
        "name": "string",
        "description": "string",
        "member_count": "integer",
        "created_at": "datetime"
      }
    ],
    "joined": [
      {
        "group_id": "integer",
        "name": "string",
        "description": "string",
        "member_count": "integer",
        "joined_at": "datetime"
      }
    ]
  }
}
```

---

### 4.5 获取群组成员列表

**接口地址**: `GET /groups/{group_id}/members`

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `group_id`: integer - 群组ID

**查询参数**:
- `status`: string (可选) - 成员状态: `active`, `inactive`

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "group_id": "integer",
    "name": "string",
    "total_members": "integer",
    "members": [
      {
        "user_id": "integer",
        "username": "string",
        "avatar": "string (可选)",
        "role": "string (creator/admin/member)",
        "joined_at": "datetime",
        "last_checkin_date": "date (可选)",
        "days_without_checkin": "integer"
      }
    ]
  }
}
```

---

### 4.6 移除群组成员 (供n8n自动化调用)

**接口地址**: `DELETE /groups/{group_id}/members/{user_id}`

**请求头**:
```
Authorization: Bearer {api_key}
```

**路径参数**:
- `group_id`: integer - 群组ID
- `user_id`: integer - 用户ID

**响应数据**:
```json
{
  "code": 200,
  "message": "成员已移出群组",
  "data": {
    "group_id": "integer",
    "user_id": "integer",
    "removed_at": "datetime"
  }
}
```

---

### 4.7 获取群组打卡概览

**接口地址**: `GET /groups/{group_id}/checkins`

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `group_id`: integer - 群组ID

**查询参数**:
- `date`: string (可选) - 日期 YYYY-MM-DD 格式

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "group_id": "integer",
    "date": "date",
    "total_members": "integer",
    "checked_in_count": "integer",
    "not_checked_in_count": "integer",
    "checked_in": [
      {
        "user_id": "integer",
        "username": "string",
        "hours": "float",
        "checkin_time": "datetime"
      }
    ],
    "not_checked_in": [
      {
        "user_id": "integer",
        "username": "string"
      }
    ]
  }
}
```

---

## 五、AI 学习评估模块

### 5.1 获取本周 AI 学习分析报告

**接口地址**: `GET /ai/weekly_report`

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
- `week_date`: string (可选) - 周日期 YYYY-MM-DD 格式, 默认本周

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "week_start": "date",
    "week_end": "date",
    "generated_at": "datetime",
    "score": {
      "total": "integer (0-100)",
      "frequency": "integer (打卡频率得分)",
      "duration": "integer (学习时长得分)",
      "stability": "integer (学习稳定性得分)"
    },
    "summary": {
      "checkin_frequency": "string (打卡频率描述)",
      "learning_trend": "string (学习时长趋势描述)",
      "stability_level": "string (学习稳定性描述)"
    },
    "issues": [
      "string (本周学习问题点)"
    ],
    "suggestions": [
      "string (改进建议)"
    ],
    "recommended_hours": "float (建议每日学习小时数)"
  }
}
```

---

### 5.2 触发 AI 报告生成 (供n8n调用)

**接口地址**: `POST /ai/generate_report`

**请求头**:
```
Authorization: Bearer {api_key}
```

**请求参数**:
```json
{
  "user_id": "integer (必填)",
  "week_start": "string (必填, YYYY-MM-DD格式)",
  "week_end": "string (必填, YYYY-MM-DD格式)"
}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "AI报告生成中",
  "data": {
    "task_id": "string",
    "status": "processing",
    "estimated_time": "integer (秒)"
  }
}
```

---

## 六、错误码说明

| 错误码 | 说明 |
|-------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 / Token 无效 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突 (如用户名已存在) |
| 422 | 数据验证失败 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

---

## 七、API 调用示例

### 7.1 用户注册流程

```bash
# 1. 注册用户
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"123456"}'

# 2. 登录获取 Token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"123456"}'

# 3. 使用 Token 获取用户信息
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer {access_token}"
```

### 7.2 打卡流程示例

```bash
# 1. 创建学习计划
curl -X POST http://localhost:8000/api/plans \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"title":"学习Python","description":"每天学习2小时","daily_goal_hours":2,"start_date":"2026-02-04"}'

# 2. 提交打卡
curl -X POST http://localhost:8000/api/checkins \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"plan_id":1,"hours":2,"content":"学习了Python基础语法"}'

# 3. 查看今日打卡
curl -X GET http://localhost:8000/api/checkins/today \
  -H "Authorization: Bearer {access_token}"
```

---

## 八、n8n 自动化接口

### 8.1 自动化 API Key 获取

**接口地址**: `POST /admin/api_key`

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "api_key": "string",
    "created_at": "datetime"
  }
}
```

---

## 更新日志

### v1.0.0 (2026-02-04)
- 初始版本
- 实现用户认证模块
- 实现学习计划模块
- 实现打卡记录模块
- 实现学习群组模块
- 实现 AI 学习评估模块
