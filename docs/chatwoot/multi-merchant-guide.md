# Chatwoot 多店铺客服集成指南

> 实例地址：`https://chatwoot-dev.dreamwiseai.com`（dev）/ `https://chatwoot.dreamwiseai.com`（prod）
> SuperAdmin：`admin@dreamwiseai.com` / `DreamAI@2026`

---

## 架构说明

```
平台后端
    ↓ 调用 Chatwoot API
Chatwoot（不改源码，纯 API 集成）
    ├── Inbox A（店铺A）← 客服A 登录只看这里
    ├── Inbox B（店铺B）← 客服B 登录只看这里
    └── Inbox C（店铺C）← 客服C 登录只看这里
```

**权限隔离机制：**
- 每个客服是 Chatwoot 的 Agent
- Agent 只被分配到自己店铺的 Inbox
- 登录后台后只能看到分配给自己 Inbox 的对话，看不到其他店铺的数据

---

## 配置信息

```bash
# Dev 环境
CHATWOOT_URL=https://chatwoot-dev.dreamwiseai.com
CHATWOOT_ACCOUNT_ID=1                    # 登录后台后在 URL 中可以看到
CHATWOOT_API_TOKEN=                      # SuperAdmin token，见下方获取方式

# 获取 SuperAdmin API Token：
# 登录 Chatwoot → 左下角头像 → Profile Settings → Access Token
```

---

## Step 1：获取 API Token

```bash
# 方式一：用邮箱密码登录获取
curl -X POST https://chatwoot-dev.dreamwiseai.com/auth/sign_in \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@dreamwiseai.com",
    "password": "DreamAI@2026"
  }'

# 返回中的 access_token 就是 API Token
# {
#   "data": {
#     "access_token": "xxxxxx",
#     "account_id": 1
#   }
# }
```

---

## Step 2：店铺入驻 — 创建 Inbox

```bash
CHATWOOT_URL="https://chatwoot-dev.dreamwiseai.com"
ACCOUNT_ID=1
TOKEN="your_api_token"
BRAND_COLOR="#FF6B35"   # 店铺品牌色

curl -X POST "$CHATWOOT_URL/api/v1/accounts/$ACCOUNT_ID/inboxes" \
  -H "api_access_token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "店铺A官方客服",
    "channel": {
      "type": "web_widget",
      "website_url": "https://shop-a.example.com"
    },
    "widget_color": "'"$BRAND_COLOR"'",
    "welcome_title": "欢迎咨询店铺A",
    "welcome_tagline": "我们将在24小时内回复您"
  }'

# 返回关键字段：
# {
#   "id": 123,                           ← inbox_id，存入数据库
#   "website_token": "abc123xyz",        ← 前端 Widget 嵌入用
#   "name": "店铺A官方客服"
# }
```

---

## Step 3：店铺入驻 — 创建客服账号

```bash
curl -X POST "$CHATWOOT_URL/api/v1/accounts/$ACCOUNT_ID/agents" \
  -H "api_access_token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "店铺A客服",
    "email": "cs@shop-a.com",
    "role": "agent",
    "password": "商家自己设置的密码"
  }'

# 返回关键字段：
# {
#   "id": 456,          ← agent_id，存入数据库
#   "name": "店铺A客服",
#   "email": "cs@shop-a.com"
# }
```

---

## Step 4：将客服绑定到 Inbox

```bash
INBOX_ID=123
AGENT_ID=456

curl -X POST "$CHATWOOT_URL/api/v1/accounts/$ACCOUNT_ID/inbox_members" \
  -H "api_access_token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inbox_id": '"$INBOX_ID"',
    "user_ids": ['"$AGENT_ID"']
  }'

# 绑定后：
# - 客服登录 Chatwoot 只能看到这个 Inbox 的对话
# - 看不到其他店铺的任何数据
```

---

## 完整入驻流程（伪代码）

