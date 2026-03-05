---
name: integration-test-generator
description: 生成多 API 组合的业务场景集成测试代码。测试多个 API 端点之间的协作，验证完整的业务流程。不涉及 UI，纯后端集成测试。禁止使用 Mock。适用于验证 API 间协作、业务流程集成、回归测试。当用户提到"集成测试"、"API流程测试"、"业务场景测试"、"多API测试"时触发。
---

# 集成测试生成器

测试层级：Unit Tests → API Tests → **Integration Tests** → E2E Tests

- **API 测试**：单个端点，多种场景
- **集成测试**：多个端点协作，完整业务流程（本 Skill）
- **E2E 测试**：含 UI 的用户旅程

---

## 核心原则

- **禁止 Mock**：调用真实 API 端点
- **业务流程**：测试完整 API 调用链（API1 → API2 → API3 → 验证）
- **数据清理**：每个测试自己准备和清理数据
- **每流程 2-4 个测试用例**

## 输入要求

| 必需信息 | 示例 |
|----------|------|
| API 流程定义（按顺序） | `POST /users → POST /orders → POST /payments` |
| 技术栈 | Python + FastAPI |
| 测试环境地址 | `http://localhost:8000` |
| 鉴权方式 | Bearer Token |

---

## 流程设计模板

```
测试场景：{场景名称}
步骤：
1. {前置条件} - 调用 API A
2. {业务动作} - 调用 API B，使用 A 的返回值
3. {后续操作} - 调用 API C，使用 B 的返回值
4. {验证} - 验证最终状态

测试用例：
- 正常流程：所有步骤成功
- 边界条件：某步骤返回错误
```

---

## 代码模板

见 [references/integration-test-templates.md](references/integration-test-templates.md)：Python、Node.js、Go、Java 模板。

---

## 常见业务场景

```yaml
# 用户下单支付
流程: POST /users → POST /auth/login → POST /orders → POST /orders/{id}/pay
用例: 正常流程 / 库存不足 / 余额不足

# 商户配置商品
流程: POST /merchants → POST /merchants/{id}/products → PATCH /inventory/{id}
用例: 正常流程 / 商品已存在 / 库存为0时下单
```

---

## 目录结构

| 检测条件 | 目录前缀 |
|----------|----------|
| 路径含 `backend/` / `api/` | `tests/backend/integration` |
| 路径含 `frontend/` / `web/` | `tests/frontend/integration` |
| 根目录直接有 `src/` | `tests/integration` |

测试文件：`tests/{type}/integration/test_{scenario}_integration.py`
测试报告：`test_reports/{type}/integration_test_reports/{scenario}_integration_test_report.md`

## 文件命名

| 语言 | backend | 默认 |
|------|---------|------|
| Python | `tests/backend/integration/test_{scenario}_integration.py` | `tests/integration/test_{scenario}_integration.py` |
| Node.js | `tests/backend/integration/{scenario}.integration.test.ts` | `tests/integration/{scenario}.integration.test.ts` |
| Go | `tests/backend/integration/{scenario}_integration_test.go` | `tests/integration/{scenario}_integration_test.go` |
| Java | `src/test/java/.../integration/{Scenario}IntegrationTest.java` | 同左 |

## 运行命令

```bash
pytest tests/integration/test_{scenario}_integration.py -v  # Python
pnpm test tests/integration/{scenario}.integration.test.ts  # Node.js
go test ./tests/integration/... -v -run Test{ScenarioName}  # Go
mvn test -Dtest={ScenarioName}IntegrationTest               # Java
```

---

## 禁止事项

- ❌ 任何 Mock
- ❌ 跳过某个 API 调用
- ❌ 测试间数据依赖
- ❌ 硬编码敏感信息
- ❌ sleep / 固定等待

## 成功标准

- [ ] 覆盖完整业务流程 Happy Path
- [ ] 覆盖关键步骤失败场景
- [ ] 无 Mock
- [ ] 测试数据有清理策略
- [ ] 每流程 2-4 个测试用例
- [ ] 可独立运行
