---
name: switching-campaign
description: 基于竞品对战卡和客户名单，生成定向的"为什么切换到我们"推广活动素材。针对每个竞品客户群体，生成个性化的触达文案矩阵：冷邮件序列（5封）、LinkedIn DM 模板、定向广告文案、Landing Page 转化文案、案例故事框架。所有文案都基于竞品真实痛点，植入具体的切换理由和社会证明。适合在 battle-card-generator 生成对战卡之后使用，为 linkedin-outreach 和 cold-email-sequence 提供精准素材。当用户提到"切换文案"、"switching campaign"、"拉竞品用户"、"转化竞品客户"、"竞品客户文案"、"为什么切换"、"定向推广"、"触达竞品用户"时触发。
---

# Switching Campaign

基于竞品对战卡和客户名单，生成一套完整的"Why Switch"推广活动素材，帮助市场和销售团队系统化地触达竞品用户、推动转化。

## 输入

- 竞品名称（1-3 个）
- 我方产品名称和核心优势
- 可选：`battle-card-generator` 生成的对战卡（读取 `research/battle-cards/`）
- 可选：`competitor-customer-hunter` 生成的客户名单（读取 `research/competitor-customers/`）

## 输出

```
research/
└── switching-campaign/
    ├── vs-{竞品名}/
    │   ├── cold-email-sequence.md    # 5封冷邮件序列
    │   ├── linkedin-dm.md            # LinkedIn DM 模板（3个场景）
    │   ├── ad-copy.md                # 定向广告文案（Google/LinkedIn Ads）
    │   └── landing-page.md           # 专题 Landing Page 文案
    └── campaign-brief.md             # 整体活动简报（汇总所有竞品）
```

---

## Phase 0：读取已有素材

先读取已有的分析结果：

```bash
ls research/battle-cards/ 2>/dev/null
ls research/competitor-customers/ 2>/dev/null
cat research/battle-cards/quick-ref.md 2>/dev/null
```

从对战卡中提炼每个竞品的：
- **核心切换理由**（1-3 个最有力的）
- **目标客户特征**（最容易被撬动的用户类型）
- **竞品最大痛点**（基于真实用户反馈）
- **我方核心优势**（具体、可量化的）

如果没有对战卡，询问用户提供基本信息后继续。

---

## Phase 1：生成冷邮件序列

为每个竞品生成 5 封冷邮件，形成完整触达序列。

**序列逻辑：**
- 邮件 1：初次接触，以痛点切入（不提我方产品）
- 邮件 2：提供价值，分享行业洞察或数据
- 邮件 3：提出解决方案，简短对比
- 邮件 4：社会证明，案例 + 数据
- 邮件 5：最后一次，直接提问 + 简单 CTA

**每封邮件的写作原则：**
- 主题行 <50 字符，要具体不要模糊
- 正文 <150 字（移动端友好）
- 个性化占位符：`{{first_name}}`、`{{company}}`、`{{pain_point}}`
- 每封邮件只有一个 CTA，且 CTA 要低门槛

生成 `research/switching-campaign/vs-{竞品名}/cold-email-sequence.md`：

```markdown
# 冷邮件序列：面向 {竞品名} 用户

> 适用对象：使用 {竞品名} 的公司，尤其是对 [竞品最大痛点] 有过反馈的用户

---

## 邮件 1 / 5 — 痛点共鸣（第 1 天）

**主题行选项：**
- A: "Quick question about your {竞品名} setup"
- B: "{竞品名} users are [具体问题] — you too?"
- C: "The [具体痛点] problem with {竞品名}"

**正文：**
```
Hi {{first_name}},

Noticed {{company}} is using {竞品名} — we work with a lot of teams that do.

Quick question: are you running into [具体问题，如"the export limits when your team grows beyond 20 people"]?

We've heard this from a lot of {竞品名} users recently. Curious if it's been an issue for you too.

{我方姓名}
```

**发送时间：** 周二或周三上午 9-11 点

---

## 邮件 2 / 5 — 价值输出（第 3 天）

**主题行：** "How [客户类型] teams solve [痛点] (data inside)"

**正文：**
```
Hi {{first_name}},

Following up — wanted to share something relevant regardless of what you decide.

[行业数据或洞察，如：] We surveyed 200 teams who switched away from {竞品名} last year. The #1 reason: [具体原因].

The workaround most teams use: [简短描述].

Happy to share the full report if useful.

{我方姓名}
```

---

## 邮件 3 / 5 — 解决方案（第 7 天）

**主题行：** "What [相似公司] does differently"

**正文：**
```
Hi {{first_name}},

We built [我方产品] specifically for teams hitting {竞品名}'s [具体限制].

One thing that's different: [核心差异化功能，具体描述].

[相似公司名] switched 3 months ago — [具体结果，如：cut their monthly bill by $X and onboarded 2x faster].

Worth a 20-min call to see if it fits your setup?

{我方姓名}
```

---

## 邮件 4 / 5 — 社会证明（第 14 天）

**主题行：** "[客户名] switched from {竞品名} — here's what happened"

**正文：**
```
Hi {{first_name}},