```javascript
async function setupMerchant(merchant) {
  // 1. 创建 Inbox
  const inbox = await chatwoot.post(`/accounts/${ACCOUNT_ID}/inboxes`, {
    name: `${merchant.name}官方客服`,
    channel: { type: 'web_widget', website_url: merchant.url },
    widget_color: merchant.brandColor,
  })

  // 2. 创建客服账号
  const agent = await chatwoot.post(`/accounts/${ACCOUNT_ID}/agents`, {
    name: merchant.csName,
    email: merchant.csEmail,
    role: 'agent',
    password: merchant.csPassword,   // 商家自设
  })

  // 3. 绑定
  await chatwoot.post(`/accounts/${ACCOUNT_ID}/inbox_members`, {
    inbox_id: inbox.id,
    user_ids: [agent.id],
  })

  // 4. 存入平台数据库
  await db.merchantChatwoot.create({
    merchantId: merchant.id,
    inboxId: inbox.id,
    inboxToken: inbox.website_token,   // ← 前端 Widget 用这个
    agentId: agent.id,
    brandColor: merchant.brandColor,
  })

  return {
    chatwootUrl: 'https://chatwoot-dev.dreamwiseai.com',
    inboxToken: inbox.website_token,
    agentEmail: merchant.csEmail,
  }
}
```

---

## Step 5：前端嵌入 Widget

每个店铺页面用自己的 `website_token`（即 `inbox_identifier`）：

```html
<script>
  window.chatwootSettings = {
    position: 'right',
    locale: 'zh_CN',
  };
  (function(d, t) {
    var BASE_URL = "https://chatwoot-dev.dreamwiseai.com";
    var g = d.createElement(t), s = d.getElementsByTagName(t)[0];
    g.src = BASE_URL + "/packs/js/sdk.js";
    g.defer = true;
    g.async = true;
    s.parentNode.insertBefore(g, s);
    g.onload = function() {
      window.chatwootSDK.run({
        websiteToken: 'SHOP_A_INBOX_TOKEN',  // ← 每个店铺不同
        baseUrl: BASE_URL
      });
    };
  })(document, "script");
</script>
```

**识别已登录用户（可选）：**

```javascript
// 用户登录后调用，客服可以看到用户信息
window.$chatwoot?.setUser(user.id, {
  name: user.name,
  email: user.email,
  phone_number: user.phone,
})
```

---

## 常用管理 API

```bash
# 查看所有 Inbox
GET /api/v1/accounts/{account_id}/inboxes

# 更新 Inbox 配色
PATCH /api/v1/accounts/{account_id}/inboxes/{inbox_id}
{ "widget_color": "#FF0000" }

# 查看 Inbox 的客服列表
GET /api/v1/accounts/{account_id}/inbox_members/{inbox_id}

# 新增客服到 Inbox
POST /api/v1/accounts/{account_id}/inbox_members
{ "inbox_id": 123, "user_ids": [789] }

# 移除客服账号
DELETE /api/v1/accounts/{account_id}/agents/{agent_id}

# 停用 Inbox（商家退出时）
PATCH /api/v1/accounts/{account_id}/inboxes/{inbox_id}
{ "enabled": false }

# 查看某 Inbox 的对话
GET /api/v1/accounts/{account_id}/conversations?inbox_id={inbox_id}
```

---

## 权限隔离验证

```bash
# 1. 用商家客服账号登录，获取 agent token
curl -X POST https://chatwoot-dev.dreamwiseai.com/auth/sign_in \
  -d '{"email":"cs@shop-a.com","password":"xxx"}'
# → 拿到 agent_access_token

# 2. 用 agent token 查询对话 → 只能看到店铺A的对话
curl https://chatwoot-dev.dreamwiseai.com/api/v1/accounts/1/conversations \
  -H "api_access_token: {agent_access_token}"
# → 只返回 Inbox A 的对话，不会返回 Inbox B/C 的数据
```

---

## 数据库表结构

```sql
-- 存储店铺与 Chatwoot 的映射关系
CREATE TABLE merchant_chatwoot_config (
  merchant_id      VARCHAR PRIMARY KEY,
  inbox_id         INT NOT NULL,
  inbox_token      VARCHAR NOT NULL,   -- 前端 Widget 使用
  agent_id         INT NOT NULL,
  account_id       INT DEFAULT 1,
  brand_color      VARCHAR DEFAULT '#1F93FF',
  created_at       TIMESTAMP DEFAULT NOW(),
  updated_at       TIMESTAMP DEFAULT NOW()
);
```

---

## 相关文档

- PRD：`PRD/chatwoot-merchant-inbox-PRD.md`
- Chatwoot API 文档：`https://www.chatwoot.com/developers/api/`
- Dev 实例：`https://chatwoot-dev.dreamwiseai.com`
- K8s 配置：`k8s/k3s/dev/chatwoot/`
