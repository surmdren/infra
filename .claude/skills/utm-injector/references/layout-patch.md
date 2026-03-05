# layout.tsx 注入参考

`app/layout.tsx` 中注入 UTM 捕获和分析初始化的标准方式。

## 方式一：Client Component 包装（推荐）

创建 `components/analytics-provider.tsx`：

```tsx
'use client'

import { useEffect } from 'react'
import { captureUTM } from '@/lib/utm'
import { initAnalytics, trackEvent } from '@/lib/analytics'

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    initAnalytics()
    captureUTM()
    trackEvent('session_started')
  }, [])

  return <>{children}</>
}
```

在 `app/layout.tsx` 中使用：

```tsx
import { AnalyticsProvider } from '@/components/analytics-provider'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        {/* GA4 Script */}
        <script
          async
          src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}`}
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', '${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}');
            `,
          }}
        />
      </head>
      <body>
        <AnalyticsProvider>
          {children}
        </AnalyticsProvider>
      </body>
    </html>
  )
}
```

## 方式二：Next.js Script 组件（适合纯 Server Component layout）

```tsx
import Script from 'next/script'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        {/* GA4 */}
        <Script
          src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}`}
          strategy="afterInteractive"
        />
        <Script id="ga4-init" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}');
          `}
        </Script>
        {/* UTM + PostHog 初始化 */}
        <Script id="analytics-init" strategy="afterInteractive">
          {`
            // PostHog 和 UTM 初始化由 AnalyticsProvider Client Component 处理
          `}
        </Script>
      </body>
    </html>
  )
}
```

## 注入检查

注入前用以下模式检测是否已存在：

```bash
grep -q "captureUTM\|initAnalytics\|AnalyticsProvider" app/layout.tsx
```

- 如果返回 0（找到匹配），说明已注入，跳过
- 如果返回 1（未找到），执行注入

## auth 回调中注入 saveUserUTM

在用户注册成功后（Supabase auth callback 或 sign-up handler）调用：

```typescript
import { saveUserUTM } from '@/lib/utm'
import { identifyUser } from '@/lib/analytics'

// 注册成功后
const { data: { user } } = await supabase.auth.signUp({ email, password })
if (user) {
  await saveUserUTM(user.id)
  identifyUser(user.id, { email: user.email })
  trackEvent('signup_completed', { method: 'email' })
}
```
