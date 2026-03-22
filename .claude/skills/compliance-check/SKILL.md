---
name: compliance-check
description: 合规前置设计。在技术方案阶段（tech-solution 之后、dev-planner 之前）输出具体的合规技术要求，让开发阶段从一开始就把合规设计进去，而不是开发完再补救。输出：PII 字段加密方案、数据保留期配置、用户数据删除接口设计、审计日志表结构、同意记录设计。覆盖 PIPL（个人信息保护法）、GDPR、开源协议、第三方依赖合规性。应在 tech-solution 完成后、dev-planner 之前执行。当用户提到"合规设计"、"合规前置"、"PIPL"、"GDPR合规设计"、"数据合规"、"合规文档"、"合规报告"、"法律合规"、"数据保留"、"PII加密"、"compliance-check"时触发。所有涉及用户数据的项目，在开发前主动建议运行此 skill。
---

# Compliance Check — 合规前置设计

在开发开始之前明确合规技术要求，避免开发完成后大规模返工。

## 输出文件

```
Compliance/
├── compliance-design.md    # 合规技术设计（主文档）
├── pii-fields.md           # PII 字段清单和加密方案
├── data-retention.md       # 数据保留期和清理策略
├── user-rights-api.md      # 用户权利接口设计
└── audit-log-schema.md     # 审计日志表结构
```

## Phase 0：扫描项目

先从已有文档中提取信息，减少向用户询问：

```bash
# 读取技术方案和 PRD
ls PRD/ TechSolution/ docs/ 2>/dev/null
cat TechSolution/backend/data-design.md 2>/dev/null
cat PRD/*.md 2>/dev/null | head -100
```

从文档中提取：目标市场、用户数据类型、技术栈、第三方服务。

仅询问无法推断的信息：
- 主要目标市场（中国 / 欧盟 / 美国 / 全球）
- 是否处理支付信息
- 是否有未成年人用户

## Phase 1：PII 字段加密方案

识别数据库中所有 PII 字段，为每类字段指定处理策略：

| 字段类型 | 示例 | 处理策略 |
|---------|------|---------|
| 直接标识符 | 姓名、邮箱、手机号 | 存储时加密（AES-256），查询时解密 |
| 准标识符 | 生日、性别、地区 | 粗粒度存储（年份、省份），不存精确值 |
| 敏感信息 | 身份证、银行卡、密码 | 单向哈希（密码）或加密存储 + 单独同意 |
| 行为数据 | 浏览记录、点击流 | 匿名化（user_id 而非真实身份） |
| 支付信息 | 卡号 | 不存储原始值，仅存 token（Stripe/微信支付托管） |

**输出 `pii-fields.md`**，格式：

```markdown
## PII 字段清单

| 表名 | 字段名 | 数据类型 | PII 分类 | 加密方式 | 保留期 |
|------|--------|---------|---------|---------|--------|
| users | email | varchar | 直接标识符 | AES-256 | 账号存续期 + 1年 |
| users | phone | varchar | 直接标识符 | AES-256 | 账号存续期 + 1年 |
| orders | address | text | 直接标识符 | AES-256 | 交易完成后 5年（财务合规）|
```

**加密实现建议（Node.js）：**

```typescript
// lib/encryption.ts
import { createCipheriv, createDecipheriv, randomBytes } from 'crypto'

const ALGORITHM = 'aes-256-gcm'
const KEY = Buffer.from(process.env.ENCRYPTION_KEY!, 'hex')  // 32 bytes，存 Secret

export function encrypt(plaintext: string): string {
  const iv = randomBytes(16)
  const cipher = createCipheriv(ALGORITHM, KEY, iv)
  const encrypted = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()])
  const tag = cipher.getAuthTag()
  return `${iv.toString('hex')}:${tag.toString('hex')}:${encrypted.toString('hex')}`
}

export function decrypt(ciphertext: string): string {
  const [ivHex, tagHex, dataHex] = ciphertext.split(':')
  const decipher = createDecipheriv(ALGORITHM, KEY, Buffer.from(ivHex, 'hex'))
  decipher.setAuthTag(Buffer.from(tagHex, 'hex'))
  return decipher.update(Buffer.from(dataHex, 'hex')) + decipher.final('utf8')
}
```

## Phase 2：数据保留期配置

**输出 `data-retention.md`**，为每类数据指定保留期和清理机制：

| 数据类型 | 保留期 | 法规依据 | 清理方式 |
|---------|--------|---------|---------|
| 用户账号数据 | 账号存续期 + 1年 | PIPL 第 19 条 | 账号注销后定期批量删除 |
| 交易记录 | 5年 | 电子商务法第 51 条 | 归档后加密存储，不可查询 |
| 登录日志 | 6个月 | 网络安全法 | 自动过期删除 |
| 行为分析数据 | 2年 | GDPR Article 5 | 匿名化后可长期保留 |
| Cookie 同意记录 | 2年 | GDPR 举证要求 | 保留原始记录，不可删除 |

