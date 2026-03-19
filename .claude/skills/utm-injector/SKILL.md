---
name: utm-injector
description: 为已有项目补充 UTM 追踪、GA4、PostHog 分析能力，并自动创建 PostHog Dashboard。检测现有代码，幂等地添加缺失部分：lib/utm.ts（UTM 参数捕获与 localStorage 存储）、lib/analytics.ts（GA4 + PostHog 双轨上报）、Supabase user_utm 表迁移、layout.tsx 初始化注入、注册 AARRR 核心事件。最后自动检测部署域名，通过 PostHog API 创建按域名过滤的 AARRR Dashboard（UTM 来源/漏斗/留存/付费转化）。适用于没有 UTM 注入的现有项目，或需要补充分析能力的项目。当用户提到"加 UTM"、"UTM 追踪"、"注入分析"、"补充埋点"、"加 GA4"、"加 PostHog"、"PostHog Dashboard"、"utm-injector"时触发。
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

按优先级读取以下来源，后者覆盖前者：

1. `~/.dreamai-env`（共享凭据，PostHog Key 已预配置）
2. 项目 `.env.local` 或 `.env`（项目级覆盖）

```bash
# 加载共享凭据
source ~/.dreamai-env 2>/dev/null

# 加载项目级覆盖（优先级更高）
source .env.local 2>/dev/null || source .env 2>/dev/null
```

确认以下变量是否已配置：

| 变量名 | 来源 | 用途 |
|--------|------|------|
| `NEXT_PUBLIC_GA_MEASUREMENT_ID` | 项目 `.env.local` | GA4 数据流 ID（G-XXXXXXXXXX） |
| `NEXT_PUBLIC_POSTHOG_KEY` | `~/.dreamai-env` 已配置 | PostHog Project API Key |
| `NEXT_PUBLIC_POSTHOG_HOST` | `~/.dreamai-env` 已配置（https://us.i.posthog.com） | PostHog 实例地址 |
| `POSTHOG_PROJECT_ID` | `~/.dreamai-env` 已配置（323381） | 用于 API 查询 |
| `POSTHOG_PERSONAL_API_KEY` | `~/.dreamai-env` 已配置 | 用于 Step 7.2 自动验证 |

**缺失变量处理：**
- `NEXT_PUBLIC_POSTHOG_KEY` / `NEXT_PUBLIC_POSTHOG_HOST`：已在 `~/.dreamai-env` 预配置，无需手动填写
- `NEXT_PUBLIC_GA_MEASUREMENT_ID`：在 `.env.local` 末尾追加占位符，继续执行不阻塞

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

### Step 7: 验证事件是否到达 PostHog

**前置条件**：`NEXT_PUBLIC_POSTHOG_KEY` 已配置。

#### 7.1 发送测试事件（服务端直接调用）

通过 PostHog Capture API 发送一个带唯一标识的测试事件，绕过前端代码，直接验证网络连通性和 API Key 有效性：

```bash
POSTHOG_KEY=$(grep NEXT_PUBLIC_POSTHOG_KEY .env.local | cut -d '=' -f2)
POSTHOG_HOST=$(grep NEXT_PUBLIC_POSTHOG_HOST .env.local | cut -d '=' -f2 || echo "https://app.posthog.com")
TEST_EVENT_ID="utm_verify_$(date +%s)"

curl -s -X POST "${POSTHOG_HOST}/capture/" \
  -H "Content-Type: application/json" \
  -d "{
    \"api_key\": \"${POSTHOG_KEY}\",
    \"event\": \"utm_injector_verification\",
    \"distinct_id\": \"${TEST_EVENT_ID}\",
    \"properties\": {
      \"test\": true,
      \"injected_by\": \"utm-injector\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"

echo "Test event sent. distinct_id: ${TEST_EVENT_ID}"
```

#### 7.2 等待并查询 PostHog API 确认接收

PostHog 事件入库约需 10-30 秒，查询前先等待：

```bash
echo "Waiting 30s for PostHog to ingest event..."
sleep 30

# 需要 PostHog Personal API Key（不同于 Project API Key，在 PostHog Settings → Personal API Keys 生成）
# 从环境变量或提示用户输入
POSTHOG_PERSONAL_KEY=${POSTHOG_PERSONAL_API_KEY:-""}

if [ -z "$POSTHOG_PERSONAL_KEY" ]; then
  echo "⚠️  POSTHOG_PERSONAL_API_KEY 未配置，跳过自动查询。"
  echo "   请手动在 PostHog → Activity → Live Events 中搜索 distinct_id: ${TEST_EVENT_ID}"
else
  POSTHOG_PROJECT_ID=$(grep POSTHOG_PROJECT_ID .env.local | cut -d '=' -f2)
  RESULT=$(curl -s "${POSTHOG_HOST}/api/projects/${POSTHOG_PROJECT_ID}/events/?event=utm_injector_verification&properties=%5B%7B%22key%22%3A%22distinct_id%22%2C%22value%22%3A%22${TEST_EVENT_ID}%22%7D%5D" \
    -H "Authorization: Bearer ${POSTHOG_PERSONAL_KEY}")

  COUNT=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])" 2>/dev/null || echo "0")

  if [ "$COUNT" -gt "0" ]; then
    echo "✅ PostHog 验证通过：事件已成功接收（count=${COUNT}）"
  else
    echo "❌ PostHog 验证失败：未找到测试事件，请检查："
    echo "   1. NEXT_PUBLIC_POSTHOG_KEY 是否正确"
    echo "   2. POSTHOG_PROJECT_ID 是否正确"
    echo "   3. 网络是否可访问 ${POSTHOG_HOST}"
  fi
fi
```

