---
name: privacy-scanner
description: 数据隐私合规扫描。在商用软件上线或集成外部代码之前，自动检测 PIPL（个人信息保护法）和 GDPR 数据隐私风险。扫描代码库、配置文件，检测：(1) PII 硬编码（手机号、身份证、银行卡、密码等），(2) 危险数据处理模式（明文存储、日志泄露、弱加密、HTTP 明文传输），(3) 配置文件隐私风险（Cookie 安全设置、CORS 策略、Session 配置）。输出风险报告 privacy-scan/privacy-risk-report.md，按高/中/低风险分级列出所有问题和修复建议。当用户提到"隐私扫描"、"PII检测"、"PIPL合规"、"GDPR合规"、"数据隐私风险"、"用户数据安全"、"隐私合规检查"、"这个项目有没有隐私问题"时触发。
---

# Privacy Scanner — 数据隐私合规扫描

## 适用场景

- 新项目上线前的隐私合规自查
- 集成第三方代码前的风险评估
- 定期隐私合规审计
- 出海产品的 GDPR 合规检查

## 扫描范围

| 维度 | 脚本 | 检测内容 |
|------|------|---------|
| PII 硬编码 | `scripts/scan_pii.py` | 手机号、身份证、银行卡、邮箱、密码、API Key |
| 危险数据处理 | `scripts/scan_data_risks.py` | 明文存储、日志泄露、弱加密、HTTP 传输 |
| 配置文件风险 | `scripts/check_privacy_config.py` | Cookie 设置、CORS、Session、JWT |

## 执行流程

### Phase 1：并行扫描（3个脚本同时运行）

```bash
python scripts/scan_pii.py <target> --output /tmp/pii_result.json
python scripts/scan_data_risks.py <target> --output /tmp/data_risks_result.json
python scripts/check_privacy_config.py <target> --output /tmp/config_result.json
```

### Phase 2：风险评估

读取三个 JSON 结果，按风险等级汇总：
- 🔴 **高风险**：需立即修复，可能已违反 PIPL/GDPR
- 🟡 **中风险**：需确认后处理，存在潜在合规问题
- 🟢 **低风险**：知悉即可，建议规范化

风险等级定义参见 `references/pipl-gdpr-mapping.md`

### Phase 3：生成报告

输出到 `privacy-scan/privacy-risk-report.md`，格式：

```markdown
# 数据隐私风险扫描报告
扫描时间：YYYY-MM-DD HH:MM
扫描目标：<path>

## 扫描摘要
| 风险等级 | 发现数量 |
|---------|---------|
| 🔴 高风险 | N 项 |
| 🟡 中风险 | N 项 |
| 🟢 低风险 | N 项 |

## 🔴 高风险问题
### [问题类型]
- **文件**：path/to/file.py:行号
- **问题**：发现手机号硬编码
- **内容**：`phone = "138xxxx1234"`
- **修复建议**：移除硬编码，改用环境变量或加密存储

## 🟡 中风险问题
...

## 🟢 低风险问题
...

## PIPL/GDPR 合规检查清单
- [ ] 用户同意机制（收集数据前获取明确授权）
- [ ] 数据最小化（只收集必要数据）
- [ ] 数据保留策略（明确数据删除周期）
- [ ] 第三方数据共享（明确告知用户）
- [ ] 用户删除权（支持用户申请删除数据）
```

## 技术栈支持

扫描支持混合技术栈，文件类型覆盖：
- **后端**：`.py`、`.js`、`.ts`、`.php`、`.go`、`.java`、`.rb`、`.cs`
- **前端**：`.jsx`、`.tsx`、`.vue`、`.svelte`、`.html`
- **配置**：`.env`、`.json`、`.yaml`、`.yml`、`.xml`、`.toml`
- **模板**：`.tpl`、`.ejs`、`.jinja2`

## 参考文档

- `references/pii-patterns.md` — PII 正则规则库及误报说明
- `references/pipl-gdpr-mapping.md` — PIPL vs GDPR 对照表及风险等级定义