One more thing: [客户名]'s team was in your exact situation 6 months ago — [描述相似场景].

After switching to [我方产品]:
- [具体结果1，如：saved $X/month]
- [具体结果2，如：onboarding time went from 2 weeks to 3 days]
- [具体结果3]

Their CTO said: "[真实引用或近似描述]"

Would a quick case study walkthrough be helpful?

{我方姓名}
```

---

## 邮件 5 / 5 — 最后一次（第 21 天）

**主题行：** "Last reach out — quick yes/no?"

**正文：**
```
Hi {{first_name}},

I'll keep this short — last email from me on this.

Are you actively looking at alternatives to {竞品名} right now?

A) Yes, let's talk
B) No, happy with our current setup
C) Not now, but follow up in [timeframe]

Just reply with A, B, or C — no commitment either way.

{我方姓名}
```
```

---

## Phase 2：生成 LinkedIn DM 模板

LinkedIn 触达比冷邮件更直接，但字数更有限。针对 3 个场景生成模板：

生成 `research/switching-campaign/vs-{竞品名}/linkedin-dm.md`：

```markdown
# LinkedIn DM 模板：面向 {竞品名} 用户

---

## 场景 A：对方在 G2/Reddit 上抱怨过 {竞品名}

> 适用：你看到对方发过对竞品的负面评论

**连接请求附言（<300字符）：**
```
Hi {{first_name}} — saw your comment about {竞品名}'s [具体问题]. We built [我方产品] to fix exactly that. Would love to connect and share how.
```

**跟进 DM（连接后 1 天内）：**
```
Thanks for connecting, {{first_name}}!

Your point about {竞品名}'s [问题] really resonated — we hear this constantly from [行业] teams.

We've helped [X] companies move off {竞品名} specifically because of this. The main thing they appreciate: [核心差异].

Would a quick 15-min call make sense to explore if it'd work for {{company}}?
```

---

## 场景 B：对方职位显示与 {竞品名} 相关（如 "HubSpot Admin"）

> 适用：对方 LinkedIn 个人简介/经历里提到使用竞品

**连接请求附言：**
```
Hi {{first_name}} — building a community of [行业] leaders exploring alternatives to {竞品名}. Your experience looks very relevant. Happy to connect!
```

**跟进 DM：**
```
Thanks {{first_name}}!

As someone who's managed {竞品名} at scale, I'd love your take on something:

What's the one thing you wish {竞品名} did better?

