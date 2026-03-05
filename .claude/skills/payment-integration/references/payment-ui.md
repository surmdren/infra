# 支付 UI 规范

## 品牌色

| 支付方式 | 主色 | 辅色 | 文字色 |
|---------|------|------|--------|
| 微信支付 | `#07C160` | `#06AD56` | `#FFFFFF` |
| PayPal | `#003087` | `#009CDE` | `#FFFFFF` |
| 通用成功 | `#52C41A` | — | `#FFFFFF` |
| 通用失败 | `#FF4D4F` | — | `#FFFFFF` |

## 支付按钮规范

```tsx
// 微信支付按钮
<button
  className="flex items-center justify-center gap-2 w-full h-12 rounded-lg font-medium text-white"
  style={{ backgroundColor: '#07C160' }}
>
  <WechatIcon className="w-5 h-5" />
  微信支付
</button>

// PayPal 按钮（使用官方 Smart Buttons，禁止自定义 PayPal 按钮样式）
// PayPal Smart Buttons 已内置品牌规范，直接渲染即可
<div id="paypal-button-container" />
```

⚠️ PayPal 官方要求使用 Smart Buttons，不得自行设计 PayPal 按钮样式。

## 支付状态页布局

### Loading（支付中）
```tsx
<div className="flex flex-col items-center justify-center min-h-[300px] gap-4">
  <Spinner className="w-12 h-12 text-blue-500 animate-spin" />
  <p className="text-gray-600 text-lg">支付处理中，请稍候...</p>
  <p className="text-gray-400 text-sm">请勿关闭页面</p>
</div>
```

### Success（支付成功）
```tsx
<div className="flex flex-col items-center justify-center min-h-[300px] gap-4">
  <CheckCircleIcon className="w-16 h-16" style={{ color: '#52C41A' }} />
  <h2 className="text-2xl font-semibold text-gray-800">支付成功</h2>
  <p className="text-gray-500">订单号：{orderId}</p>
  <button className="mt-4 px-6 py-2 bg-blue-500 text-white rounded-lg">
    查看订单
  </button>
</div>
```

### Failed（支付失败）
```tsx
<div className="flex flex-col items-center justify-center min-h-[300px] gap-4">
  <XCircleIcon className="w-16 h-16" style={{ color: '#FF4D4F' }} />
  <h2 className="text-2xl font-semibold text-gray-800">支付失败</h2>
  <p className="text-gray-500">{errorMessage}</p>
  <div className="flex gap-3 mt-4">
    <button className="px-6 py-2 border border-gray-300 rounded-lg">返回</button>
    <button className="px-6 py-2 bg-blue-500 text-white rounded-lg">重新支付</button>
  </div>
</div>
```

## 支付选择页布局

```tsx
// 当同时支持微信和 PayPal 时，提供选择卡片
<div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-lg mx-auto">
  <PaymentCard
    provider="wechat"
    icon={<WechatIcon />}
    label="微信支付"
    description="支持国内用户"
    accentColor="#07C160"
    onClick={() => setProvider('wechat')}
  />
  <PaymentCard
    provider="paypal"
    icon={<PayPalIcon />}
    label="PayPal"
    description="支持国际信用卡"
    accentColor="#003087"
    onClick={() => setProvider('paypal')}
  />
</div>
```

## 响应式规范

- 移动端（< 768px）：按钮全宽，状态页垂直居中
- 桌面端（≥ 768px）：最大宽度 480px，水平居中
- 支付弹窗：移动端底部 Sheet，桌面端居中 Modal（最大宽度 500px）
