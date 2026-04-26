---
name: miniprogram-test
description: 为微信小程序页面生成 miniprogram-automator UI 自动化测试脚本。先读 PRD 提取用户故事，再分析 wxml/js，生成覆盖展示态、交互、弹框的测试用例。如有 prd-gap 报告则直接消费，否则做简化版前端检查。仅限本地运行，不加入 CI。PRD 合规全栈检查请用 /prd-gap。
---

# Miniprogram Automator Test Generator

为微信小程序页面生成可运行的 UI 自动化测试，补充 pytest 无法覆盖的前端交互层。

## ⚠️ 重要约束

**这些测试只能本地运行，不能加入 CI workflow。**

原因：miniprogram-automator 依赖微信开发者工具 GUI，无头服务器无法启动。
在 CI 中加入此测试会导致 pipeline 持续失败。

---

## 输出目录约定

```
tests/miniprogram/
├── helpers/
│   └── setup.js                              # 共用启动 + mock 工具
└── features/
    └── NNN-{feature}/
        ├── fixtures.js                       # 集中管理 mock 数据
        ├── {page}.test.js                    # 测试文件（每个页面一个）
        └── ...

QA/features/NNN-{feature}/
└── miniprogram-report.md                     # 验收测试报告（运行后填写）
```

**命名规则**：`features/NNN-{feature}/{page}.test.js`，例如：
- `features/001-neolix-delivery/buyer-order.test.js`
- `features/001-neolix-delivery/merchant-dispatch.test.js`

**编号对应关系**（三个目录保持一致）：
```
tests/miniprogram/features/NNN-{feature}/   ← 测试代码
QA/features/NNN-{feature}/                  ← 验收报告
ManualTesting/features/NNN-{feature}/       ← 人工测试文档
```

---

## Phase 0: 先读 PRD，再看代码

**这是最重要的一步。** 先理解"应该做什么"，再看"实际做了什么"，才能发现 Gap。

读取以下文档（按优先级）：
1. `docs/features/NNN-{feature}.md` — 功能 PRD（用户故事 + 验收标准）
2. `DevPlan/features/NNN-{feature}/checklist.md` — UAT 场景列表
3. `ManualTesting/features/NNN-{feature}/` — 手动测试用例（如已存在）

**提取用户故事**，格式化为可测试的场景表：

| 用户故事 | 对应 UI 元素 | 测试类型 |
|---------|------------|---------|
| 作为买家，收到通知后点击开箱取货 | 「开箱取货」按钮 / 弹框 | 交互测试 |
| 作为买家，看到配送进度 | 进度条各节点 | 展示态测试 |

**如果没有 PRD 文档**，则询问用户目标功能的用户故事，再继续。

---

## Phase 1: 定位文件

```bash
# 确认目标页面文件存在
ls frontend/wenzhouxiewang/pages/{page-path}/
```

读取以下文件：
1. `index.wxml` — 提取结构
2. `index.js` — 提取数据和方法
3. `tests/miniprogram/helpers/setup.js` — 确认工具可复用

**如果 `helpers/setup.js` 不存在**，先生成它：

```javascript
// tests/miniprogram/helpers/setup.js
const automator = require('miniprogram-automator')
const path = require('path')

const MINIPROGRAM_PATH = path.resolve(__dirname, '../../../frontend/wenzhouxiewang')
const WX_CLI = '/Applications/wechatwebdevtools.app/Contents/MacOS/cli'

async function launchMiniProgram() {
  return automator.launch({
    projectPath: MINIPROGRAM_PATH,
    cliPath: WX_CLI,
  })
}

async function mockRequest(miniProgram, urlPattern, responseData) {
  await miniProgram.mockWxMethod('request', (args) => {
    if (args.url && args.url.includes(urlPattern)) {
      args.success({ statusCode: 200, data: { error: 0, ...responseData } })
      return
    }
    return args.__originalMethod__(args)
  })
}

async function clearMock(miniProgram) {
  await miniProgram.restoreWxMethod('request')
}

module.exports = { launchMiniProgram, mockRequest, clearMock }
```

