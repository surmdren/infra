# 微信支付 V3 API 集成指南

> 使用微信支付 API V3（JSON + RSA 签名），非旧版 V2（XML + MD5）。

## 支付模式选择

| 场景 | 模式 | API |
|------|------|-----|
| 微信内置浏览器 | JSAPI | `/v3/pay/transactions/jsapi` |
| PC 网页 | Native（扫码）| `/v3/pay/transactions/native` |
| 外部手机浏览器 | H5 支付 | `/v3/pay/transactions/h5` |

## 依赖安装

```bash
npm install wechatpay-node-v3
```

## 初始化客户端

```typescript
// lib/wechat-pay.ts
import WxPay from 'wechatpay-node-v3'
import fs from 'fs'

export const wxpay = new WxPay({
  appid: process.env.NEXT_PUBLIC_WECHAT_APP_ID!,
  mchid: process.env.WECHAT_MCH_ID!,
  privateKey: process.env.WECHAT_PRIVATE_KEY!,  // RSA 私钥
  serial_no: process.env.WECHAT_SERIAL_NO!,     // 证书序列号
  apiV3Key: process.env.WECHAT_API_V3_KEY!,     // V3 密钥（解密用）
  notify_url: process.env.NEXT_PUBLIC_WECHAT_NOTIFY_URL!,
})
```

## JSAPI 支付

### 后端：创建订单
```typescript
// POST /api/payment/create (微信 JSAPI)
export async function createWechatJSAPIOrder(params: {
  orderId: string
  amount: number     // 元为单位，内部转换为分
  openid: string
  description: string
}) {
  const result = await wxpay.transactions_jsapi({
    description: params.description,
    out_trade_no: params.orderId,
    amount: { total: Math.round(params.amount * 100), currency: 'CNY' },
    payer: { openid: params.openid },
  })
  // result.data 包含 prepay_id，传给前端调起支付
  return result.data
}
```

### 前端：唤起支付
```typescript
declare const WeixinJSBridge: any

async function invokeWechatPay(orderId: string) {
  // 从后端获取支付参数
  const res = await fetch('/api/payment/create', {
    method: 'POST',
    body: JSON.stringify({ provider: 'wechat', orderId })
  })
  const payParams = await res.json()

  WeixinJSBridge.invoke('getBrandWCPayRequest', payParams, (result: any) => {
    if (result.err_msg === 'get_brand_wcpay_request:ok') {
      // 支付成功（仍需等 Webhook 最终确认）
    }
  })
}
```

## Native 支付（PC扫码）

```typescript
// 后端返回 code_url，前端生成二维码
const result = await wxpay.transactions_native({
  description: '商品描述',
  out_trade_no: orderId,
  amount: { total: Math.round(amount * 100), currency: 'CNY' },
})
const codeUrl = result.data.code_url  // 传给前端

// 前端轮询订单状态（每2秒，最多5分钟）
function pollOrderStatus(orderId: string) {
  const timer = setInterval(async () => {
    const { status } = await fetch(`/api/payment/status/${orderId}`).then(r => r.json())
    if (status === 'paid') { clearInterval(timer); /* 跳转成功页 */ }
  }, 2000)
  setTimeout(() => clearInterval(timer), 300_000)
}
```

## H5 支付

```typescript
// 后端
const result = await wxpay.transactions_h5({
  description: '商品描述',
  out_trade_no: orderId,
  amount: { total: Math.round(amount * 100), currency: 'CNY' },
  scene_info: {
    payer_client_ip: clientIp,
    h5_info: { type: 'Wap' }
  }
})
const mwebUrl = result.data.h5_url

// 前端直接跳转
window.location.href = mwebUrl + '&redirect_url=' + encodeURIComponent(window.location.href)
```

## Webhook 验证与解密（V3）

V3 Webhook 使用 **AES-256-GCM** 加密，`wechatpay-node-v3` 库已封装解密逻辑：

```typescript
// POST /api/webhook/wechat
import { headers } from 'next/headers'

export async function POST(req: Request) {
  const rawBody = await req.text()
  const headersList = headers()

  // 1. 验证签名（wechatpay-node-v3 内部处理）
  const signature = headersList.get('wechatpay-signature')
  const timestamp = headersList.get('wechatpay-timestamp')
  const nonce = headersList.get('wechatpay-nonce')
  const serial = headersList.get('wechatpay-serial')

  const verifyResult = await wxpay.verifySign({
    timestamp: timestamp!,
    nonce: nonce!,
    body: rawBody,
    serial: serial!,
    signature: signature!,
  })

  if (!verifyResult) {
    return new Response('签名验证失败', { status: 401 })
  }

  // 2. 解密通知内容
  const event = JSON.parse(rawBody)
  const resource = event.resource
  const decrypted = wxpay.decipher_gcm(
    resource.ciphertext,
    resource.associated_data,
    resource.nonce,
    process.env.WECHAT_API_V3_KEY!
  )
  const paymentData = JSON.parse(decrypted)

  // 3. 幂等检查（防重复处理）
  const orderId = paymentData.out_trade_no
  // 查数据库，若已处理则直接返回成功

  // 4. 验证金额
  const paidAmount = paymentData.amount.total / 100  // 分转元

  // 5. 更新订单状态
  if (paymentData.trade_state === 'SUCCESS') {
    // await updateOrderStatus(orderId, 'paid')
  }

  return new Response(JSON.stringify({ code: 'SUCCESS', message: '成功' }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
```

## 查询订单状态

```typescript
// GET /api/payment/status/:orderId
const result = await wxpay.query({ out_trade_no: orderId })
// result.data.trade_state: SUCCESS | NOTPAY | CLOSED | REFUND
```

## 退款

```typescript
await wxpay.refunds({
  out_trade_no: orderId,
  out_refund_no: `refund_${orderId}`,
  reason: '用户申请退款',
  amount: {
    refund: Math.round(refundAmount * 100),
    total: Math.round(totalAmount * 100),
    currency: 'CNY'
  }
})
```
