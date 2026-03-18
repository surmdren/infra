---
name: competitor-customer-hunter
description: 系统化挖掘竞争对手的真实客户名单，用于 B2B 海外竞品客户抢夺。从 G2/Capterra 差评、LinkedIn、Twitter/X、竞品官网 Case Study、Product Hunt 评论等多个公开渠道，找出正在使用竞品的公司和关键决策人，输出带联系方式线索的结构化客户名单。适合在 competitor-analysis 之后执行，为 battle-card-generator 和 switching-campaign 提供目标客户输入。当用户提到"找竞品客户"、"挖竞争对手客户"、"竞品用户在哪里"、"抢竞品客户"、"competitor customers"、"找潜在客户"、"target competitor users"时触发。
---

# Competitor Customer Hunter

系统化从公开渠道挖掘竞品真实客户，输出可供直接触达的 B2B 客户名单。

## 输入

用户提供：
- 竞品名称（1-3 个）
- 自身产品所在行业/品类（用于缩小搜索范围）
- 目标客户画像（可选，如：100-500 人规模的 SaaS 公司 CTO）

## 输出

```
research/
└── competitor-customers/
    ├── {competitor}-customer-list.md    # 每个竞品一份客户名单
    └── summary.md                       # 汇总：总线索数、质量分布、推荐优先触达名单
```

---

## 挖掘渠道（按质量排序）

### 渠道 1：G2 / Capterra / Trustpilot 差评（最高价值）

差评用户是最容易被撬动的目标——他们已经不满意，只差一个更好的选择。

```
搜索：site:g2.com "{竞品名称}" reviews
搜索：site:capterra.com "{竞品名称}"
搜索："{竞品名称}" site:trustpilot.com
```

从每条差评中提取：
- 评论者姓名 + 职位（通常显示）
- 所在公司（点进评论者主页可见）
- 投诉的具体痛点（直接用于后续 switching-campaign 的切入点）
- 评分（3星以下为高优先级目标）

### 渠道 2：竞品官网 Case Study / Testimonials（精准但已满意）

竞品官网公开的客户成功案例，说明这些公司确实在用竞品。虽然他们目前满意，但仍是值得长期跟进的目标。

```
搜索：site:{竞品官网} "case study" OR "customer story" OR "testimonial"
搜索："{竞品名称}" "powered by" OR "built with" OR "uses {竞品名称}"
```

提取：公司名、行业、规模（通常在案例里提及）、使用场景。

### 渠道 3：LinkedIn（找到决策人）

LinkedIn 是 B2B 最重要的渠道，可以精准定位到使用竞品的个人。

**搜索策略：**
```
LinkedIn 搜索："{竞品名称}" in People's profile
LinkedIn 搜索："{竞品名称} admin" OR "{竞品名称} manager"
People 搜索筛选：Job Title = [目标职位] + Company Size = [目标规模]
```

也可以搜索竞品公司的 LinkedIn 页面 → Followers（关注竞品的人很可能是用户或潜在用户）。

**注意**：不要在 LinkedIn 上搜索"谁在用某软件"——应该搜索职位名称中提到竞品的人（如 "Salesforce Admin"、"HubSpot Specialist"）。

### 渠道 4：Twitter/X 提及

用户在推特上实名抱怨或讨论竞品，是极高意向的目标。

```
搜索："{竞品名称}" min_faves:5 lang:en -is:retweet
搜索："{竞品名称}" "frustrated" OR "issue" OR "broken" OR "switching" OR "alternative"
搜索："looking for alternative to {竞品名称}"
```

从推文中找到发帖者的公司（通常在个人简介里），记录投诉内容。

### 渠道 5：Reddit / 行业社群

```
搜索：site:reddit.com "{竞品名称}" alternative
搜索：site:reddit.com "switched from {竞品名称}"
搜索："{竞品名称}" site:reddit.com/r/{行业相关subreddit}
```

Reddit 上的帖子常常包含真实用户名 + 公司背景，且投诉/比较贴的评论区经常有大量同类用户出没。

### 渠道 6：Product Hunt / AppSumo 评论

适合 SaaS 产品。

```
搜索：site:producthunt.com "{竞品名称}"
```

Product Hunt 评论者通常是早期用户，个人主页可以找到 Twitter/LinkedIn。

### 渠道 7：竞品集成市场 / 合作伙伴页面

如果竞品有公开的集成合作（如 Zapier、Slack App Directory、Shopify App Store），可以通过集成用户间接找到客户：

```
搜索：site:zapier.com "{竞品名称}"
搜索："{竞品名称}" app directory
```

---

## 执行流程

### Phase 1：确认目标

向用户确认：
```
竞品名称：[用户提供]
行业/品类：[用户提供]
目标客户规模：[如：50-500人的SaaS公司]
目标决策人职位：[如：CTO、VP of Engineering、Product Manager]
```

### Phase 2：多渠道并行搜索

按渠道 1-7 的顺序执行 WebSearch，每个渠道搜索 2-3 次，覆盖不同关键词变体。

重点关注：
- **差评用户**（最容易撬动）
- **提到"looking for alternative"的用户**（已有换掉意向）
- **竞品官网 Case Study 里提到痛点的客户**

### Phase 3：信息提炼与去重

对每条线索记录：

| 字段 | 说明 |
|------|------|
| 公司名 | 目标公司 |
| 决策人姓名 | 尽量找到 |
| 职位 | CTO / VP / Manager |
| 来源渠道 | G2 差评 / LinkedIn / Twitter |
| 痛点 | 他们对竞品的具体不满 |
| 优先级 | 高（差评/换掉意向）/ 中（Case Study）/ 低（普通提及） |
| LinkedIn URL | 如果能找到 |
| 备注 | 其他有用信息 |

### Phase 4：输出报告

生成 `research/competitor-customers/{competitor}-customer-list.md`：

```markdown
# {竞品名称} 客户名单

> 挖掘时间：{日期} | 总线索数：{N} | 高优先级：{N}

## 🔴 高优先级（差评 / 已有换掉意向）

| 公司 | 决策人 | 职位 | 来源 | 核心痛点 | LinkedIn |
|------|-------|------|------|---------|---------|
| Acme Corp | John Smith | CTO | G2 差评 2星 | "数据导出太慢，支持响应差" | linkedin.com/in/... |

## 🟡 中优先级（已在用，但无明显不满）

| 公司 | 决策人 | 职位 | 来源 | 备注 |
|------|-------|------|------|------|

## 📊 渠道来源分布

| 渠道 | 线索数 | 高优先级数 |
|------|--------|-----------|
| G2/Capterra 差评 | | |
| 竞品 Case Study | | |
| LinkedIn | | |
| Twitter/Reddit | | |
```

生成 `research/competitor-customers/summary.md`，汇总所有竞品的名单，列出前 20 条推荐优先触达的线索。

---

## 下一步

名单生成后，告知用户：
- 用 `/battle-card-generator` 针对每个竞品生成对战话术
- 用 `/switching-campaign` 生成定向触达这批客户的文案
- 用 `/linkedin-outreach` 或 `/cold-email-sequence` 执行触达

---

## 注意事项

- 只收集**公开可见**的信息，不使用任何爬虫或未经授权的数据
- 差评中的公司名有时模糊处理，需结合评论者 LinkedIn 主页交叉验证
- 优先关注有明确痛点记录的线索，痛点越具体，后续触达转化率越高
- 每个竞品建议挖掘 20-50 条有效线索，太多反而难以处理
