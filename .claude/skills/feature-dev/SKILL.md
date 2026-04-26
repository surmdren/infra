---
name: feature-dev
description: 在已有软件项目上增量开发新功能（Feature）。接收功能描述，分析影响范围，同步更新架构文档（PRD/TechSolution/Architecture/DevPlan），拆解增量开发任务，执行 TDD 开发，运行回归测试，提交 PR。⚠️ 与 dev-executor 的区别：dev-executor 面向全新项目的模块开发；feature-dev 面向已有代码库的增量功能开发。当用户提到"加功能"、"新增功能"、"添加feature"、"实现新需求"、"在现有项目上加"、"add feature"时触发。
---

# Feature Dev

在已有项目上增量开发新功能，全流程闭环：需求澄清 → 影响分析 → 文档更新 → 开发实现 → 技术验收 → 人工测试用例 → PR。

## 文档约定结构

skill 按以下固定路径管理 feature 文档，**项目应遵循此约定**：

```
docs/
├── PRD.md                        # 产品概述、用户角色、全局规则（不放 feature 细节）
└── features/
    ├── 001-user-auth.md           # 每个 feature 独立文件
    ├── 002-dashboard.md
    └── NNN-<feature-name>.md

DevPlan/
├── overview.md                    # 总进度索引（所有 feature 的状态汇总）
└── features/
    ├── 001-user-auth/
    │   └── checklist.md
    └── NNN-<feature-name>/
        └── checklist.md
```

### overview.md 格式

```markdown
| ID  | Feature  | PRD 文件                          | DevPlan 目录                        | 状态 | 完成度 |
|-----|----------|-----------------------------------|-------------------------------------|------|--------|
| 001 | 用户认证 | docs/features/001-user-auth.md    | DevPlan/features/001-user-auth/     | ✅   | 3/3    |
| 002 | 数据看板 | docs/features/002-dashboard.md    | DevPlan/features/002-dashboard/     | 🚧   | 2/5    |
```

### feature PRD 文件格式（`docs/features/NNN-<name>.md`）

```markdown
## Feature: <功能名>

### 背景
<为什么要做这个功能>

### 用户故事
- 作为 <角色>，我希望 <行为>，以便 <价值>

### 功能描述
- <功能点 1>
- <功能点 2>

### 验收标准
- [ ] <可验证的条件 1>
- [ ] <可验证的条件 2>

### 不在范围内
- <明确排除的内容>
```

### feature checklist 格式（`DevPlan/features/NNN-<name>/checklist.md`）

```markdown
# Feature NNN: <功能名>

PRD: docs/features/NNN-<name>.md

## Tasks
- [ ] Task 1: 数据层 - <具体描述>
- [ ] Task 2: 服务层 - <具体描述>
- [ ] Task 3: API 层 - <具体描述>
- [ ] Task 4: 前端组件 - <具体描述>
- [ ] Task 5: 集成联调

## UAT 测试用例

> 根据 PRD 用户故事逐条列出，供人工验收执行

### 正向场景
- [ ] UAT-01: <基于用户故事1> — 步骤：... 通过标准：...
- [ ] UAT-02: <基于用户故事2> — 步骤：... 通过标准：...

### 跨角色链条
- [ ] UAT-0X: <角色A操作 → 角色B继续> — 步骤：... 通过标准：...

### 异常与边界
- [ ] UAT-0X: <负向场景> — 步骤：... 通过标准：...
```

## Phase 0: 文件发现

执行前，先定位本次 feature 的相关文件：

```bash
# 读取总索引，确认下一个 feature ID
cat DevPlan/overview.md 2>/dev/null || echo "首次使用，将创建 overview.md"

# 检查 docs/features/ 已有的 feature 文件
ls docs/features/ 2>/dev/null
```

- 若 `DevPlan/overview.md` 存在：读取索引，分配新 ID，定位已有文件
- 若不存在：初始化目录结构，从 ID 001 开始

## Phase 1: 需求澄清

接收 Feature 描述后，确认以下信息（必要时提问）：

- **功能目标**：这个 feature 解决什么问题？
- **用户角色**：谁来使用？
- **输入/输出**：触发条件和期望结果是什么？
- **边界**：不在本次范围内的是什么？
- **验收标准**：怎样算做完了？

## Phase 2: 影响范围分析

扫描现有代码库，识别受影响的模块：

```bash
# 查看项目结构
find . -type f -name "*.ts" -o -name "*.py" -o -name "*.go" | head -50

# 搜索相关模块
grep -r "<关键词>" --include="*.ts" -l
```

输出影响分析报告：
- 需要新增的文件/模块
- 需要修改的现有文件
- 受影响的 API 端点
- 数据库 Schema 变更（如有）
- 潜在的破坏性变更
- **架构影响结论**（必填）：
  - `架构影响：无` — 普通功能增量，不涉及新组件或数据流变更
  - `架构影响：需更新 Architecture.md — 原因：<具体说明>` — 新增重要组件、引入中间件、改变数据流等

此结论直接决定 Phase 3 是否更新 `Architecture.md` / `TechSolution.md`，不再依赖隐式判断。

## Phase 3: 创建/更新文档

按约定结构创建本次 feature 的文档文件：

