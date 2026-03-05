---
name: dev-integration
description: 执行集成测试和E2E测试，验证所有模块协同工作。测试API接口、用户场景、模块间交互。发现问题时自动定位到具体模块，修复后重新测试直到通过。应在 dev-executor/dev-autopilot 所有模块完成后、release-qa 前执行。适用于验证系统集成、回归测试、发布前质量检查。当用户提到"集成测试"、"E2E测试"、"端到端测试"、"系统测试"、"API测试"、"模块联调"时触发。
---

# 集成测试与 E2E 测试执行器

在 dev-planner 所有模块开发完成后执行，验证整个系统功能正确性。

```
         E2E Tests      ← dev-integration 负责
        /            \
       / Integration  \  ← dev-integration 负责
      /______________\
     /   Unit Tests   \  ← dev-executor 负责
    /________________\
```

---

## 工作流程

| 步骤 | 操作 |
|------|------|
| Step 1 | 读取 `DevPlan/checklist.md`，确认所有基础/核心模块已完成 |
| Step 2 | 设计集成测试：基于 `TechSolution/backend/api-design.md` 设计 API 流程测试 |
| Step 3 | 设计 E2E 测试：基于 PRD 业务场景，使用 POM 模式组织页面对象 |
| Step 4 | 生成测试代码（见参考模板） |
| Step 5 | 运行测试（集成测试 + E2E 测试） |
| Step 6 | 问题定位 → 修复 → 重新测试（循环直到全部通过） |
| Step 7 | 生成测试报告 |

---

## Step 4: 测试代码模板

完整代码示例见 [references/test-examples.md](references/test-examples.md)：Fastify 集成测试、Playwright E2E 测试、vitest/playwright 配置文件、报告模板。

---

## Step 5: 运行测试

```bash
# 集成测试
cd backend && npm run test:integration

# E2E 测试（先启动服务）
npm run dev &
cd frontend && npm run test:e2e

# 查看报告
npm run test:integration -- --reporter=html
```

---

## Step 6: 问题定位

| 失败类型 | 可能模块 | 定位方法 |
|---------|---------|---------|
| API 404 | 路由/控制器 | 检查 routes, controller |
| 数据验证失败 | Service/Repository | 检查业务逻辑 |
| 数据库错误 | Repository/Schema | 检查数据模型 |
| 权限错误 | 认证授权模块 | 检查 middleware |
| 前端渲染错误 | 组件 | 检查 Component |

**自动修复循环**：

```
while 有失败测试:
  分析失败日志 → 定位问题模块 → 读取代码 → 修复 → 重新运行
```

---

## Output

```
backend/src/integration/
├── auth.integration.spec.ts
├── chat.integration.spec.ts
└── fixtures/test-data.ts

frontend/src/e2e/
├── scenarios/user-chat.e2e.spec.ts
└── pages/
    ├── LoginPage.ts
    └── ChatPage.ts

DevPlan/reports/
├── 集成测试报告.md
└── E2E测试报告.md
```

---

## 测试工具

| 工具 | 用途 |
|------|------|
| Vitest + Supertest | 集成测试 |
| Playwright | E2E 浏览器自动化 |
| Testcontainers | 容器化测试环境（可选） |

```bash
npm install --save-dev vitest supertest @playwright/test
npx playwright install
```

---

## 最佳实践

**集成测试**：每个测试使用测试数据库，结果可重复，名称清晰表达意图。

**E2E 测试**：模拟真实用户操作，使用 `data-testid` 而非 CSS 选择器，场景间无依赖，使用 POM 模式。