同时确认 `tests/miniprogram/package.json` 的 jest config 包含：

```json
{
  "jest": {
    "testTimeout": 30000,
    "testMatch": ["**/features/**/*.test.js"]
  }
}
```

---

## Phase 2: 分析页面结构

从 `.wxml` 提取：

| 目标 | 提取内容 | 用途 |
|------|---------|------|
| `wx:if="{{...}}"` | 所有条件表达式 | 生成展示态测试 |
| `bindtap="xxx"` | 所有事件绑定 | 生成交互测试 |
| `<button>` | 按钮文案 + 属性 | 验证文案和状态 |
| `wx.showModal` / `wx.showActionSheet` | 弹框调用 | 生成弹框 mock |

从 `.js` 提取：

| 目标 | 提取内容 | 用途 |
|------|---------|------|
| `data: {}` | 初始数据结构 | 构造 mock 响应 |
| `t.post(url, ...)` | 所有 API 请求 URL | 生成 mockRequest |
| `wx.showModal(...)` | title / content | 验证弹框文案 |
| `wx.showToast(...)` | title | 验证 toast 文案 |

---

## Phase 3: 读取 Gap 报告（如已有）

如果 `QA/features/NNN-{feature}/prd-gap-report.md` 已存在（由 `/prd-gap` 生成），直接读取它，不重复分析。

根据报告中每条 AC 的状态决定测试写法：

| Gap 报告状态 | 测试写法 |
|------------|---------|
| ✅ 已实现 | 正常写测试 |
| ❌ BUG | 写会失败的测试，注释标注 `// BUG-XX，修复后应通过` |
| ❌ GAP | `test.todo('GAP-XX: ...')` 占位 |
| ❓ 待确认 | `test.todo('待确认: ...')` 占位 |

**如果 Gap 报告不存在**，在生成测试的同时做简化版 Gap 分析：只看前端 wxml/js，发现的问题写入测试文件末尾注释区块：

```javascript
/*
 * ⚠️ 已知 Bug / Gap（建议先运行 /prd-gap 做完整全栈检查）
 *
 * BUG-01: <描述> — <文件>:<行号>
 *   问题: ...  修复: ...
 *
 * GAP-01: <描述> — PRD 要求: ...
 */
```

---

## Phase 4: 归类测试场景

### 必须覆盖

**展示态测试**（每个 `wx:if` 分支至少一个）
```javascript
test('当 delivery_status=1 时，显示「开始装货」和「取消配送」按钮', async () => {
  // mock delivery_status=1
  // 断言按钮存在 / 不存在
})
```

**交互测试**（每个 `bindtap` 至少一个）
```javascript
test('点击「确认发货」弹出确认框', async () => {
  // mock wx.showModal，捕获 title/content
  // 验证文案正确
})
```

**Loading 状态测试**（有 loading/disabled 的按钮）
```javascript
test('呼叫中按钮进入 disabled 状态', async () => {
  // 让请求延迟响应
  // 点击后立即断言 disabled=true 且文案变化
})
```

### 不需要覆盖

- 实际网络请求（全部 mock）
- 微信支付流程
- 真实设备权限弹框
- 需要物理操作的场景（开箱、收货）

---

## Phase 5: 生成代码

### 选择器优先级

1. `button[bindtap="methodName"]` — 最稳定
2. `[data-testid="xxx"]` — 如果有的话
3. `.class-name` — 尽量避免，容易变
4. `view:nth-child(n)` — 最后手段

**如果页面缺少稳定选择器**，在测试文件顶部注释提示：
```javascript
// TODO: 建议给以下元素加 data-testid 以提高选择器稳定性：
// - 站点选择入口: data-testid="station-selector"
```

### require 路径规范

```javascript
// 文件在 features/NNN-{feature}/{page}.test.js
// helpers 在 helpers/setup.js（上两级）
const { launchMiniProgram, mockRequest, clearMock } = require('../../helpers/setup')
const fixtures = require('./fixtures')
```

### waitFor 规范

