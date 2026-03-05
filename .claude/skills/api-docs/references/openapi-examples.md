# OpenAPI 3.0 完整示例

## 基础结构

```yaml
openapi: 3.0.0
info:
  title: 智能客服系统 API
  version: 1.0.0
  description: |
    ## 认证方式
    所有 API 需要使用 Bearer Token 认证

servers:
  - url: https://api.example.com/v1
    description: 生产环境
  - url: http://localhost:3000/v1
    description: 开发环境

security:
  - BearerAuth: []

tags:
  - name: Auth
    description: 认证授权
  - name: Sessions
    description: 会话管理

paths:
  /auth/login:
    post:
      tags: [Auth]
      summary: 用户登录
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
            example:
              email: "user@example.com"
              password: "password123"
      responses:
        '200':
          description: 登录成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'
        '401':
          description: 认证失败
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /sessions:
    post:
      tags: [Sessions]
      summary: 创建会话
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateSessionRequest'
      responses:
        '201':
          description: 创建成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SessionResponse'

    get:
      tags: [Sessions]
      summary: 获取会话列表
      parameters:
        - name: page
          in: query
          schema: { type: integer, default: 1 }
        - name: limit
          in: query
          schema: { type: integer, default: 20 }
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/SessionResponse'
                  pagination:
                    $ref: '#/components/schemas/Pagination'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    LoginRequest:
      type: object
      required: [email, password]
      properties:
        email:
          type: string
          format: email
        password:
          type: string
          format: password
          minLength: 8

    LoginResponse:
      type: object
      properties:
        accessToken:
          type: string
        refreshToken:
          type: string
        user:
          $ref: '#/components/schemas/User'

    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
        role:
          type: string
          enum: [USER, AGENT, ADMIN]
      required: [id, email, role]

    ErrorResponse:
      type: object
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: object

    Pagination:
      type: object
      properties:
        page: { type: integer }
        limit: { type: integer }
        total: { type: integer }
        totalPages: { type: integer }
```

## Prisma → OpenAPI 转换示例

```typescript
// Prisma Schema
model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String?
  role      Role     @default(USER)
  createdAt DateTime @default(now())
}

// 对应 OpenAPI Schema
// User:
//   type: object
//   properties:
//     id: { type: string, format: uuid }
//     email: { type: string, format: email }
//     name: { type: string, nullable: true }
//     role: { type: string, enum: [USER, AGENT, ADMIN] }
//     createdAt: { type: string, format: date-time }
//   required: [id, email, role, createdAt]
```

## 代码注解规范

### Fastify

```typescript
app.post('/sessions', {
  schema: {
    tags: ['Sessions'],
    summary: '创建会话',
    security: [{ bearerAuth: [] }],
    body: {
      type: 'object',
      required: ['userId'],
      properties: {
        userId: { type: 'string', format: 'uuid' }
      }
    },
    response: {
      201: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          userId: { type: 'string' },
          status: { type: 'string' },
          createdAt: { type: 'string', format: 'date-time' }
        }
      }
    }
  }
}, handler)
```

### NestJS

```typescript
import { ApiProperty, ApiTags } from '@nestjs/swagger';

@ApiTags('Sessions')
export class CreateSessionDto {
  @ApiProperty({ description: '用户 ID', format: 'uuid' })
  @IsUUID()
  userId: string;
}
```