(We're building [我方产品] and actively talking to power users — your input would genuinely shape what we prioritize.)
```

---

## 场景 C：通用冷触达（无明显信号）

> 适用：对方符合 ICP 但无明显竞品使用信号

**连接请求附言：**
```
Hi {{first_name}} — noticed {{company}} is in [行业]. We work with similar teams on [核心价值主张]. Would love to connect!
```

**跟进 DM（连接后 3 天）：**
```
Hi {{first_name}},

Quick question: how is {{company}} currently handling [解决的核心问题]?

We work with [X] teams in [行业] who use [我方产品] for this — curious what your current setup looks like and whether it's working well.

Happy to share what others in your space are doing if useful.
```
```

---

## Phase 3：生成定向广告文案

为 Google Ads 和 LinkedIn Ads 生成竞品定向广告文案。

生成 `research/switching-campaign/vs-{竞品名}/ad-copy.md`：

```markdown
# 定向广告文案：面向 {竞品名} 用户

---

## Google Search Ads（竞品关键词投放）

> 关键词："{竞品名} alternative"、"{竞品名} vs"、"{竞品名} pricing"、"switch from {竞品名}"

### 广告组 1：Alternative 意图

**标题 1（30字符）：** {竞品名} Alternative — Free Trial
**标题 2：** [X]% Cheaper Than {竞品名}
**标题 3：** No Annual Contract — Cancel Anytime
**描述（90字符）：** Tired of {竞品名}'s [具体痛点]? [我方产品] gives you [核心功能] without the [痛点]. Start free.

### 广告组 2：Pricing 意图

**标题 1：** {竞品名} Too Expensive?
**标题 2：** [我方产品]：[X]x More Value
**标题 3：** See Why [X]K+ Teams Switched
**描述：** {竞品名} charges [具体费用]. We charge [我方费用]. Same features, fraction of the cost. Compare now.

---

## LinkedIn Sponsored Content

> 定向：职位包含 {竞品名} / 公司规模 [X-X] 人 / 行业 [X]

### 图文广告 — 痛点型

**标题：** Still struggling with {竞品名}'s [痛点]?

**正文：**
> [数据/引用，如：] "67% of {竞品名} users report [问题] as their #1 frustration." (G2, 2024)
>
> [我方产品] was built specifically for teams that need [解决方案].
>
> [客户名] switched 3 months ago and [具体结果].

**CTA 按钮：** "See the Comparison" / "Get Free Migration"

---

## 竞品对比 Landing Page 广告入口

**URL 路径建议：** /vs/{竞品名-lowercase}
**UTM 参数：** `?utm_source=google&utm_campaign=vs-{竞品名}&utm_medium=cpc`
```

---

## Phase 4：生成 Landing Page 文案

生成专门针对竞品用户的对比页文案框架。

生成 `research/switching-campaign/vs-{竞品名}/landing-page.md`：

```markdown
# Landing Page 文案：[我方产品] vs {竞品名}

> URL：/vs/{竞品名} | 目标：让竞品用户在 5 分钟内决定申请 Demo

---

## Hero Section

**主标题：**
> "[我方产品] vs {竞品名}: The Switch [X,000] Teams Made"

**副标题：**
> {竞品名} 在 [具体场景] 上的限制让越来越多团队开始寻找替代方案。看看 [我方产品] 如何解决他们最头疼的问题。

**CTA：** "Start Free Migration" / "See Live Demo"
**次级 CTA：** "Compare Features Side-by-Side ↓"

---

## 痛点区（Why Teams Leave {竞品名}）

> 用数据说话，每条有来源

**标题：** "What {竞品名} Users Say" (based on [X] G2 reviews)

- "❌ [痛点1]" — [真实用户引用], [职位] at [公司类型]
- "❌ [痛点2]" — [真实引用]
- "❌ [痛点3]" — [真实引用]

---

## 功能对比表

| 功能 | [我方产品] | {竞品名} |
|------|-----------|---------|
| [核心功能1] | ✅ 包含 | ❌ 需付费升级 |
| [核心功能2] | ✅ 无限制 | ⚠️ 有用量上限 |
| [核心功能3] | ✅ 内置 | ❌ 需第三方插件 |
| 客服响应时间 | ✅ <2小时 | ⚠️ 24-48小时 |
| 合同灵活性 | ✅ 月付，随时取消 | ❌ 年付锁定 |

---

## 迁移保障（降低切换成本）

**标题：** "Switching Is Easier Than You Think"

- ✅ **免费迁移服务**：我们的团队帮你从 {竞品名} 导出和导入所有数据
- ✅ **双轨并行期**：迁移过程中可同时使用两个平台，零停机
- ✅ **专属 Onboarding**：[X] 天内完成团队培训
- ✅ **30天退款保证**：如果不满意，全额退款

---

## 社会证明

**来自 {竞品名} 切换过来的客户：**

> "[引用]" — [姓名], [职位] at [公司]（前 {竞品名} 用户，切换于 [年份]）

**关键数据：**
- [X] 家公司从 {竞品名} 迁移
- 平均迁移时间：[X] 天
- 客户满意度：[X]/5 (基于 [N] 条评价)

---

## FAQ（针对切换顾虑）

**Q: 迁移数据会丢失吗？**
A: 不会。我们提供完整的数据导出工具和迁移支持...

**Q: 如果我们的团队已经习惯 {竞品名} 的界面怎么办？**
A: ...

**Q: {竞品名} 有些功能我们很依赖，你们有吗？**
A: ...
```

---

## Phase 5：生成活动简报

生成 `research/switching-campaign/campaign-brief.md`，供市场负责人统览：

```markdown
# Switching Campaign 活动简报

> 生成时间：{日期} | 目标：从竞品用户中获取 [X] 个 Demo 预约/月

## 活动概览

| 竞品 | 目标客户数 | 核心切换理由 | 预期转化率 |
|------|-----------|------------|----------|
| {竞品1} | [N] | [一句话] | [X]% |
| {竞品2} | [N] | [一句话] | [X]% |

## 执行优先级

1. **立即行动（本周）**：
   - 启动 Google Ads 竞品词投放（预算：$X/天）
   - 开始 LinkedIn 手动触达高优先级名单（5-10 人/天）

2. **下周**：
   - 发布竞品对比 Landing Page
   - 启动邮件序列（推荐工具：Apollo.io / Lemlist）

3. **持续运营**：
   - 每月补充新的竞品客户名单（用 `/competitor-customer-hunter`）
   - 每季度更新对战卡和文案（用 `/battle-card-generator`）

## 推荐工具栈

| 环节 | 工具 | 备注 |
|------|------|------|
| 冷邮件发送 | Apollo.io / Lemlist | 支持个性化序列 |
| LinkedIn 自动化 | Dux-Soup / Expandi | 注意 LinkedIn 限流规则 |
| 广告投放 | Google Ads + LinkedIn Campaign Manager | 竞品词 + 受众定向 |
| Landing Page | Webflow / Next.js | 建议用 UTM 追踪各渠道 |
| 数据追踪 | PostHog / HubSpot | 追踪 Demo 预约转化率 |
```

---

## 注意事项

- **合规性**：广告投放需遵守各平台关于竞品名称使用的规则（Google 允许竞品关键词，但广告文案中使用竞品商标需谨慎）
- **真实性**：所有数据和引用必须真实，不能夸大或捏造
- **个性化**：批量触达时，至少要有公司名、姓名、痛点 3 个个性化字段，否则回复率极低
- **节奏控制**：LinkedIn 每天手动触达不超过 20 人，避免账号被限制
- **A/B 测试**：邮件主题行和 LinkedIn 第一句话要 A/B 测试，优胜版本推广
- 生成完成后，告知用户可以用 `/linkedin-outreach` 或 `/cold-email-sequence` 开始实际执行触达
