---
name: copyright-scanner
description: 代码版权风险扫描。在集成任何外部代码之前，自动识别潜在的侵权风险。扫描代码库、仓库或文件，检测：(1) 版权声明头缺失或被篡改，(2) 国内常见商业软件特征码（微擎、CRMEB、FastAdmin 等破解版），(3) 开源协议类型及商业兼容性（GPL 传染性、MIT 可商用等），(4) 水印字符串或加密授权校验代码。输出风险报告 copyright-scan/copyright-risk-report.md，按高/中/低风险分级列出问题和处理建议。当用户提到"版权扫描"、"license 检查"、"开源协议兼容性"、"破解版检测"、"版权风险"、"copyright scan"、"license compliance"、"侵权风险"、"这个代码能商用吗"、"检查一下这个库的协议"时触发。遇到任何第三方代码集成、开源库引入、外包代码验收等场景，主动建议运行此 skill。
---

# 代码版权风险扫描

在集成外部代码前识别版权和许可证风险，避免商业侵权隐患。

## 扫描目标

接收用户提供的：
- 本地目录路径（如 `./vendor/some-lib`）
- Git 仓库 URL
- 单个文件
- 当前工程（无参数时扫描整个项目）

## 执行流程

### Phase 1：扫描（并行执行三个脚本）

```bash
# 1. 版权声明头扫描
python .claude/skills/copyright-scanner/scripts/scan_headers.py <target_path> --output /tmp/headers_result.json

# 2. 商业软件特征检测
python .claude/skills/copyright-scanner/scripts/detect_watermarks.py <target_path> --output /tmp/watermarks_result.json

# 3. 开源协议识别与兼容性检查
python .claude/skills/copyright-scanner/scripts/check_licenses.py <target_path> --output /tmp/licenses_result.json
```

三个脚本可以并行运行，互不依赖。

### Phase 2：风险评级

读取三个脚本的输出，结合以下参考文档进行评级：
- `references/risk-levels.md` — 风险等级标准
- `references/commercial-software-signatures.md` — 商业软件特征库（供人工核查补充）
- `references/license-compatibility.md` — 协议兼容性矩阵

### Phase 3：生成报告

输出到 `copyright-scan/copyright-risk-report.md`，格式见下方模板。

---

## 报告格式

```markdown
# 版权风险扫描报告

**扫描目标**: <path>
**扫描时间**: <datetime>
**风险概览**: 🔴 高风险 N 项 | 🟡 中风险 N 项 | 🟢 低风险 N 项

---

## 🔴 高风险（需立即处理）

### [风险项标题]
- **位置**: `file/path:line`
- **问题**: 具体描述
- **建议**: 处理方案

---

## 🟡 中风险（建议处理）

...

## 🟢 低风险（知悉即可）

...

---

## 许可证汇总

| 依赖/文件 | 许可证 | 商业可用 | 备注 |
|-----------|--------|----------|------|
| ...       | MIT    | ✅       |      |
| ...       | GPL-3  | ❌       | 传染性，需替换 |

---

## 行动建议

1. [按优先级列出需要处理的事项]
```

---

## 边界说明

- 扫描基于静态代码分析，无法保证 100% 覆盖
- 商业软件特征库以国内常见系统为主（见 `references/commercial-software-signatures.md`）
- 协议兼容性判断基于标准解读，具体法律风险建议咨询法务
- 遇到加密/混淆代码，标记为"需人工审查"而非直接判定风险等级