**定时清理任务（Cron）：**

```typescript
// 每天凌晨 2 点清理过期数据
// cron: '0 2 * * *'
async function cleanExpiredData() {
  const cutoff = new Date()
  cutoff.setFullYear(cutoff.getFullYear() - 1)

  await db.query(`
    DELETE FROM user_activity_logs
    WHERE created_at < $1
      AND user_id IN (SELECT id FROM users WHERE deleted_at IS NOT NULL)
  `, [cutoff])
}
```

## Phase 3：用户权利接口设计

**输出 `user-rights-api.md`**，PIPL 和 GDPR 要求提供以下接口：

```
GET  /api/user/data-export     # 数据导出（右利：查阅+可携带性）
PUT  /api/user/data-correct    # 数据更正
POST /api/user/data-delete     # 账号注销 + 数据删除（右利：删除权）
GET  /api/user/data-processing # 查看数据处理记录
POST /api/user/consent         # 更新同意状态
```

**删除接口设计要点：**

```typescript
// POST /api/user/data-delete
async function deleteUserData(userId: string) {
  // 1. 软删除账号（标记 deleted_at）
  await db.users.update({ deleted_at: new Date() }, { where: { id: userId } })

  // 2. 立即匿名化 PII（不等定时任务）
  await db.users.update({
    email: `deleted_${userId}@deleted.invalid`,
    phone: null,
    name: '已注销用户',
  }, { where: { id: userId } })

  // 3. 保留交易记录（财务合规要求，仅匿名化关联）
  await db.orders.update({ user_id: null }, { where: { user_id: userId } })

  // 4. 删除行为数据
  await db.activity_logs.destroy({ where: { user_id: userId } })

  // 5. 记录删除操作（审计日志）
  await auditLog('user_deleted', { userId, timestamp: new Date() })
}
```

## Phase 4：审计日志表结构

**输出 `audit-log-schema.md`**：

```sql
-- 审计日志表（不可删除、只追加）
CREATE TABLE audit_logs (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type  varchar(100) NOT NULL,  -- 'user_deleted', 'data_exported', 'consent_updated'
  actor_id    uuid,                   -- 操作者 user_id（系统操作为 null）
  target_id   uuid,                   -- 被操作的对象 ID
  target_type varchar(50),            -- 'user', 'order', 'document'
  metadata    jsonb,                  -- 操作详情（不含 PII）
  ip_address  inet,
  user_agent  text,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- 禁止删除（仅追加）
-- 通过 RLS 或应用层控制：无 DELETE 权限
-- 保留期：5年（财务+法律合规）
COMMENT ON TABLE audit_logs IS 'Immutable audit trail. Retain 5 years. No DELETE allowed.';
```

## Phase 5：开源协议合规

扫描 `package.json` 中的依赖，识别高风险协议：

```bash
npx license-checker --summary 2>/dev/null || \
  cat package.json | python3 -c "
import sys, json
d = json.load(sys.stdin)
deps = {**d.get('dependencies',{}), **d.get('devDependencies',{})}
print('\n'.join(deps.keys()))
"
```

| 协议 | 商用风险 | 处理建议 |
|------|---------|---------|
| MIT / Apache 2.0 / BSD | 无风险 | 保留原始版权声明即可 |
| LGPL | 低风险 | 动态链接可闭源，检查链接方式 |
| GPL / AGPL | 高风险 | 衍生代码需开源，必须替换或获得商业授权 |
| 自定义协议 | 需人工确认 | 逐条阅读条款 |

## 输出汇总

生成完成后，输出一份给 dev-planner 的合规要求清单：

```markdown
## 合规技术要求（传递给开发阶段）

### 必须实现
- [ ] 加密工具库（lib/encryption.ts）
- [ ] 用户注销接口（软删除 + PII 匿名化）
- [ ] 数据导出接口（GDPR 数据可携带性）
- [ ] 审计日志表（只追加，5年保留）
- [ ] 数据保留期定时清理 Cron Job

### 数据库 Schema 要求
- users 表：email/phone 字段加密存储
- 所有表：added deleted_at 软删除字段
- audit_logs 表：只追加，禁止删除

### 第三方服务
- [依赖包名]：需替换（GPL 协议）
```

## 与其他 skill 的关系

- **之前**：`tech-solution`（需要数据库设计作为输入）
- **之后**：`dev-planner`（将合规要求作为模块纳入开发计划）
- **配合**：`privacy-scanner`（开发完成后扫描实现是否符合本文档设计）
- **配合**：`legal-docs-generator`（生成面向用户的隐私政策等法律文件）
