---
name: utm-injector
description: 为已有项目补充 UTM 追踪、GA4、PostHog 分析能力。检测现有代码，幂等地添加缺失部分：lib/utm.ts（UTM 参数捕获与 localStorage 存储）、lib/analytics.ts（GA4 + PostHog 双轨上报）、Supabase user_utm 表迁移、layout.tsx 初始化注入、注册 AARRR 核心事件。适用于没有 UTM 注入的现有项目，或需要补充分析能力的项目。当用户提到"加 UTM"、"UTM 追踪"、"注入分析"、"补充埋点"、"加 GA4"、"加 PostHog"、"utm-injector"时触发。
---

# UTM Injector

为现有 Next.js 项目补充完整的 UTM 追踪 + GA4 + PostHog 双轨分析能力。**幂等设计**：每步先检测文件是否已存在，只创建/修改缺失部分。

## 工作流程

### Step 1: 检测现有文件

并行检查以下文件是否存在：

```
lib/utm.ts              → UTM 捕获模块
lib/analytics.ts        → 分析上报模块
app/layout.tsx          → 根布局（注入点）
supabase/migrations/    → 数据库迁移目录
```

同时检查 `package.json` 是否已有 `posthog-js` 依赖。

记录检测结果，后续步骤只处理缺失或不完整的部分。

---

### Step 2: 检查环境变量

读取 `.env.local`（或 `.env`），确认以下变量是否配置：

| 变量名 | 用途 |
|--------|------|
| `NEXT_PUBLIC_GA_MEASUREMENT_ID` | GA4 数据流 ID（G-XXXXXXXXXX） |
| `NEXT_PUBLIC_POSTHOG_KEY` | PostHog Project API Key |
| `NEXT_PUBLIC_POSTHOG_HOST` | PostHog 实例地址（默认 https://app.posthog.com） |

**缺失变量处理：**
- 在 `.env.local` 末尾追加缺失变量的占位符，并注明需要填写
- 继续执行，不阻塞后续步骤

---

### Step 3: 生成缺失文件

#### 3.1 lib/utm.ts（若不存在）

创建 UTM 参数捕获模块，功能：
- `captureUTM()`: 解析 URL 参数（utm_source/medium/campaign/term/content），回退到 `inferSourceFromReferrer()` 推断来源，存入 `localStorage['utm_params']`（首次访问 first-touch 模型）
- `getStoredUTM()`: 从 localStorage 读取已存储的 UTM 数据
- `inferSourceFromReferrer()`: 从 `document.referrer` 推断来源（google/bing/baidu → organic；直接访问 → direct；其他 → referral + referrer domain）
- `saveUserUTM(userId)`: 将 UTM 数据写入 Supabase `user_utm` 表（用于归因分析）

```typescript
// lib/utm.ts 核心结构
export interface UTMParams {
  source: string       // utm_source 或推断来源
  medium: string       // utm_medium 或 'organic'/'direct'/'referral'
  campaign: string     // utm_campaign
  term?: string        // utm_term
  content?: string     // utm_content
  referrer?: string    // 原始 referrer
  landingPage: string  // 首次落地页 URL
  capturedAt: string   // ISO 时间戳
}

export function captureUTM(): UTMParams | null
export function getStoredUTM(): UTMParams | null
export function saveUserUTM(userId: string): Promise<void>
```

#### 3.2 lib/analytics.ts（若不存在）

创建 GA4 + PostHog 双轨上报模块：

```typescript
// lib/analytics.ts 核心结构
export function initAnalytics(): void  // 初始化 PostHog + GA4 gtag
export function trackEvent(
  eventName: string,
  properties?: Record<string, unknown>
): void  // 同时上报到 GA4 (gtag) 和 PostHog

export function identifyUser(
  userId: string,
  traits?: Record<string, unknown>
): void  // PostHog identify + GA4 set user_id
```

`trackEvent` 自动附加 UTM 参数（从 `getStoredUTM()` 获取），确保每个事件都带有来源信息。

#### 3.3 Supabase 迁移文件（若 user_utm 表不存在）

在 `supabase/migrations/` 创建迁移文件（文件名含时间戳）：

```sql
-- create user_utm table
CREATE TABLE IF NOT EXISTS user_utm (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  source TEXT,
  medium TEXT,
  campaign TEXT,
  term TEXT,
  content TEXT,
  referrer TEXT,
  landing_page TEXT,
  captured_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS user_utm_user_id_idx ON user_utm(user_id);

-- RLS
ALTER TABLE user_utm ENABLE ROW LEVEL SECURITY;
CREATE POLICY "users can insert own utm" ON user_utm
  FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "users can read own utm" ON user_utm
  FOR SELECT USING (auth.uid() = user_id);
```

---

### Step 4: 注入 layout.tsx

读取 `app/layout.tsx`，检查是否已有 `initAnalytics()` 和 `captureUTM()` 调用。

