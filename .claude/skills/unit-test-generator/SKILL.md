---
name: unit-test-generator
description: 生成单元测试代码。只测试高风险/复杂逻辑，允许使用 Mock 隔离外部依赖。测试执行快速（毫秒级）。适用于测试核心业务规则、状态流转、权限判断、复杂分支、数据转换、算法实现。
---

# Unit Test Generator

## 只为以下内容生成单元测试

| 类型 | 说明 | 示例 |
|------|------|------|
| 核心业务规则 | 涉及金额计算、业务判断 | 价格计算器、折扣规则 |
| 状态流转 | 状态机、工作流 | 订单状态、审批流程 |
| 权限判断 | 复杂的权限逻辑 | 角色权限、数据权限 |
| 复杂分支 | 3+ 个 if/switch 分支 | 条件处理、策略模式 |
| 数据转换 | 复杂的格式转换 | 数据映射、格式化 |
| 算法实现 | 自定义算法 | 排序、搜索、计算 |

## 禁止为以下生成

| 类型 | 原因 |
|------|------|
| 简单 CRUD | 由 API 测试覆盖 |
| getter/setter | 无业务逻辑 |
| 框架行为 | 框架自身已测试 |
| 纯数据库查询 | 由 API 测试覆盖 |
| 第三方库封装 | 信任第三方库 |

---

## Mock 规则

| 依赖类型 | Mock 方式 |
|----------|-----------|
| 数据库 | Mock Repository/DAO |
| 缓存 | Mock Cache Client |
| 消息队列 | Mock Producer/Consumer |
| 第三方 API | Mock HTTP Client |
| 时间 | Mock Clock/DateTime |

**原则**：只 Mock 外部依赖，不 Mock 被测对象本身。

```python
# ✅ 好：只 Mock 外部依赖
mock_repository.get_user.return_value = User(vip_level=2)
result = service.calculate_discount(user_id=1, amount=100)
assert result == 90

# ❌ 坏：Mock 了被测对象本身
mock_service.calculate.return_value = 90  # 这测试了什么？
```

---

## 代码模板

见 [references/unit-test-templates.md](references/unit-test-templates.md)：Python (pytest)、Node.js (Vitest)、Go (testing+testify)、Java (JUnit5+Mockito) 模板。

---

## 目录结构

| 检测条件 | 目录前缀 |
|----------|----------|
| 路径含 `backend/` / `api/` / `services/` | `tests/backend/unit` |
| 路径含 `frontend/` / `web/` / `ui/` | `tests/frontend/unit` |
| 根目录直接有 `src/` | `tests/unit` |

测试文件：`tests/{type}/unit/test_{module}.py`
测试报告：`test_reports/{type}/unit_test_reports/{module}_unit_test_report.md`

## 文件命名

| 语言 | backend | frontend | 默认 |
|------|---------|----------|------|
| Python | `tests/backend/unit/test_{module}.py` | `tests/frontend/unit/test_{module}.py` | `tests/unit/test_{module}.py` |
| Node.js | `tests/backend/unit/{module}.test.ts` | `tests/frontend/unit/{module}.test.ts` | `tests/unit/{module}.test.ts` |
| Go | `{module}_test.go` | - | `{module}_test.go` |
| Java | `src/test/java/.../{ClassName}Test.java` | - | 同左 |

## 运行命令

```bash
pytest tests/unit/test_{module}.py -v      # Python
pnpm test tests/unit/{module}.test.ts      # Node.js
go test ./{module}_test.go -v             # Go
mvn test -Dtest={ClassName}Test           # Java
```

---

## 严格禁止

- ❌ 为简单 CRUD / getter/setter 生成测试
- ❌ 在单元测试中调用真实数据库/API
- ❌ 测试执行时间超过 100ms
- ❌ 测试之间状态共享

## 成功标准

- [ ] 只测试了高风险/复杂逻辑
- [ ] 正确使用 Mock 隔离外部依赖
- [ ] 覆盖正常路径和关键边界条件
- [ ] 状态机覆盖所有有效/无效转换
- [ ] 单个测试执行 < 100ms
- [ ] 测试命名清晰表达目的
