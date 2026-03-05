---
name: api-docs
description: 根据后端代码和API设计自动生成API文档。支持Swagger/OpenAPI 3.0格式，生成交互式文档、SDK客户端代码、Postman Collection。适用于API文档生成、接口对接、前后端协作。当用户提到"API文档"、"接口文档"、"Swagger"、"OpenAPI"、"api docs"时触发。
---

# API 文档生成器

## Overview

```
1. 分析后端代码，提取 API 端点信息
2. 生成 OpenAPI 3.0 规范（openapi.yaml）
3. 生成交互式文档（Swagger UI / ReDoc）
4. 生成 Postman Collection
5. 生成 TypeScript SDK（可选）
6. 生成文档概览 README.md
```

## 支持框架

| 框架 | 支持情况 |
|------|---------|
| Fastify (Node.js) | ✅ 原生 schema 注解 |
| NestJS (Node.js) | ✅ @nestjs/swagger 装饰器 |
| Express (Node.js) | ✅ JSDoc 注解 |
| FastAPI (Python) | ✅ 原生支持 |
| Spring Boot (Java) | ✅ SpringDoc |
| Gin (Go) | ✅ Swaggo |

---

## Step 1: 分析 API 设计

```bash
cat TechSolution/backend/api-design.md
# 扫描 backend/src/modules/ 下的 controller/routes/dto 文件
```

提取信息：

| 信息 | 说明 |
|------|------|
| 端点路径 | `/api/users`, `/api/sessions/:id` |
| HTTP 方法 | GET, POST, PUT, DELETE, PATCH |
| 请求参数 | Query, Path, Body, Header |
| 响应格式 | 200/400/401/403/404/500 |
| 数据模型 | Request/Response DTO / Prisma Schema |
| 认证方式 | Bearer Token, API Key |

---

## Step 2: 生成 OpenAPI 规范

完整 OpenAPI 3.0 YAML 示例、Prisma Schema → OpenAPI 转换规则、Fastify/NestJS 代码注解规范见：[references/openapi-examples.md](references/openapi-examples.md)

输出 `api-docs/openapi.yaml`，基础结构：

```yaml
openapi: 3.0.0
info:
  title: {项目名} API
  version: 1.0.0
servers:
  - url: https://api.example.com/v1
  - url: http://localhost:3000/v1
security:
  - BearerAuth: []
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

## Step 3: 生成交互式文档

**Swagger UI** (`api-docs/index.html`):
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>API 文档</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: './openapi.yaml',
      dom_id: '#swagger-ui',
      deepLinking: true,
      tryItOutEnabled: true,
      persistAuthorization: true,
    });
  </script>
</body>
</html>
```

**ReDoc** (`api-docs/redoc.html`):
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>API 文档</title>
</head>
<body>
  <redoc spec-url='./openapi.yaml'></redoc>
  <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
</body>
</html>
```

---

## Step 4: 生成 Postman Collection

输出 `api-docs/postman_collection.json`，结构：

```json
{
  "info": { "name": "{项目} API", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json" },
  "variable": [
    { "key": "baseUrl", "value": "http://localhost:3000/v1" },
    { "key": "token", "value": "" }
  ],
  "auth": { "type": "bearer", "bearer": [{ "key": "token", "value": "{{token}}" }] },
  "item": [
    {
      "name": "Auth",
      "item": [{ "name": "Login", "request": { "method": "POST", "url": "{{baseUrl}}/auth/login" } }]
    }
  ]
}
```

---

## Step 5: 生成 TypeScript SDK（可选）

输出 `api-docs/sdk/typescript/src/client.ts`：

```typescript
export class ApiClient {
  constructor(private baseUrl: string, private token?: string) {}

  setToken(token: string) { this.token = token; }

  private async request<T>(method: string, path: string, body?: any): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) throw new ApiError(res.status, await res.json());
    return res.json();
  }

  async login(data: { email: string; password: string }) {
    return this.request<{ accessToken: string; refreshToken: string }>('POST', '/auth/login', data);
  }
  // 按照 openapi.yaml 继续添加各个端点方法...
}

export class ApiError extends Error {
  constructor(public status: number, public data: any) { super(data.message); }
}
```

---

## Step 6: 生成文档概览 README.md

输出 `api-docs/README.md`，包含：
- **Base URL** + 认证方式（Bearer Token 示例）
- **API 端点总览表**：模块 / 路径 / 方法 / 描述
- **错误格式**：统一 `{ code, message, details }` + HTTP 状态码表
- **快速开始**：登录获取 Token → 使用 Token 的 curl 示例
- **在线文档**链接（Swagger UI / ReDoc）
- **Postman Collection** 下载链接

---

## Output

```
api-docs/
├── README.md                  # 文档概览
├── openapi.yaml               # OpenAPI 规范
├── index.html                 # Swagger UI
├── redoc.html                 # ReDoc
├── postman_collection.json    # Postman Collection
└── sdk/typescript/            # TypeScript SDK（可选）
```