#### 7.3 无 Personal API Key 时的替代验证

若无法获取 Personal API Key，引导用户手动确认：

```
手动验证步骤：
1. 打开 PostHog → Activity → Live Events
2. 搜索事件名：utm_injector_verification
3. 确认 distinct_id 包含 "utm_verify_" 前缀的事件存在
4. 检查属性中 injected_by = "utm-injector"

若事件存在 → ✅ 集成验证通过
若事件不存在（等待 2 分钟后） → ❌ 检查 API Key 和网络配置
```

#### 7.4 验证注入的业务事件（代码层面）并写入报告

扫描 Step 5.3 注入的 `trackEvent` 调用，统计注入情况，生成报告写入文件：

```bash
# 统计 trackEvent 调用
TRACK_FILES=$(grep -r "trackEvent(" --include="*.ts" --include="*.tsx" -l 2>/dev/null)
TRACK_COUNT=$(grep -r "trackEvent(" --include="*.ts" --include="*.tsx" 2>/dev/null | wc -l | tr -d ' ')
FILE_COUNT=$(echo "$TRACK_FILES" | grep -c . || echo 0)

# 生成报告
mkdir -p QA
REPORT_FILE="QA/utm-verification-report.md"

cat > "$REPORT_FILE" << EOF
# UTM Injector 验证报告

生成时间: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
项目: $(basename $(pwd))

## 网络连通性
- PostHog Capture API: ${CAPTURE_STATUS:-⚠️ 未执行}
- 测试事件 distinct_id: ${TEST_EVENT_ID:-N/A}

## 事件接收确认
- utm_injector_verification: ${VERIFY_STATUS:-⚠️ 需手动确认}

> 手动确认：PostHog → Activity → Live Events → 搜索 distinct_id: ${TEST_EVENT_ID:-N/A}

## 代码注入统计
- trackEvent 调用总数: ${TRACK_COUNT}
- 注入文件数: ${FILE_COUNT}

### 注入文件列表
$(echo "$TRACK_FILES" | sed 's/^/- /')

### 覆盖事件清单（来自 Step 5.2）
<!-- 在此列出所有注入的事件名 -->

## 待办
- [ ] 配置 POSTHOG_PERSONAL_API_KEY（可选，启用自动查询验证）
- [ ] 在 PostHog 确认测试事件已接收后删除/忽略该事件
EOF

echo "✅ 验证报告已写入: ${REPORT_FILE}"
```

**注意**：`CAPTURE_STATUS`、`VERIFY_STATUS`、`TEST_EVENT_ID` 变量由 7.1/7.2 步骤执行后赋值，确保按顺序执行。

---

### Step 8: 创建 PostHog Dashboard

#### 8.1 获取部署域名

按优先级依次尝试：

```bash
# 1. .env.local / .env
DOMAIN=$(grep -E "^NEXT_PUBLIC_APP_URL|^DOMAIN|^APP_URL" .env.local .env 2>/dev/null | head -1 | cut -d'=' -f2 | sed 's|https\?://||')

# 2. TechSolution 文档
if [ -z "$DOMAIN" ]; then
  DOMAIN=$(grep -rE "(domain|host):\s*\S+\.\S+" TechSolution/ 2>/dev/null | grep -oE "[a-z0-9.-]+\.[a-z]{2,}" | head -1)
fi

# 3. K8s Ingress yaml
if [ -z "$DOMAIN" ]; then
  DOMAIN=$(grep -rE "host:\s*\S+" infrastructure/ k8s/ 2>/dev/null | grep -oE "[a-z0-9.-]+\.[a-z]{2,}" | head -1)
fi

# 4. ~/.dreamai-env
if [ -z "$DOMAIN" ]; then
  DOMAIN=$(grep -E "^DOMAIN|^APP_DOMAIN" ~/.dreamai-env 2>/dev/null | head -1 | cut -d'=' -f2)
fi

# 5. 找不到 → 询问用户
if [ -z "$DOMAIN" ]; then
  echo "未能自动检测部署域名，请输入（如 app.example.com）："
  read DOMAIN
fi

echo "✅ 使用域名: ${DOMAIN}"
```

