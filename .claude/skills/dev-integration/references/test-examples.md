# 集成测试代码示例

## Fastify 集成测试示例

```typescript
// backend/src/integration/chat.integration.spec.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { app } from '../app';
import { FastifyInstance } from 'fastify';

describe('Chat API Integration Tests', () => {
  let server: FastifyInstance;

  beforeAll(async () => {
    server = app;
    await server.ready();
  });

  afterAll(async () => {
    await server.close();
  });

  it('should complete full chat flow', async () => {
    // 1. 创建会话
    const sessionRes = await server.inject({
      method: 'POST',
      url: '/api/sessions',
      payload: { userId: 'user-123' }
    });
    expect(sessionRes.statusCode).toBe(201);
    const sessionId = sessionRes.json().id;

    // 2. 发送消息
    const messageRes = await server.inject({
      method: 'POST',
      url: '/api/messages',
      payload: { sessionId, content: '测试消息', type: 'text' }
    });
    expect(messageRes.statusCode).toBe(201);

    // 3. 获取消息历史
    const historyRes = await server.inject({
      method: 'GET',
      url: `/api/sessions/${sessionId}/messages`
    });
    expect(historyRes.statusCode).toBe(200);
    expect(historyRes.json().items).toHaveLength(1);
  });
});
```

---

## Playwright E2E 测试示例

```typescript
// frontend/src/e2e/scenarios/user-chat.e2e.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Chat E2E Tests', () => {
  test('should complete full chat flow', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.click('[data-testid="chat-button"]');

    await page.fill('[data-testid="message-input"]', '你好，我想咨询问题');
    await page.click('[data-testid="send-button"]');

    await expect(page.locator('[data-testid="ai-message"]')).toBeVisible();

    await page.click('[data-testid="transfer-agent-button"]');
    await expect(page.locator('[data-testid="agent-joined-message"]')).toBeVisible();
  });
});
```

---

## 问题修复示例

```typescript
// 问题：API 返回 500，日志：Cannot read property 'id' of undefined
// 定位：chat.service.ts 的 createMessage 方法

// 修复前
async createMessage(data: CreateMessageDto) {
  const session = await this.sessionRepo.findById(data.sessionId);
  return await this.messageRepo.create({
    sessionId: session.id,  // session 可能为 null
    content: data.content
  });
}

// 修复后
async createMessage(data: CreateMessageDto) {
  const session = await this.sessionRepo.findById(data.sessionId);
  if (!session) {
    throw new NotFoundException('Session not found');
  }
  return await this.messageRepo.create({
    sessionId: session.id,
    content: data.content
  });
}
```

---

## vitest.integration.config.ts

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['**/*.integration.spec.ts'],
    setupFiles: ['./backend/src/integration/setup.ts'],
    environment: 'node',
  },
});
```

---

## playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './frontend/src/e2e/scenarios',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## 集成测试报告模板

```markdown
# 集成测试报告

## 测试概览

| 项目 | 数量 |
|------|------|
| 测试套件 | XX 个 |
| 测试用例 | XX 个 |
| 通过 | XX |
| 失败 | XX |
| 执行时间 | XX 秒 |

## API 集成测试结果

| API 端点 | 状态 | 响应时间 | 备注 |
|---------|------|----------|------|
| POST /api/sessions | ✅ | 45ms | |
| POST /api/messages | ❌ | - | 500 Error |

## 模块集成测试

| 场景 | 状态 | 问题描述 |
|------|------|----------|
| 用户注册→登录 | ✅ | |
| 发送消息→AI回复 | ❌ | Redis 连接失败 |

## 问题修复记录

| 问题 | 定位模块 | 修复状态 |
|------|---------|---------|
| POST /api/messages 500 | chat.service | ✅ 已修复 |

## 最终结论

- [ ] 所有集成测试通过
- [ ] 可以进行 E2E 测试
```

---

## E2E 测试报告模板

```markdown
# E2E 测试报告

## 测试概览

| 项目 | 数量 |
|------|------|
| 测试场景 | XX 个 |
| 通过 | XX |
| 失败 | XX |
| 执行时间 | XX 秒 |

## 场景测试结果

| 场景 | 状态 | 失败步骤 |
|------|------|----------|
| 用户首次咨询 | ✅ | |
| 历史记录查询 | ❌ | 搜索结果不匹配 |

## 问题修复记录

| 问题 | 定位模块 | 修复状态 |
|------|---------|---------|
| 搜索结果不匹配 | message.repository | ✅ 已修复 |

## 最终结论

- [ ] 所有 E2E 测试通过
- [ ] 系统可以发布
```
