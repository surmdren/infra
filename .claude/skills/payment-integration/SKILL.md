---
name: payment-integration
description: 为 SaaS 前端项目集成微信支付和 PayPal 支付能力。支持微信支付（JSAPI/Native扫码/H5支付）和 PayPal（Smart Buttons SDK/订单创建与捕获/Webhook验证）。包含前端支付组件、后端 API 端点、Webhook 处理、安全签名验证。适用场景：(1) SaaS 产品新增支付功能 (2) 同时接入国内（微信）和海外（PayPal）支付 (3) 订阅制或一次性付款场景。当用户提到"接入支付"、"微信支付"、"PayPal"、"支付集成"、"payment"、"收款"时触发。
---

# 支付集成

为 SaaS 项目同时接入微信支付和 PayPal，覆盖前端组件、后端 API、Webhook 处理。

## 工作流程

### Step 1: 确认支付场景
- 用户在哪个端？（PC / H5 / App 内嵌 WebView）
- 付款类型？（一次性 / 订阅）
- 需要哪些支付方式？（微信 / PayPal / 均需要）

### Step 2: 读取设计规范
读取 [references/payment-ui.md](references/payment-ui.md)，严格按规范实现支付 UI（按钮样式、品牌色、状态页）。

### Step 3: 实现后端
创建以下端点，详见对应 references：
- `POST /api/payment/create` — 创建订单
- `POST /api/payment/webhook/wechat` — 微信回调
- `POST /api/payment/webhook/paypal` — PayPal 回调
- `GET /api/payment/status/:orderId` — 查询状态

⚠️ **安全强制要求**：
- 签名必须在后端生成，绝不在前端暴露 `apiSecret` / `CLIENT_SECRET`
- Webhook 必须验证签名，拒绝伪造请求
- 订单金额以后端数据库为准，不信任前端传入

### Step 4: 实现前端组件
参考 `references/payment-ui.md` 实现：
- `<WechatPayButton />` — 微信支付按钮
- `<PayPalButton />` — PayPal Smart Button
- `<PaymentStatusPage />` — 三态（loading / success / failed）

### Step 5: 测试
- 微信：使用微信支付沙箱环境
- PayPal：使用 Sandbox 账号（developer.paypal.com）
- 必须覆盖：正常支付、取消支付、Webhook 延迟、重复 Webhook

## References

- **微信支付集成** → [references/wechat-pay.md](references/wechat-pay.md)（JSAPI/Native/H5、V3 API RSA 签名、AES-256-GCM Webhook 解密）
- **PayPal 集成** → [references/paypal.md](references/paypal.md)（Smart Buttons、Orders API、Webhook 验证、退款）
- **支付 UI 规范** → [references/payment-ui.md](references/payment-ui.md)（品牌色、按钮样式、状态页布局）

## 环境变量

```bash
# 微信支付 V3 API
NEXT_PUBLIC_WECHAT_APP_ID=wx...          # 公众号/小程序 AppID（前端可用）
WECHAT_MCH_ID=1234567890                 # 商户号
WECHAT_API_V3_KEY=...                    # V3 密钥（32字节，用于解密 Webhook）
WECHAT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
                                         # RSA 私钥（用于请求签名，后端专用）
WECHAT_SERIAL_NO=...                     # 证书序列号（配合私钥使用）
NEXT_PUBLIC_WECHAT_NOTIFY_URL=https://{domain}/api/webhook/wechat

# PayPal
NEXT_PUBLIC_PAYPAL_CLIENT_ID=...         # 前端可用（Smart Buttons 初始化）
PAYPAL_CLIENT_ID=...                     # 后端用（与上面相同值）
PAYPAL_CLIENT_SECRET=...                 # 后端专用，严禁前端使用
PAYPAL_MODE=sandbox                      # sandbox | live
```