#### 8.2 分析业务类型 + 已注入事件

读取 PRD 和 Step 5.2 生成的事件清单，确定 Dashboard 模板：

- **SaaS / 订阅制**：AARRR 漏斗 + 试用转化 + MRR 趋势
- **电商**：商品浏览 → 加购 → 结账转化漏斗
- **内容/工具站**：页面 PV + 核心功能使用率 + 分享率

扫描代码获取真实事件列表：

```bash
EVENTS=$(grep -rh "trackEvent(" --include="*.ts" --include="*.tsx" . 2>/dev/null \
  | grep -oE "'[a-z_]+'" | sort -u | tr -d "'" | tr '\n' ',')
echo "已注入事件: ${EVENTS}"
```

#### 8.3 通过 PostHog API 创建 Dashboard + Insights

```bash
source ~/.dreamai-env 2>/dev/null
source .env.local 2>/dev/null || source .env 2>/dev/null

PH_HOST="${NEXT_PUBLIC_POSTHOG_HOST:-https://us.i.posthog.com}"
PH_PROJECT="${POSTHOG_PROJECT_ID}"
PH_KEY="${POSTHOG_PERSONAL_API_KEY}"
PROJECT_NAME=$(basename $(pwd))

# 创建 Dashboard
DASHBOARD_ID=$(curl -s -X POST "${PH_HOST}/api/projects/${PH_PROJECT}/dashboards/" \
  -H "Authorization: Bearer ${PH_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"${PROJECT_NAME} | ${DOMAIN}\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "✅ Dashboard 创建成功: ID=${DASHBOARD_ID}"

# 创建标准 Insights（按 AARRR）
create_insight() {
  local name=$1
  local filters=$2
  curl -s -X POST "${PH_HOST}/api/projects/${PH_PROJECT}/insights/" \
    -H "Authorization: Bearer ${PH_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"${name}\", \"filters\": ${filters}, \"dashboards\": [${DASHBOARD_ID}]}" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('  ✅', d.get('name','?'), '- ID:', d.get('id','?'))"
}

# Acquisition: UTM source breakdown
create_insight "[Acquisition] UTM Source Breakdown" \
  "{\"events\":[{\"id\":\"\$pageview\"}],\"breakdown\":\"utm_source\",\"breakdown_type\":\"event\",\"properties\":[{\"key\":\"\$host\",\"value\":\"${DOMAIN}\",\"operator\":\"exact\",\"type\":\"event\"}],\"date_from\":\"-30d\"}"

# Acquisition: UTM medium breakdown
create_insight "[Acquisition] Traffic Medium" \
  "{\"events\":[{\"id\":\"\$pageview\"}],\"breakdown\":\"utm_medium\",\"breakdown_type\":\"event\",\"properties\":[{\"key\":\"\$host\",\"value\":\"${DOMAIN}\",\"operator\":\"exact\",\"type\":\"event\"}],\"date_from\":\"-30d\"}"

# Activation: Signup funnel
create_insight "[Activation] Signup Funnel" \
  "{\"insight\":\"FUNNELS\",\"events\":[{\"id\":\"\$pageview\"},{\"id\":\"signup_completed\"},{\"id\":\"aha_moment_reached\"}],\"date_from\":\"-30d\"}"

# Retention: User retention
create_insight "[Retention] User Retention" \
  "{\"insight\":\"RETENTION\",\"target_entity\":{\"id\":\"signup_completed\",\"type\":\"events\"},\"returning_entity\":{\"id\":\"\$pageview\",\"type\":\"events\"},\"date_from\":\"-30d\"}"

# Revenue: Payment conversion funnel
create_insight "[Revenue] Payment Conversion Funnel" \
  "{\"insight\":\"FUNNELS\",\"events\":[{\"id\":\"pricing_page_viewed\"},{\"id\":\"upgrade_cta_clicked\"},{\"id\":\"payment_completed\"}],\"date_from\":\"-30d\"}"

echo ""
echo "✅ PostHog Dashboard 创建完成"
echo "   访问: ${PH_HOST}/project/${PH_PROJECT}/dashboard/${DASHBOARD_ID}"
```

#### 8.4 更新验证报告

将 Dashboard 链接追加到 `QA/utm-verification-report.md`：

```bash
cat >> QA/utm-verification-report.md << EOF

## PostHog Dashboard
- Dashboard ID: ${DASHBOARD_ID}
- 域名过滤: ${DOMAIN}
- 访问链接: ${PH_HOST}/project/${PH_PROJECT}/dashboard/${DASHBOARD_ID}
- 包含 Insights: UTM 来源分布、流量媒介、注册漏斗、留存曲线、付费漏斗
EOF
```

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
| `QA/utm-verification-report.md` | 新建（Step 7 验证报告 + Step 8 Dashboard 链接） |

## 参考资源

- **layout.tsx 注入方式**：见 `references/layout-patch.md`
