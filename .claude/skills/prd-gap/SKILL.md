---
name: prd-gap
description: PRD 验收标准 vs 实际实现的合规检查。逐条读取 PRD 验收标准，在后端代码、前端 wxml/js、数据库迁移中查找对应实现，输出每条要求的实现状态（已实现/BUG/GAP）。不生成代码，只输出报告。适用于功能开发完成后、UAT 前、上线前的合规核查。当用户说"检查 PRD 有没有漏掉"、"对照需求看实现"、"功能做完了吗"、"prd gap"时触发。
---

# PRD Gap Checker

对照 PRD 验收标准逐条检查代码实现，输出实现状态报告。

**职责边界**：
- ✅ 检查"做没做"（PRD 要求 vs 实际代码）
- ✅ 发现 BUG（代码有错，行为不符合预期）
- ✅ 发现 GAP（功能缺失，PRD 要求但未实现）
- ❌ 不评估行业最佳实践（那是 `product-gap-analyzer` 的职责）
- ❌ 不生成代码或测试

---

## 输出

```
QA/features/NNN-{feature}/
└── prd-gap-report.md     # PRD 合规检查报告
```

---

## Phase 0: 读取 PRD 验收标准

读取以下文档，提取所有验收标准：

1. `docs/features/NNN-{feature}.md` — 功能 PRD（**验收标准**章节，逐条提取）
2. `DevPlan/features/NNN-{feature}/checklist.md` — UAT 场景（补充边界条件）

将验收标准整理为检查清单：

```
AC-01: 买家可以看到配送进度条（delivery_status 1~4）
AC-02: delivery_status=4 时显示「开箱取货」按钮
AC-03: neolixDelivery 为 null 时页面不报错
AC-04: 商户取消后买家能看到取消原因
AC-05: 开箱取货弹框显示正确的 title 和 content
...
```

---

## Phase 1: 逐条检查实现

对每条验收标准，按以下顺序在代码中查找：

### 检查顺序

1. **前端 wxml**：条件渲染（`wx:if`）、按钮绑定（`bindtap`）、文案
2. **前端 js**：方法实现、API 调用、弹框文案（`wx.showModal` title/content）
3. **后端 PHP**：API 接口是否存在、返回字段是否正确
4. **数据库迁移**：所需字段是否在 migration 中创建

### 判断标准

| 结论 | 含义 | 示例 |
|------|------|------|
| ✅ 已实现 | 代码完整实现了 PRD 要求 | wxml 有对应 wx:if，js 有对应方法，后端有对应接口 |
| ⚠️ 部分实现 | 前端有但后端字段缺失，或反之 | 前端展示了字段，但后端接口不返回该字段 |
| ❌ BUG | 代码存在但行为有误 | `neolixDelivery.delivery_status` 在 null 时会报错 |
| ❌ GAP | 代码完全缺失 | app.js 没有推送通知点击跳转逻辑 |
| ❓ 待确认 | 无法从代码判断，需要联调或文档确认 | 第三方接口字段是否真实返回 |

---

## Phase 2: 生成报告

输出到 `QA/features/NNN-{feature}/prd-gap-report.md`：

```markdown
# PRD Gap 报告 — {Feature 名称}

**生成日期**：YYYY-MM-DD
**PRD 文档**：docs/features/NNN-{feature}.md
**检查范围**：前端 wxml/js + 后端 PHP + DB migration

## 汇总

| 状态 | 数量 |
|------|------|
| ✅ 已实现 | N |
| ⚠️ 部分实现 | N |
| ❌ BUG | N |
| ❌ GAP | N |
| ❓ 待确认 | N |

**结论**：☐ 可进入 UAT  ☐ 需修复后再 UAT

---

## 逐条检查结果

### AC-01: {验收标准描述}

**结论**：✅ 已实现

**证据**：
- 前端：`index.wxml:52` `wx:if="{{order.dispatchtype==2&&neolixDelivery}}"`
- 后端：`order/index.php` `detail()` 返回 `neolixDelivery` 对象

---

### AC-02: {验收标准描述}

**结论**：❌ BUG

**问题**：`index.wxml:503` 直接访问 `neolixDelivery.delivery_status`，当 `neolixDelivery` 为 null 时抛出异常。

**代码**：
```
wx:if="{{order.cancomplete&&order.dispatchtype==2&&neolixDelivery.delivery_status==4}}"
```

**修复建议**：
```
wx:if="{{order.cancomplete&&order.dispatchtype==2&&neolixDelivery&&neolixDelivery.delivery_status==4}}"
```

---

### AC-03: {验收标准描述}

**结论**：❌ GAP

**问题**：PRD 要求买家能看到取消原因，但 `index.wxml:52` 条件为 `order.status==2`，商户取消后 `order.status` 回退到 1，整个配送区域消失。

**PRD 原文**：「买家应能知晓配送被取消的原因」

**修复建议**：条件改为 `order.status>=1`，或单独处理 `delivery_status=5` 的展示。

---

### AC-0N: {验收标准描述}

**结论**：❓ 待确认

**问题**：前端使用了 `neolixDelivery.to_station_name` 字段（`index.wxml:88`），但无法从代码判断后端 `neolix/delivery/status` 接口是否实际返回此字段。

**需要**：联调时确认接口响应，或查看新石器 API 文档。

---

## 待处理事项

> 按优先级排序，上线前必须解决 BUG，GAP 视业务决策

### 必须修复（BUG）
- [ ] BUG-01: `index.wxml:503` null pointer — 1 行修复
- [ ] ...

### 需排期（GAP）
- [ ] GAP-01: 买家看不到取消原因 — 需前端条件调整
- [ ] GAP-02: 推送通知跳转 — 需 app.js 实现路由

### 需确认（待确认）
- [ ] GAP-02: `to_station_name` 字段后端是否返回 — 联调时验证
```

---

## 注意事项

- **只报告，不修复**：发现问题记录在报告中，不直接改代码。修复由开发者决策后执行。
- **给出证据**：每条结论都要有文件路径 + 行号，不能只说"代码有问题"。
- **GAP 不等于不上线**：GAP 是功能缺失，是否阻断上线由产品决策，不是技术判断。BUG 才是必须修复的。
- **待确认不要猜**：无法从代码判断的，老老实实标 ❓，不要猜测。
