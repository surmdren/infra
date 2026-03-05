---
name: api-test-generator
description: 生成单个 API 端点的集成测试代码。调用真实接口，禁止使用任何 Mock。每个接口 2-5 个测试用例，覆盖 Happy Path、参数校验、鉴权/权限校验。适用于测试 API 端点的各种场景。
---

# API Test Generator

**核心原则**：调用真实接口，禁止 Mock；每接口 2-5 个测试用例；稳定、可重复、执行快速。

## 输入要求

| 必需信息 | 说明 | 示例 |
|----------|------|------|
| 接口定义 | 路由、方法、参数、响应 | `POST /api/orders` |
| 技术栈 | 语言和框架 | Python + FastAPI |
| 环境配置 | 测试环境地址 | `http://localhost:8000` |
| 鉴权方式 | 如何获取测试 Token | Bearer Token |

---

## 每个接口必须覆盖

1. **Happy Path**：有效参数 → 验证状态码 + 响应数据结构
2. **参数校验**：缺失必填、类型错误、边界值 → 400/422
3. **鉴权/权限**：无 Token → 401；无效 Token → 401；无权限 → 403
4. **业务边界**（按需）：不存在 → 404；幂等性验证

---

## 代码模板

见 [references/api-test-templates.md](references/api-test-templates.md)：Python (pytest+httpx)、Node.js (Vitest+supertest)、Go (testing+testify)、Java (JUnit5+REST Assured) 模板 + 数据清理策略示例。

---

## 数据策略

- **隔离性**：每个测试负责自己的数据准备和清理
- **唯一性**：UUID 或时间戳生成唯一 ID，避免冲突
- **独立性**：测试之间无数据依赖和执行顺序依赖

---

## 目录结构

| 检测条件 | 目录前缀 |
|----------|----------|
| 路径含 `backend/` / `api/` / `services/` | `tests/backend/api` |
| 路径含 `frontend/` / `web/` | `tests/frontend/api` |
| 根目录直接有 `src/` | `tests/api` |

测试文件：`tests/{type}/api/test_{resource}_api.py`
测试报告：`test_reports/{type}/api_test_reports/{resource}_api_test_report.md`

## 文件命名

| 语言 | backend | 默认 |
|------|---------|------|
| Python | `tests/backend/api/test_{resource}_api.py` | `tests/api/test_{resource}_api.py` |
| Node.js | `tests/backend/api/{resource}.api.test.ts` | `tests/api/{resource}.api.test.ts` |
| Go | `tests/backend/api/{resource}_api_test.go` | `tests/api/{resource}_api_test.go` |
| Java | `src/test/java/.../api/{Resource}ApiTest.java` | 同左 |

## 运行命令

```bash
pytest tests/api/test_orders_api.py -v  # Python
pnpm test tests/api/orders.api.test.ts  # Node.js
go test ./tests/api/... -v              # Go
mvn test -Dtest=OrdersApiTest           # Java
```

---

## 严格禁止

- ❌ 任何 Mock（数据库、HTTP、服务）
- ❌ 绕过鉴权测试
- ❌ 单接口超过 6 个测试用例
- ❌ 测试之间数据依赖
- ❌ sleep / 固定等待
- ❌ 硬编码敏感信息（Token、密码）

## 成功标准

- [ ] 覆盖 Happy Path
- [ ] 覆盖参数校验错误
- [ ] 覆盖鉴权/权限校验
- [ ] 无 Mock
- [ ] 测试数据有清理策略
- [ ] 可独立运行，不依赖其他测试
