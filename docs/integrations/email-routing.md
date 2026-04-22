# 自定义域名邮箱配置指南

## 方案概述

用 Cloudflare Email Routing（免费）替代付费邮箱服务（如 Namecheap Private Email）。

- **收件**：Cloudflare Email Routing 转发到 Gmail
- **发件**：Resend SMTP（SPF/DKIM 已配置）
- **成本**：免费（Resend 每月 3000 封免费）

## 前提条件

- 域名 DNS 托管在 Cloudflare
- 有 Gmail 账号作为收件目的地
- Resend API Key（见 `~/.dreamai-env` 中 `RESEND_API_KEY`）

---

## 第一步：Cloudflare Email Routing

### 1. 进入 Email Routing 页面

Cloudflare Dashboard → 选择域名 → Email → Email Routing

### 2. 完成向导

- **Custom address**：填写你要使用的前缀，如 `sales`
- **Destination**：填写 Gmail 地址（会发确认邮件，需点击验证）
- 点 **Create and continue**

### 3. 启用

如果提示 "Delete conflicting DNS records"（旧 MX/SPF 冲突），直接点 **"Add records and enable"**，Cloudflare 会自动：
- 删除旧 MX 记录（如 privateemail、zoho 等）
- 删除旧 SPF TXT 记录
- 添加 Cloudflare Email Routing 的 MX 记录（route1/2/3.mx.cloudflare.net）
- 添加新 SPF：`v=spf1 include:_spf.mx.cloudflare.net ~all`

### 4. 补充 Resend SPF

Cloudflare 自动生成的 SPF 只包含自己的，需要手动加上 Resend（否则 Resend 发件会被标为垃圾邮件）。

在 DNS → TXT 记录中，将 SPF 更新为：
```
v=spf1 include:_spf.mx.cloudflare.net include:_spf.resend.com ~all
```

或用 API（需要对应 zone 的 DNS Edit 权限）：
```bash
source ~/.dreamai-env
ZONE=<zone_id>
TOKEN=<cloudflare_token>

TXT_ID=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records?type=TXT&name=<domain>" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(r['id']) for r in d.get('result',[]) if 'spf' in r['content']]")

curl -s -X PATCH \
  "https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records/$TXT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"v=spf1 include:_spf.mx.cloudflare.net include:_spf.resend.com ~all"}'
```

---

## 第二步：Gmail 配置发件

Gmail → Settings → Accounts and Import → **Send mail as** → Add another email address

| 字段 | 值 |
|------|-----|
| Name | 品牌名（如 Wise Optics） |
| Email | `sales@yourdomain.com` |
| Treat as alias | 取消勾选 |
| SMTP Server | `smtp.resend.com` |
| Port | `587` |
| Username | `resend` |
| Password | `RESEND_API_KEY`（见 `~/.dreamai-env`） |
| Security | TLS |

点 Add Account 后，Gmail 会发一封验证邮件到 `sales@yourdomain.com`，该邮件会被 Cloudflare 转发到你的 Gmail，点确认链接即完成。

---

## 已配置的邮箱

| 地址 | 转发到 | 用途 |
|------|--------|------|
| sales@wise-optics.com | wiseopticscn@gmail.com | Wise Optics 销售 |

---

## 添加新邮箱地址（标准流程）

1. Cloudflare → 域名 → Email Routing → Routing rules → Add rule
2. Custom address 填前缀，Destination 选已验证的 Gmail（或添加新 Gmail）
3. Gmail 那边重复第二步操作
4. 更新上方已配置邮箱表格

---

## 注意事项

- Resend API Key 统一存放在 `~/.dreamai-env`，不同域名可共用同一个 Key
- 每个域名需要单独在 Resend 验证（Domain → Add Domain → 添加 DKIM 记录）
- `send.<domain>` 子域名的 MX（SES bounce）和 SPF 独立管理，不受影响
- Cloudflare Email Routing 免费版无限制转发规则，无需付费
