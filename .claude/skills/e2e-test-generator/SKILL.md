---
name: e2e-test-generator
description: 生成端到端 E2E 测试代码。全局最多 1-2 条测试，只覆盖最关键的用户主流程。调用真实系统，禁止使用 Mock。使用 Playwright 进行浏览器自动化测试。适用于测试核心变现流程、核心业务流程、关键用户旅程。
---

# E2E Test Generator

## 核心约束：最多 1-2 条测试

| 优先级 | 流程类型 | 示例 |
|--------|----------|------|
| P0 | 核心变现流程 | 注册 → 浏览 → 加购 → 下单 → 支付 |
| P1 | 核心业务流程 | 创建项目 → 邀请成员 → 分配任务 |
| P1 | Geo 语言路由 | 首次访问 → IP 检测 → 自动重定向 |
| P2 | 关键用户旅程 | 登录 → 完善资料 → 首次使用核心功能 |

**不适合 E2E**：单页面功能测试、表单校验、边界条件、权限测试（改用 API 测试）。

---

## 编写原则

**1. 使用稳定选择器**

```typescript
await page.getByTestId('submit-button').click();        // ✅ data-testid
await page.getByRole('button', { name: '提交' }).click(); // ✅ role+name
await page.getByLabel('邮箱').fill('test@example.com');   // ✅ label
await page.click('.btn-primary-lg');                      // ❌ CSS 类名
```

**2. 禁止 sleep，使用显式等待**

```typescript
await page.waitForSelector('[data-testid="order-confirmation"]'); // ✅
await page.waitForURL('**/order/success');                         // ✅
await page.waitForTimeout(3000);                                   // ❌
```

**3. 测试数据隔离**

```typescript
const uniqueEmail = `test_${Date.now()}@example.com`;
test.afterEach(async ({ request }) => {
  await request.delete(`/api/test/cleanup/${testUserId}`);
});
```

**4. 测试独立**（不依赖其他测试状态，每个测试完成自己的前置步骤）

---

## 代码模板

见 [references/playwright-templates.md](references/playwright-templates.md)：TypeScript、Python、Java 模板 + playwright.config.ts + GitHub Actions CI。

---

## 目录结构

| 检测条件 | 目录前缀 |
|----------|----------|
| 路径含 `frontend/` / `web/` / `ui/` | `tests/frontend/e2e` |
| 路径含 `backend/` | `tests/backend/e2e` |
| 根目录直接有 `src/` | `tests/e2e` |

测试文件：`tests/{type}/e2e/{flow-name}.spec.ts`
测试报告：`test_reports/{type}/e2e_test_reports/{flow_name}_e2e_test_report.md`

---

## 输出

**1. 测试文件**

| 语言 | backend | frontend | 默认 |
|------|---------|----------|------|
| TypeScript | `tests/backend/e2e/{flow-name}.spec.ts` | `tests/frontend/e2e/{flow-name}.spec.ts` | `tests/e2e/{flow-name}.spec.ts` |
| Python | `tests/backend/e2e/test_{flow_name}.py` | `tests/frontend/e2e/test_{flow_name}.py` | `tests/e2e/test_{flow_name}.py` |
| Java | `src/test/java/.../e2e/{FlowName}Test.java` | - | 同左 |

**2. 运行命令**

```bash
npx playwright test tests/e2e/shopping-flow.spec.ts
pytest tests/e2e/test_shopping_flow.py
npx playwright test --ui  # 调试模式
```

**3. data-testid 清单**（告知前端需要添加哪些 testid）

---

## 执行前强制扫描（Pre-flight）

1. 扫描 mock/hardcoded data：`grep -r "mock\|fixture\|hardcoded" --include="*.ts" -l`
2. 验证 ID 是真实 UUID 格式，禁止 `const id = "test-id"` 等占位符
3. 验证「点击已有数据」路径：先查询真实存在的记录，再操作
4. 验证错误有可见提示（错误必须有用户可见的 UI 提示，不静默失败）

---

## 严格禁止

- ❌ 超过 2 条 E2E 测试
- ❌ 任何 Mock
- ❌ `page.waitForTimeout()` / sleep
- ❌ CSS 类名 / XPath 选择器
- ❌ 测试之间状态依赖

## 成功标准

- [ ] E2E 测试不超过 2 条，覆盖最关键主流程
- [ ] 稳定选择器（data-testid / role）
- [ ] 无 sleep / waitForTimeout
- [ ] 无 mock / hardcoded data（使用真实接口和记录）
- [ ] 覆盖「点击已有数据」路径，ID 是真实格式
- [ ] 页面错误有可见提示
- [ ] 测试独立运行，单条执行 < 2 分钟
- [ ] 提供了 data-testid 清单
