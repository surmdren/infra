---
name: ceo-dashboard
description: CEO 管理驾驶舱，整合财务、项目进度、OKR、团队、风险等公司级信息。支持从 Excel/CSV、口头描述、API 等多种方式输入数据。生成周报/月报、Dashboard 视图（Mermaid图表）、决策记录。适用场景：(1) 查看公司整体运营状态 (2) 生成管理层周报/月报 (3) 跟踪 OKR/KPI 完成度 (4) 记录重要决策 (5) 管理业务风险 (6) 现金流和预算监控。当用户提到"CEO报告"、"管理层周报"、"公司状态"、"OKR进度"、"现金流"、"项目概览"、"风险登记"、"决策记录"时触发。
---

# CEO Dashboard - 管理驾驶舱

整合公司级关键信息，生成管理层报告和决策支持。

## 核心模块

```
┌─────────────────────────────────────────────────────┐
│                   CEO Dashboard                      │
├─────────────┬─────────────┬─────────────┬───────────┤
│   财务模块   │   项目模块   │   OKR模块   │  团队模块  │
│  Cash Flow  │  Projects   │   OKR/KPI   │   Team    │
├─────────────┴─────────────┴─────────────┴───────────┤
│            风险登记 │ 决策记录 │ 周报/月报            │
└─────────────────────────────────────────────────────┘
```

## 数据输入

支持多种输入方式：

| 方式 | 适用场景 | 示例 |
|------|---------|------|
| 口头描述 | 快速更新 | "本周收入50万，支出30万" |
| Excel/CSV | 批量导入 | 上传财务表格、项目清单 |
| Jira API | 项目数据 | 使用 `scripts/jira_sync.py` |
| 手动录入 | 结构化输入 | 按模板填写各模块数据 |

## 模块详情

### 1. 财务模块 (Finance)

**跟踪内容**: 现金流（收入/支出/余额）、预算对比（实际 vs 预算）、财务报表摘要

数据结构与输出示例见 `references/data-templates.md` — "财务模块"章节。

### 2. 项目模块 (Projects)

**跟踪内容**: 项目状态（on_track/at_risk/delayed/completed）、里程碑、负责人

状态字段：`on_track | at_risk | delayed | completed`

数据结构与 Mermaid 甘特图示例见 `references/data-templates.md` — "项目模块"章节。

### 3. OKR/KPI 模块

**跟踪内容**: Objectives（季度/年度目标）、Key Results（完成度）、KPI 指标

数据结构与进度条形图输出见 `references/data-templates.md` — "OKR/KPI 模块"章节。

### 4. 团队模块 (Team)

**跟踪内容**: 总人数、部门分布、入离职变动、关键岗位状态

数据结构见 `references/data-templates.md` — "团队模块"章节。

### 5. 风险登记 (Risk Register)

**跟踪内容**: 风险描述/类别、可能性/影响评估、缓解措施、负责人

风险矩阵（高/中/低可能性 × 高/中/低影响）输出示例见 `references/data-templates.md` — "风险登记"章节。

### 6. 决策记录 (Decision Log)

**跟踪内容**: 决策事项、背景与选项、最终决定及理由、后续行动

数据结构见 `references/data-templates.md` — "决策记录"章节。

## 报告生成

### 周报模板

使用 `assets/templates/weekly-report.md`，包含本周要点、财务快照、项目状态、OKR 进度、风险与问题、下周计划。周报输出格式见 `references/data-templates.md` — "周报输出示例"章节。

### 月报模板

使用 `assets/templates/monthly-report.md`，包含更详细的分析。

### Dashboard 视图

生成 Mermaid 图表（饼图、甘特图等）。示例见 `references/data-templates.md` — "Dashboard 图表示例"章节。

## 工作流程

### 更新数据
```
用户: "更新本周财务：收入50万，支出35万"

Claude:
1. 解析更新内容
2. 更新 data/finance.yaml（或内存状态）
3. 计算变化和趋势
4. 输出确认摘要
```

### 生成报告
```
用户: "生成本周周报"

Claude:
1. 汇总各模块最新数据
2. 计算关键指标和趋势
3. 识别需关注事项
4. 按模板生成 Markdown 报告
5. 保存到 reports/ 目录
```

### 查询状态
```
用户: "OKR进度怎么样？"

Claude:
1. 读取 OKR 数据
2. 计算各目标完成度
3. 识别落后项
4. 输出摘要 + 建议
```

## 输出目录结构

```
ceo_dashboard/
├── data/
│   ├── finance.yaml
│   ├── projects.yaml
│   ├── okr.yaml
│   ├── team.yaml
│   ├── risks.yaml
│   └── decisions.yaml
├── reports/
│   ├── weekly/
│   │   └── 2025-W04.md
│   └── monthly/
│       └── 2025-01.md
└── dashboard.md  # 实时概览
```

## 与其他 Skills 配合

| 场景 | 配合 Skill | 用法 |
|------|-----------|------|
| 从 Jira 同步项目 | jira-planner | 拉取项目状态到 Dashboard |
| 分析市场机会 | market-research | 机会发现 → 决策记录 |
| 海外拓展计划 | go-to-market | GTM 进度纳入项目跟踪 |

## 使用示例

**快速状态查询**:
```
用户: 公司现在状态怎么样？
→ 输出：财务、项目、OKR 的一页摘要
```

**数据更新**:
```
用户: 记录一下，今天决定参加广交会，预算15万
→ 更新决策记录，关联财务支出计划
```

**生成报告**:
```
用户: 生成给投资人看的月报
→ 生成正式月报，强调财务和里程碑
```

## 注意事项

1. **数据保密**: Dashboard 数据可能包含敏感信息，注意存储安全
2. **数据一致性**: 定期核对实际数据，避免偏差积累
3. **简洁优先**: CEO 视角关注关键指标，避免信息过载
4. **趋势比数字重要**: 突出变化趋势而非静态数字
5. **行动导向**: 每个问题都应有建议的下一步行动

## 参考资源

- **数据结构模板与输出示例**：见 `references/data-templates.md`