1. **分配 Feature ID**：读取 `DevPlan/overview.md`，取最大 ID + 1
2. **创建 PRD 文件**：`docs/features/NNN-<name>.md`（使用上方格式）
3. **创建 checklist**：`DevPlan/features/NNN-<name>/checklist.md`（使用上方格式）
4. **更新索引**：在 `DevPlan/overview.md` 追加新行（状态设为 🚧）
5. **按需更新全局文档**（跳过不存在的）：

| 文档 | 何时更新 |
|------|----------|
| `docs/PRD.md` | 涉及全局用户角色或产品定位变化时 |
| `TechSolution.md` | 引入新技术或改变整体架构时 |
| `Architecture.md` | 新增重要组件或改变数据流时 |
| `API.md` / `docs/api.md` | 新增/变更对外暴露的接口时 |
| `database/schema.sql` | 有 DB Schema 变更时 |

**原则**：feature 细节只写在 feature 独立文件里，全局文档只更新全局影响的部分。

## Phase 4: 拆解开发任务

将 feature 拆解为独立可测试的子任务，每个任务遵循单一职责：

```
Feature: <功能名>
├── Task 1: 数据层（Model/Schema 变更）
├── Task 2: 服务层（业务逻辑实现）
├── Task 3: API 层（接口实现）
├── Task 4: 前端组件（UI 实现）
└── Task 5: 集成联调
```

## Phase 5: TDD 开发

参照 dev-executor 的 TDD 标准执行，按任务顺序逐个完成：

1. **先写测试**（描述期望行为）
2. **实现代码**（让测试通过）
3. **运行测试**
4. **修复直到通过**
5. **更新 checklist**（勾选已完成的 Task）

```bash
# 运行新增测试
npm test -- --testPathPattern="<feature-name>"

# 运行全量回归测试（确保不破坏已有功能）
npm test
```

发现回归问题时，立即定位并修复，不跳过。

## Phase 6: UI/UX 更新（条件执行）

**触发条件**：feature 有用户界面变更时执行，否则跳过。

调用 `/ui-ux-pro-max` 或 `/uiux-design`（根据需要）：
- 有新页面 → 生成完整页面设计规格，输出到 `Design/features/NNN-<name>/`
- 改动现有页面 → 更新对应设计文档，注明变更部分
- 纯后端 feature → 跳过此 Phase

## Phase 7: 技术验收（release-qa）

调用 `/release-qa`，以本次 feature 的 PRD 和 checklist 为基准，验证：
- 所有验收标准是否满足
- API 接口是否符合设计
- 数据流是否正确
- 不破坏已有功能

输出验收报告到 `QA/features/NNN-<name>-qa-report.md`

**可选**：若 feature 涉及鉴权、数据存储、外部接口，追加执行 `/security-pentest` 扫描新增代码。

## Phase 8: 用户验收（UAT）

调用 `/uat-testing`，基于 feature PRD 的用户故事，执行 Playwright E2E 测试核心用户路径：

输出 UAT 报告到 `UAT/features/NNN-<name>-uat-report.md`

## Phase 9: 人工测试用例（UAT 场景清单）

基于 feature PRD 的用户故事，逐条生成 UAT 测试场景，写入 checklist 的「UAT 测试用例」区块：

**覆盖规则**：
- PRD 每条「作为 [角色]，我希望...」→ 至少一个正向 UAT 场景
- 识别跨角色链条（A 操作后 B 才能继续）→ 一个联动场景
- 每个核心操作列出对应的异常/边界场景（失败提示、权限拒绝等）

**场景格式**（写入 checklist）：
```
- [ ] UAT-XX: <场景描述> 
  - 角色：<买家/商户/管理员>
  - 步骤：1. ... 2. ... 3. ...
  - 通过标准：<用户视角可观察的结果>
```

调用 `/manual-testing` 生成完整手动测试文档，输出到 `ManualTesting/features/NNN-<name>/`

⚠️ 此阶段由 QA 人员手动执行，不自动触发。

## Phase 10: 提交 PR

```bash
# 最终回归测试
npm test  # 或 pytest / go test ./...

# 检查 lint
npm run lint

# 提交
git add -p
git commit -m "feat(<scope>): <功能描述>"

# 创建 PR
gh pr create --title "feat: <功能名>" --body "..."
```

PR 描述模板：
```markdown
## Feature
<功能描述>

## 变更内容
- 新增：...
- 修改：...
- 文档更新：...

## 测试结果
- [ ] 单元测试通过
- [ ] 回归测试通过
- [ ] release-qa 通过（QA/features/NNN-<name>-qa-report.md）
- [ ] UAT 通过（UAT/features/NNN-<name>-uat-report.md）

## 人工测试用例
ManualTesting/features/NNN-<name>/
```

更新 `DevPlan/overview.md` 状态为 ✅，完成度更新为全部完成。

**可选 - UTM 注入**：若 feature 新增了用户转化事件（注册/付款/激活等关键行为），执行 `/utm-injector` 补充埋点。

## 注意事项

- **不要过度设计**：只实现当前 feature 需要的，不预留"未来扩展"
- **向后兼容**：API 变更需考虑兼容性，必要时版本化
- **文档同步**：代码改了，文档必须同步更新
- **小步提交**：每个子任务独立 commit，便于 review 和回滚
