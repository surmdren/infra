# 调研报告输出模板

## report.md 模板

```markdown
# 海外市场机会调研报告

## 执行摘要
- 筛选出 X 个高潜力机会（综合评分 ≥80分）
- TOP 3 推荐：[按评分排序]
- 总体机会评估

## 高潜力机会清单（≥80分）

### 1. [产品名称] - 综合评分 XX分

**基本信息**：行业、市场、HS编码

**供需缺口分析**：
- 全球供给分散度：[HHI指数]
- 中国生产能力：[强/中/弱]
- 中国出口竞争度：[渗透率%]

**四维度评分**：
- 市场规模：XX/100
- 竞争强度：XX/100
- 盈利能力：XX/100
- 执行难度：XX/100

**风险评估**：政策/运营/合规/市场风险分析

**推荐理由**：3-5个关键优势
**执行建议**：具体行动计划

---
[重复结构列出所有≥80分机会]
```

## executive_summary.md 模板

```markdown
# 海外市场机会 - 决策摘要

**调研时间**：YYYY-MM-DD
**目标市场**：[具体市场]
**调研范围**：[行业/产品类型]

## 核心发现

✅ **强烈推荐（≥85分）**：X个
- [产品A]：XX分 - [一句话优势]
- [产品B]：XX分 - [一句话优势]

⚠️ **值得考虑（80-84分）**：X个

## 决策建议

**立即行动**：[最高分产品]
**深入调研**：[需验证产品]
**暂缓进入**：[风险过高产品]

**总体判断**：[整体机会评估]
```

## Dashboard 数据结构

生成 `dashboard.html` 时，将所有机会数据组装为以下 JSON 结构，替换模板中的 `__DASHBOARD_DATA_PLACEHOLDER__` 占位符：

```javascript
{
  "meta": {
    "title": "海外市场机会调研 - {industry}",
    "industry": "{industry}",
    "target_market": "{target_market}",
    "generated_at": "YYYY-MM-DD",
    "total_opportunities": N,
    "high_potential_count": N
  },
  "opportunities": [
    {
      "name": "产品名",
      "industry": "行业",
      "segment": "细分",
      "target_market": "目标市场",
      "scores": { "market_size": 85, "competition": 72, "profitability": 90, "execution": 68 },
      "composite_score": 81.5,
      "gap_analysis": { "hhi_index": 0.15, "china_capability": 80, "export_penetration": 0.08 },
      "risks": { "policy": 70, "operations": 85, "compliance": 60, "market": 75 },
      "mvp": { "recommended_budget": "low", "method": "验证方法描述", "timeline": "4-8周" }
    }
  ]
}
```

Dashboard 包含 7 个模块：总览卡片、机会矩阵气泡图、四维雷达图、供需缺口面板、风险热力图、评分排行榜、MVP验证建议。
