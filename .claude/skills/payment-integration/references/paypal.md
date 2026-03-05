# PayPal 集成指南

## Smart Buttons（前端）

```html
<!-- 在 HTML head 中加载 SDK，CLIENT_ID 前端可用 -->
<script src="https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID&currency=USD"></script>
```

```typescript
// React 组件
import { useEffect, useRef } from 'react'

declare const paypal: any

export function PayPalButton({ amount, orderId, onSuccess, onError }: {
  amount: string
  orderId: string
  onSuccess: (details: any) => void
  onError: (err: any) => void
}) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    paypal.Buttons({
      createOrder: async () => {
        // 调用后端创建 PayPal 订单
        const res = await fetch('/api/payment/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ provider: 'paypal', orderId, amount })
        })
        const { paypalOrderId } = await res.json()
        return paypalOrderId
      },
      onApprove: async (data: any) => {
        // 调用后端捕获订单
        const res = await fetch(`/api/payment/capture/${data.orderID}`, {
          method: 'POST'
        })
        const details = await res.json()
        onSuccess(details)
      },
      onError,
      onCancel: () => console.log('用户取消支付')
    }).render(containerRef.current)
  }, [])

  return <div ref={containerRef} />
}
```

## Orders API（后端）

```typescript
import fetch from 'node-fetch'

const PAYPAL_BASE = process.env.PAYPAL_MODE === 'live'
  ? 'https://api-m.paypal.com'
  : 'https://api-m.sandbox.paypal.com'

async function getPayPalAccessToken(): Promise<string> {
  const res = await fetch(`${PAYPAL_BASE}/v1/oauth2/token`, {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${Buffer.from(
        `${process.env.PAYPAL_CLIENT_ID}:${process.env.PAYPAL_CLIENT_SECRET}`
      ).toString('base64')}`,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: 'grant_type=client_credentials'
  })
  const { access_token } = await res.json() as any
  return access_token
}

// 创建订单
async function createPayPalOrder(amount: string, currency = 'USD') {
  const token = await getPayPalAccessToken()
  const res = await fetch(`${PAYPAL_BASE}/v2/checkout/orders`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      intent: 'CAPTURE',
      purchase_units: [{ amount: { currency_code: currency, value: amount } }]
    })
  })
  return res.json()
}

// 捕获订单（用户点击支付后）
async function capturePayPalOrder(paypalOrderId: string) {
  const token = await getPayPalAccessToken()
  const res = await fetch(`${PAYPAL_BASE}/v2/checkout/orders/${paypalOrderId}/capture`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
  })
  return res.json()
}
```

## Webhook 验证

```typescript
// POST /api/payment/webhook/paypal
import fetch from 'node-fetch'

async function verifyPayPalWebhook(
  headers: Record<string, string>,
  rawBody: string
): Promise<boolean> {
  const token = await getPayPalAccessToken()
  const res = await fetch(`${PAYPAL_BASE}/v1/notifications/verify-webhook-signature`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      auth_algo: headers['paypal-auth-algo'],
      cert_url: headers['paypal-cert-url'],
      transmission_id: headers['paypal-transmission-id'],
      transmission_sig: headers['paypal-transmission-sig'],
      transmission_time: headers['paypal-transmission-time'],
      webhook_id: process.env.PAYPAL_WEBHOOK_ID,
      webhook_event: JSON.parse(rawBody)
    })
  })
  const { verification_status } = await res.json() as any
  return verification_status === 'SUCCESS'
}

async function handlePayPalWebhook(headers: Record<string, string>, rawBody: string) {
  const isValid = await verifyPayPalWebhook(headers, rawBody)
  if (!isValid) throw new Error('PayPal Webhook 签名验证失败')

  const event = JSON.parse(rawBody)
  if (event.event_type === 'PAYMENT.CAPTURE.COMPLETED') {
    const orderId = event.resource.custom_id // 你的业务订单号
    // 幂等检查 + 更新订单状态
  }
}
```

## 退款

```typescript
async function refundPayPalCapture(captureId: string, amount?: string) {
  const token = await getPayPalAccessToken()
  const body = amount
    ? JSON.stringify({ amount: { value: amount, currency_code: 'USD' } })
    : '{}'  // 不传 amount 则全额退款
  const res = await fetch(`${PAYPAL_BASE}/v2/payments/captures/${captureId}/refund`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body
  })
  return res.json()
}
```
