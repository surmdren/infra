# Analytics 事件分析指南

生成开发计划时，读取 PRD，**优先识别直接反映 KPI 的核心事件**，再补充功能和参与度事件。

## KPI 驱动原则

> 每个事件必须能回答一个管理层关心的问题。没有对应 KPI 的事件不值得埋点。

读取 PRD 时，依次分析以下 5 个 KPI 维度，每个维度至少覆盖 1 个事件：

| KPI 维度 | 核心问题 | 必须覆盖的事件类型 |
|---------|---------|----------------|
| **获客（Acquisition）** | 用户从哪里来？哪个渠道 ROI 最高？ | 注册、首次访问落地页 |
| **激活（Activation）** | 用户完成了第一个关键动作吗？ | 首次使用核心功能、Onboarding 完成 |
| **留存（Retention）** | 用户下周/下月还会回来吗？ | 重复使用核心功能、登录频次 |
| **变现（Revenue）** | 用户付费了吗？付了多少？ | 订阅/购买/升级/续费/取消 |
| **传播（Referral）** | 用户会推荐给别人吗？ | 分享、邀请、复制链接 |

## 事件分析步骤

**Step 1：识别「Aha Moment」**

读取 PRD 的核心功能描述，找到「用户第一次体验到产品价值的时刻」，这个动作必须有专属事件。

示例：
- SaaS 工具：第一次成功生成/导出结果 → `{feature}_first_completed`
- 电商：第一次下单 → `order_first_placed`
- 社区：第一次发帖/评论 → `content_first_created`

**Step 2：识别变现漏斗**

读取 PRD 的定价/付费描述，逆向追踪完整付费路径，每个节点建一个事件：

```
访问定价页 → 点击付费按钮 → 填写支付信息 → 支付成功 → （升级/降级/取消）
     ↓              ↓              ↓             ↓              ↓
pricing_page  upgrade_cta    checkout_      subscription_  subscription_
_viewed       _clicked       started        started        cancelled
```

**Step 3：识别核心功能使用**

PRD 中出现频率最高的功能动词（生成/搜索/上传/发布/分享）→ 每个对应一个事件，加 `_completed` 后缀表示成功完成（区别于「开始」）。

**Step 4：补充质量信号事件**

| 信号 | 事件 | 说明 |
|------|------|------|
| 用户卡住了 | `error_encountered` | 记录错误类型，定位流失点 |
| 用户搜索了但没找到 | `search_no_results` | 发现内容缺口 |
| 用户放弃了表单 | `form_abandoned` | 找到阻力点 |
| 用户访问了帮助/文档 | `help_viewed` | 反映产品不够直觉 |

## 事件命名规范

```
{名词}_{动词过去式}
user_signed_up          ✅  获客
subscription_started    ✅  变现
report_first_generated  ✅  激活（Aha Moment）
invite_sent             ✅  传播
userSignup              ❌  不用驼峰
sign up                 ❌  不用空格
report_generate         ❌  用过去式
```

## 输出格式（写入 Analytics 模块文档）

按 KPI 维度分组输出，每个事件标注「对应 KPI」：

```markdown
## 事件清单

### 获客（Acquisition）
| 事件名 | 触发时机 | 关键属性 | KPI |
|--------|---------|---------|-----|
| user_signed_up | 注册成功 | method(email/google/sso), utm_source | 注册转化率 |
| landing_page_viewed | 访问落地页 | utm_source, utm_campaign, referrer | 渠道流量占比 |

### 激活（Activation）
| 事件名 | 触发时机 | 关键属性 | KPI |
|--------|---------|---------|-----|
| {aha_moment}_first_completed | 首次完成核心动作 | duration_seconds | D1激活率 |
| onboarding_completed | 完成新手引导 | steps_skipped | Onboarding完成率 |

### 留存（Retention）
| 事件名 | 触发时机 | 关键属性 | KPI |
|--------|---------|---------|-----|
| {core_feature}_used | 每次使用核心功能 | result_count | DAU/WAU |
| session_started | 用户登录/打开应用 | days_since_last_visit | 7日/30日留存 |

### 变现（Revenue）
| 事件名 | 触发时机 | 关键属性 | KPI |
|--------|---------|---------|-----|
| pricing_page_viewed | 访问定价页 | plan_highlighted | 付费意向漏斗 |
| upgrade_cta_clicked | 点击升级按钮 | source_page, plan | 付费转化率 |
| subscription_started | 付费成功 | plan, price, currency, interval | MRR |
| subscription_cancelled | 取消订阅 | plan, reason, tenure_days | 流失率/Churn |

### 传播（Referral）
| 事件名 | 触发时机 | 关键属性 | KPI |
|--------|---------|---------|-----|
| invite_sent | 发送邀请 | channel(email/link/social) | K因子 |
| share_clicked | 点击分享 | content_type, platform | 病毒系数 |

### 质量信号
| 事件名 | 触发时机 | 关键属性 | KPI |
|--------|---------|---------|-----|
| error_encountered | 出现错误 | error_code, page, action | 错误率 |
| search_no_results | 搜索无结果 | query | 内容缺口 |
| form_abandoned | 放弃填写 | form_name, last_field | 流失原因 |
```
