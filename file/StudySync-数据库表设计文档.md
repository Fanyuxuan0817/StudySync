# **StudySync 数据库设计（V1）**

## **1️⃣ 用户相关表**

### **users** — 用户基本信息

| 字段名           | 类型           | 约束/说明      |
| ------------- | ------------ | ---------- |
| id            | BIGSERIAL    | 主键         |
| username      | VARCHAR(50)  | 唯一，用户登录名   |
| email         | VARCHAR(100) | 唯一，可为空     |
| password_hash | VARCHAR(256) | 密码哈希       |
| avatar_url    | VARCHAR(256) | 可选头像       |
| created_at    | TIMESTAMP    | 默认 `NOW()` |
| updated_at    | TIMESTAMP    | 默认 `NOW()` |

---

### **roles** — 用户角色表

| 字段名         | 类型          | 约束/说明                |
| ----------- | ----------- | -------------------- |
| id          | SERIAL      | 主键                   |
| name        | VARCHAR(50) | 角色名称（如 admin / user） |
| description | TEXT        | 可选描述                 |

---

### **user_roles** — 用户角色关联表（多对多）

| 字段名                           | 类型     | 约束/说明          |
| ----------------------------- | ------ | -------------- |
| user_id                       | BIGINT | 外键 → users(id) |
| role_id                       | INT    | 外键 → roles(id) |
| PRIMARY KEY(user_id, role_id) |        |                |

> 说明：便于扩展权限管理，V1 可默认每个用户只有普通角色 `user`。

---

## **2️⃣ 学习计划相关**

### **plans** — 用户学习计划

| 字段名            | 类型           | 约束/说明                  |
| -------------- | ------------ | ---------------------- |
| id             | BIGSERIAL    | 主键                     |
| user_id        | BIGINT       | 外键 → users(id)         |
| title          | VARCHAR(100) | 计划标题，如 "每天学 Python 2h" |
| description    | TEXT         | 可选                     |
| daily_goal_min | INT          | 每日目标时长（分钟）             |
| start_date     | DATE         | 开始日期                   |
| end_date       | DATE         | 可选结束日期                 |
| created_at     | TIMESTAMP    | 默认 NOW()               |
| updated_at     | TIMESTAMP    | 默认 NOW()               |

---

## **3️⃣ 打卡相关**

### **checkins** — 用户每日打卡记录

| 字段名          | 类型        | 约束/说明          |
| ------------ | --------- | -------------- |
| id           | BIGSERIAL | 主键             |
| user_id      | BIGINT    | 外键 → users(id) |
| plan_id      | BIGINT    | 外键 → plans(id) |
| checkin_date | DATE      | 打卡日期           |
| duration_min | INT       | 实际学习时长（分钟）     |
| content      | TEXT      | 学习内容/笔记        |
| created_at   | TIMESTAMP | 默认 NOW()       |

> 约束：`UNIQUE(user_id, plan_id, checkin_date)` 防止重复打卡。

---

## **4️⃣ 群组相关**

### **groups** — 学习群组

| 字段名                    | 类型           | 约束/说明              |
| ---------------------- | ------------ | ------------------ |
| id                     | BIGSERIAL    | 主键                 |
| name                   | VARCHAR(100) | 群组名称               |
| description            | TEXT         | 可选描述               |
| daily_checkin_required | BOOLEAN      | 是否要求每日打卡           |
| created_by             | BIGINT       | 外键 → users(id) 创建者 |
| created_at             | TIMESTAMP    | 默认 NOW()           |
| updated_at             | TIMESTAMP    | 默认 NOW()           |

---

### **group_members** — 群组成员

| 字段名                            | 类型          | 约束/说明                |
| ------------------------------ | ----------- | -------------------- |
| group_id                       | BIGINT      | 外键 → groups(id)      |
| user_id                        | BIGINT      | 外键 → users(id)       |
| joined_at                      | TIMESTAMP   | 默认 NOW()             |
| last_checkin                   | DATE        | 上一次打卡日期，用于 n8n 自动踢人  |
| role                           | VARCHAR(20) | 群组角色（owner / member） |
| PRIMARY KEY(group_id, user_id) |             |                      |

---

## **5️⃣ AI 学习分析**

### **ai_weekly_reports** — AI 每周学习报告

| 字段名         | 类型        | 约束/说明          |
| ----------- | --------- | -------------- |
| id          | BIGSERIAL | 主键             |
| user_id     | BIGINT    | 外键 → users(id) |
| week_start  | DATE      | 周报起始日期         |
| week_end    | DATE      | 周报结束日期         |
| score       | INT       | 本周学习强度评分 0-100 |
| summary     | TEXT      | 问题总结           |
| suggestions | TEXT      | 改进建议           |
| created_at  | TIMESTAMP | 默认 NOW()       |

> 可扩展：未来可以添加群组周报表 `group_weekly_reports`。

---

## **6️⃣ API Key / 自动化安全**

### **api_keys** — n8n 调用后端 API 的密钥表

| 字段名         | 类型           | 约束/说明      |
| ----------- | ------------ | ---------- |
| id          | BIGSERIAL    | 主键         |
| key         | VARCHAR(128) | 唯一 API Key |
| description | TEXT         | 说明用途       |
| created_at  | TIMESTAMP    | 默认 NOW()   |
| expires_at  | TIMESTAMP    | 可选过期时间     |
| is_active   | BOOLEAN      | 是否启用       |

---

## **7️⃣ 数据库关系概览**

```
users ──< plans
users ──< checkins
users ──< group_members >── groups
users ──< ai_weekly_reports
users ──< user_roles >── roles
groups ──< group_members
api_keys (独立表，用于 n8n)
```

---

## ✅ **设计说明**

1. **角色/权限**：`roles` + `user_roles` 可扩展到 admin、超级用户、群主等权限。
2. **群组踢人**：`group_members.last_checkin` 用于 n8n 自动判断超过 3 天未打卡的用户。
3. **AI 周报**：`ai_weekly_reports` 可存储文本分析结果，也可扩展 JSON 字段存储更多 AI 数据。
4. **扩展性**：未来可加：

   * 群组周报
   * 用户消息表（聊天功能）
   * 标签/主题分类（学习计划分类）
5. **数据完整性**：外键、唯一约束、防止重复打卡。