```javascript
// ❌ 禁止硬等待 > 500ms
await page.waitFor(1000)

// ✅ 条件等待（优先）
await page.waitFor(async () => {
  const btn = await page.$('button[bindtap="startLoading"]')
  return btn !== null
}, { timeout: 5000 })

// ✅ 短暂等待仅用于动画过渡（≤500ms）
await page.waitFor(300)
```

### wx 原生 API mock 规范

```javascript
// ActionSheet（站点选择等）
await miniProgram.mockWxMethod('showActionSheet', (args) => {
  args.success({ tapIndex: 0 })
})

// Modal（确认弹框）
await miniProgram.mockWxMethod('showModal', (args) => {
  modalTitle = args.title
  args.success({ confirm: false }) // 默认不执行，只验证弹框
})

// Toast
await miniProgram.mockWxMethod('showToast', (args) => {
  toastMessage = args.title
  args.complete?.()
})
```

### Fixtures 规范

mock 数据统一放在 `features/NNN-{feature}/fixtures.js`：

```javascript
module.exports = {
  buyerOrderBase: { error: 0, order: { id: 8001, status: 2, dispatchtype: 2 } },
  deliveryStatus1: { error: 0, delivery_status: 1, vin: 'X65557' },
  deliveryStatus2: { error: 0, delivery_status: 2, vin: 'X65557' },
  stationList: { error: 0, list: [{ station_id: 6780584, display_name: '淘宝城接驳点' }] },
}
```

测试文件中 `require('./fixtures')` 引用，不在文件内重复定义。

---

## Phase 6: 输出质量检查

生成后自查：

- [ ] Phase 0 已读取 PRD，测试基于用户故事而非仅基于代码结构
- [ ] Phase 3 Gap 分析已完成，BUG 写成失败测试，GAP 写成 `test.todo`
- [ ] 每个 PRD 验收标准都有对应测试或 `test.todo`
- [ ] 每个 `wx:if` 条件都有对应测试
- [ ] 每个 `bindtap` 都有对应测试
- [ ] 没有硬编码 `waitFor(>500ms)`
- [ ] mock 数据在 `fixtures.js`，测试文件内不重复定义
- [ ] `require` 路径使用 `../../helpers/setup` 和 `./fixtures`
- [ ] 文件顶部有注释说明覆盖范围和不覆盖内容
- [ ] 文件末尾有 Bug/Gap 注释区块
- [ ] 如有不稳定选择器，有 TODO 注释提示加 `data-testid`
- [ ] `QA/features/NNN-{feature}/miniprogram-report.md` 已创建（用下方模板）

---

## 运行说明

```bash
# 前置：微信开发者工具已开启服务端口
# 设置 → 安全设置 → 服务端口 → 开启

cd tests/miniprogram
npm install

# 运行单个 feature
npx jest features/NNN-{feature}/ --json --outputFile=../../QA/features/NNN-{feature}/jest-result.json
```

**不要运行**：
```bash
# ❌ 不要加入 CI
# ❌ 不要在无 GUI 的服务器上运行
```

---

## 报告模板

生成测试文件的同时，创建 `QA/features/NNN-{feature}/miniprogram-report.md`：

```markdown
# Miniprogram UI 验收报告 — {Feature 名称}

**测试日期**：（待填写）
**测试人**：（待填写）
**小程序版本**：（待填写）
**微信开发者工具版本**：（待填写）

## 测试结果汇总

| 测试文件 | 用例数 | 通过 | 失败 | 跳过 |
|---------|-------|------|------|------|
| {page}.test.js | — | — | — | — |

## 失败用例

> 全部通过时此节留空

| 用例名称 | 失败原因 | 是否 Bug |
|---------|---------|---------|

## Bug / Gap 状态

> 对照测试文件末尾的 ⚠️ 区块更新

| ID | 描述 | 状态 |
|----|------|------|
| BUG-01 | xxx | ☐ 待修复 |
| GAP-01 | xxx | ☐ 待排期 |

## 结论

☐ 通过（可上线）  ☐ 待修复后重测
```
