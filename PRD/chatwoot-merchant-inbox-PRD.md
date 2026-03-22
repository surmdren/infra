# 客商交流功能 产品需求文档 (PRD)

> 基于 Chatwoot 自托管实例（chatwoot-dev.dreamwiseai.com）
> 版本：v1.0 | 状态：草稿

## 目录

- [项目背景与目标](#项目背景与目标)
- [目标用户与角色定义](#目标用户与角色定义)
- [业务范围说明](#业务范围说明)
- [核心业务流程](#核心业务流程)
- [功能模块需求](#功能模块需求)
- [非功能性需求](#非功能性需求)
- [风险与不确定性提示](#风险与不确定性提示)
- [后续迭代建议](#后续迭代建议)

---

## 项目背景与目标

### 业务痛点

多商家平台中，客户咨询无法精准路由到对应商家，导致：
- 客服混乱：不同商家的对话混在一起，客服人员无法专注处理自家咨询
- 数据泄露风险：商家A的客服可能看到商家B的对话
- 入驻效率低：每个商家手动配置客服系统，无自动化流程

### 目标

1. 商家入驻时，通过 Chatwoot API **自动创建专属 Inbox**，零人工干预
2. 每个商家的客服账号**严格隔离**，只能访问自己 Inbox 的对话
3. 客户消息**精准路由**到对应商家的 Inbox
4. 商家客服通过 Chatwoot 统一后台**实时回复**

---

## 目标用户与角色定义

| 角色 | 说明 | 权限 |
|------|------|------|
| **平台管理员** | SuperAdmin，管理整个 Chatwoot 实例 | 可见所有 Inbox、Account、Agent |
| **商家** | 入驻平台的商户 | 拥有独立 Inbox，可管理自己的客服账号 |
| **商家客服（Agent）** | 商家指定的客服人员 | 只能查看和回复分配到自己 Inbox 的对话 |
| **客户（Consumer）** | 平台上的买家/访客 | 通过 Widget 或 API 向对应商家发起咨询 |

---

## 业务范围说明（Scope）

### ✅ MVP 必须包含

- 商家入驻时自动调用 Chatwoot API 创建 Inbox
- 自动创建商家客服 Agent 账号并绑定到对应 Inbox
- 客户发消息时携带商家标识，路由到正确 Inbox
- 商家客服通过 Chatwoot 后台回复

### ❌ 暂不包含

- AI 自动回复（Phase 2）
- 多语言客服（Phase 2）
- 商家客服绩效统计（Phase 3）
- 跨 Inbox 对话转移（Phase 2）
- 移动端 APP 客服（Phase 2）

---

## 核心业务流程

### 主路径：商家入驻自动化配置

```
商家提交入驻申请
    ↓
平台后端审核通过
    ↓
调用 Chatwoot API（原子化操作，失败回滚）
    ├── 1. 创建 Inbox（Channel 类型: API 或 Web Widget）
    ├── 2. 创建商家客服 Agent 账号（邮箱/密码）
    └── 3. 将 Agent 绑定到 Inbox
    ↓
返回给商家：
    ├── Chatwoot 登录地址
    ├── inbox_identifier（前端 Widget 嵌入用）
    └── Agent 账号信息
```

### 主路径：客户发起咨询

```
客户访问商家页面
    ↓
前端加载 Chatwoot Widget（携带该商家的 inbox_identifier）
    ↓
客户发送消息
    ↓
Chatwoot 根据 inbox_identifier 路由到对应商家 Inbox
    ↓
商家客服在 Chatwoot 后台收到通知并回复
    ↓
客户实时收到回复
```

### 异常路径

| 异常场景 | 处理方式 |
|----------|----------|
| Chatwoot API 创建 Inbox 失败 | 回滚，入驻流程中断，返回错误信息，触发告警 |
| Agent 账号邮箱已存在 | 复用已有账号，重新绑定到新 Inbox |
| 商家 Inbox 被误删 | 支持手动重新调用 API 重建，[待确认] 是否保留历史对话 |
| 客户消息携带错误 inbox_identifier | 返回 404，前端提示"该商家客服暂不可用" |
| 客服离线 | Chatwoot 内置离线提示，[待确认] 是否需要邮件通知客户 |

---

## 功能模块需求

### 模块一：入驻自动化服务（后端）

**子功能 1.1 — Inbox 创建**

- 触发时机：商家入驻审核通过后
- 调用接口：`POST /api/v1/accounts/{account_id}/inboxes`
- 参数：
  - `name`：商家名称（如"商家A官方客服"）
  - `channel.type`：`api`（纯 API 接入）或 `web_widget`（前端嵌入）
  - `[待确认]` 是否需要自定义 Widget 配色以匹配商家品牌
- 返回：`inbox_id`、`inbox_identifier`，存入平台数据库

**子功能 1.2 — Agent 账号创建**

- 调用接口：`POST /api/v1/accounts/{account_id}/agents`
- 参数：
  - `name`：商家客服名称
  - `email`：商家提供的客服邮箱
  - `role`：`agent`
  - `[待确认]` 初始密码生成策略（随机生成后发邮件？还是商家自设？）
- 支持一个商家创建多个 Agent

**子功能 1.3 — Agent 与 Inbox 绑定**

- 调用接口：`POST /api/v1/accounts/{account_id}/inbox_members`
- 参数：`inbox_id`、`user_ids[]`
- 原子化执行：1.1 → 1.2 → 1.3，任一步骤失败则全部回滚

**子功能 1.4 — 商家配置存储**

平台数据库新增字段（或独立表）：

```sql
merchant_chatwoot_config (
  merchant_id        VARCHAR PRIMARY KEY,
  inbox_id           INT,
  inbox_identifier   VARCHAR,  -- 前端 Widget 使用
  account_id         INT,      -- Chatwoot Account ID
  created_at         TIMESTAMP
)
```

---

### 模块二：前端 Widget 集成

**子功能 2.1 — 商家页面嵌入**

每个商家页面根据 `inbox_identifier` 动态加载 Chatwoot Widget：

```javascript
// 从平台 API 获取当前商家的 inbox_identifier
const { inboxIdentifier } = await fetch(`/api/merchant/${merchantId}/chatwoot-config`)

window.chatwootSettings = { position: 'right', locale: 'zh_CN' }
// 使用商家专属 inbox_identifier 初始化
window.chatwootSDK.run({
  websiteToken: inboxIdentifier,
  baseUrl: 'https://chatwoot-dev.dreamwiseai.com'
})
```

**子功能 2.2 — 客户身份识别（可选）**

若平台用户已登录，自动传递用户信息到 Chatwoot：

```javascript
window.$chatwoot?.setUser(userId, {
  name: userName,
  email: userEmail,
  phone_number: userPhone
})
```

---

### 模块三：商家客服后台

- 商家客服使用 Chatwoot 原生后台：`https://chatwoot-dev.dreamwiseai.com`
- 登录后只可见自己 Inbox 的对话（Chatwoot 原生权限隔离）
- [待确认] 是否需要为商家提供独立域名（如 `merchant-a.chatwoot-dev.dreamwiseai.com`）

---

### 模块四：平台管理接口（后端 API）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/merchant/{id}/chatwoot/setup` | POST | 商家入驻时触发，完整初始化 |
| `/api/merchant/{id}/chatwoot/config` | GET | 前端获取 inbox_identifier |
| `/api/merchant/{id}/chatwoot/agents` | POST | 为商家新增客服账号 |
| `/api/merchant/{id}/chatwoot/agents/{agentId}` | DELETE | 移除商家客服账号 |
| `/api/merchant/{id}/chatwoot/teardown` | DELETE | 商家退出时清理 Inbox |

---

## 非功能性需求

| 维度 | 要求 |
|------|------|
| **性能** | 入驻自动化配置（3个 API 调用）完成时间 < 3s |
| **可靠性** | Chatwoot API 调用失败重试 3 次，超过后写入失败队列，异步重试 |
| **安全** | inbox_identifier 不暴露在前端 URL 中；Chatwoot API Token 存储在 K8s Secret |
| **隔离性** | 商家 Agent 严格只能访问自己 Inbox，Chatwoot 原生权限保障 |
| **可观测性** | 每次 API 调用记录日志，接入 PostHog/Sentry 监控失败率 |
| **扩展性** | 支持同一商家多个 Agent、多个 Inbox（如售前/售后分开） |

---

## 风险与不确定性提示

| 风险 | 等级 | 说明 |
|------|------|------|
| Chatwoot API 限流 | 中 | 大量商家同时入驻时可能触发限流，需评估 Chatwoot 实例并发能力 |
| Agent 邮箱重复 | 低 | 同一邮箱不能注册多个 Agent，需要邮箱唯一性校验策略 |
| inbox_identifier 泄露 | 中 | 若 identifier 泄露，外部可向任意商家发送消息，需考虑鉴权机制 |
| Chatwoot 版本升级 | 低 | API 接口可能随版本变化，需固定镜像版本并做回归测试 |
| 历史对话归属 | [待确认] | 商家退出平台后，历史对话如何处理（保留/删除/归档）|
| 客服离线通知 | [待确认] | 是否需要邮件/短信通知客户"客服将在X小时内回复" |

---

## 后续迭代建议

### MVP（当前版本）
- 商家入驻自动创建 Inbox + Agent
- Web Widget 嵌入，客户消息精准路由
- 商家客服通过 Chatwoot 后台回复

### Phase 2
- **AI 自动回复**：接入 Claude/DeepSeek，对常见问题自动回答，人工客服兜底
- **知识库**：每个商家维护自己的 FAQ 知识库，供 AI 检索
- **多渠道**：支持微信、WhatsApp 等渠道接入同一 Inbox
- **对话转移**：支持将对话从售前 Inbox 转移到售后 Inbox

### Phase 3
- **客服绩效**：响应时长、满意度评分、对话量统计
- **商家自助管理**：商家在平台后台自助添加/删除客服账号
- **移动端**：商家客服使用 Chatwoot 移动 APP 回复