**若未注入**，在 `<body>` 渲染完成后的客户端 Script 或 `useEffect` 中添加初始化逻辑。

参考注入方式：见 `references/layout-patch.md`

**注意**：修改前先备份 layout.tsx，注入失败时恢复原文件。

---

### Step 5: PRD 深度分析 + 定制化事件注册

#### 5.1 读取产品文档，提取 3 个核心要素

并行读取以下文件（优先级从高到低）：
```
PRD/requirements.md        → 功能需求、用户流程
DevPlan/checklist.md       → 已实现模块列表
TechSolution/              → API 端点、数据模型
```

从文档中提取：

**① Aha Moment（用户首次感受到产品价值的时刻）**
- 识别标志：用户完成注册后第一个"哇塞"操作是什么？
- 例：AI 写作工具 → 第一次生成内容；报表工具 → 第一次看到数据图表
- 统一命名为 `aha_moment_reached`，属性中记录具体动作名

**② 变现漏斗节点**
- 找出从免费到付费的完整路径，每个节点都要追踪
- 例：`pricing_page_viewed` → `plan_selected` → `checkout_started` → `payment_completed`
- 若有试用期：加 `trial_started`、`trial_converted`

**③ 核心功能列表（用户高频使用的主流程）**
- 每个核心功能生成专属事件名，不用泛化的 `feature_X_used`
- 例：报表工具 → `report_created`、`report_exported`、`dashboard_shared`
- 例：AI 工具 → `generation_started`、`generation_completed`、`result_saved`

#### 5.2 生成定制化事件清单

基于 5.1 的分析，输出完整事件清单（按 AARRR 优先级排序）：

| 优先级 | 维度 | 事件名 | 触发时机 | 关键属性 |
|--------|------|--------|----------|----------|
| P0 | 变现 | `payment_completed` | 支付成功 | `plan`, `amount`, `currency` |
| P0 | 变现 | `subscription_started` | 订阅激活 | `plan`, `billing_cycle` |
| P0 | 激活 | `aha_moment_reached` | 首次完成核心动作 | `action_name`, `time_to_aha_seconds` |
| P1 | 激活 | `signup_completed` | 注册完成 | `method` (email/google/github) |
| P1 | 获客 | `page_viewed` | 每次页面访问 | `page`（自动附加 UTM） |
| P1 | 留存 | `{核心功能}_completed` | 核心功能完成 | 功能相关属性 |
| P2 | 变现 | `pricing_page_viewed` | 进入价格页 | `source` |
| P2 | 变现 | `upgrade_cta_clicked` | 点击升级按钮 | `cta_location`, `current_plan` |
| P2 | 留存 | `session_started` | 会话开始 | `days_since_signup` |
| P3 | 传播 | `share_clicked` | 分享操作 | `share_type`, `content_id` |
| P3 | 质量 | `error_encountered` | 报错 | `error_code`, `page` |

（`{核心功能}_completed` 替换为 5.1 中提取的具体功能名）

**事件命名规则**：`{名词}_{动词}` 全小写下划线，动词用过去式（`_completed`、`_started`、`_clicked`、`_viewed`）。

#### 5.3 在代码中注入事件

找到每个事件对应的代码位置并注入 `trackEvent` 调用：

```typescript
// 示例：Aha Moment 注入（AI 写作工具）
async function generateContent(prompt: string) {
  const result = await aiGenerate(prompt)

  const isFirstGeneration = await checkFirstTime(userId, 'generation')
  if (isFirstGeneration) {
    trackEvent('aha_moment_reached', {
      action_name: 'first_content_generated',
      time_to_aha_seconds: getSecondsSinceSignup(),
    })
  }

  trackEvent('generation_completed', {
    prompt_length: prompt.length,
    output_length: result.length,
  })
  return result
}
```

每个 `trackEvent` 自动附加存储的 UTM 参数（由 `lib/analytics.ts` 内部处理）。

---

### Step 6: 安装依赖

检查 `package.json`，若缺少 `posthog-js`：

```bash
npm install posthog-js
# 或
pnpm add posthog-js
# 或
bun add posthog-js
```

根据项目使用的包管理器选择对应命令（检查 `package-lock.json` / `pnpm-lock.yaml` / `bun.lockb` 判断）。

---

## 输出产物

| 文件 | 状态 |
|------|------|
| `lib/utm.ts` | 新建（如不存在） |
| `lib/analytics.ts` | 新建（如不存在） |
| `supabase/migrations/YYYYMMDDHHMMSS_create_user_utm.sql` | 新建（如不存在） |
| `app/layout.tsx` | 修改（注入初始化代码） |
| 各页面/组件文件 | 修改（注入事件追踪） |
| `.env.local` | 追加缺失变量占位符 |

## 参考资源

- **layout.tsx 注入方式**：见 `references/layout-patch.md`
