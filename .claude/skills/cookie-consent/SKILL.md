---
name: cookie-consent
description: 为 Next.js/React 项目实现 GDPR/PIPL 合规的 Cookie Consent Banner。生成前端同意弹窗组件（必要/分析/营销三类分组）、用户同意状态持久化、同意记录入库（Supabase）、以及与 GA4/PostHog 等分析工具的条件加载集成。应在 legal-docs-generator 生成 Cookie Policy 后执行，或在 dev-deploy 完成后、监控配置前执行。当用户提到"Cookie同意"、"Cookie Banner"、"Cookie Consent"、"GDPR Cookie"、"cookie-consent"、"用户同意弹窗"、"隐私同意"时触发。接入海外市场的项目上线前主动建议运行此 skill。
---

# Cookie Consent

为项目实现合规的 Cookie 同意机制，确保只在用户明确同意后才加载对应追踪脚本。

## 输出文件

```
src/
├── components/
│   └── CookieConsent.tsx       # 同意弹窗组件
├── lib/
│   └── cookie-consent.ts       # 同意状态管理
└── app/
    └── layout.tsx              # 注入弹窗（幂等修改）

supabase/migrations/
└── xxx_cookie_consent.sql      # 同意记录表（如使用 Supabase）
```

## Phase 0：扫描项目

```bash
# 检测框架和分析工具
cat package.json | grep -E "next|react|ga4|posthog|mixpanel|gtm"
grep -r "GoogleAnalytics\|PostHog\|gtag\|_ga" src/ --include="*.tsx" -l 2>/dev/null
cat src/app/layout.tsx 2>/dev/null | head -60
```

确认：
- 框架：Next.js App Router / Pages Router / React SPA
- 使用的分析工具：GA4 / PostHog / GTM / 其他
- 数据库：Supabase / 无（仅 localStorage）
- 目标市场：欧盟（GDPR 强制）/ 全球

## Phase 1：生成同意弹窗组件

### 同意分类

| 类别 | 说明 | 默认状态 |
|------|------|---------|
| `necessary` | 登录、CSRF、会话 — 无需同意 | 始终开启，不可关闭 |
| `analytics` | GA4、PostHog、行为分析 | 默认关闭 |
| `marketing` | 广告追踪、再营销像素 | 默认关闭 |

### CookieConsent.tsx

```tsx
'use client'

import { useState, useEffect } from 'react'
import { getConsent, saveConsent, type ConsentState } from '@/lib/cookie-consent'

export default function CookieConsent() {
  const [show, setShow] = useState(false)
  const [showDetails, setShowDetails] = useState(false)
  const [consent, setConsent] = useState<ConsentState>({
    necessary: true,   // 始终 true，不可更改
    analytics: false,
    marketing: false,
  })

  useEffect(() => {
    const saved = getConsent()
    if (!saved) setShow(true)  // 未同意过，显示弹窗
    else setConsent(saved)
  }, [])

  const handleAcceptAll = () => {
    const all = { necessary: true, analytics: true, marketing: true }
    saveConsent(all)
    setConsent(all)
    setShow(false)
  }

  const handleRejectAll = () => {
    const min = { necessary: true, analytics: false, marketing: false }
    saveConsent(min)
    setConsent(min)
    setShow(false)
  }

  const handleSavePreferences = () => {
    saveConsent(consent)
    setShow(false)
  }

  if (!show) return null

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 bg-white border-t shadow-lg md:bottom-4 md:left-4 md:right-auto md:max-w-md md:rounded-lg md:border">
      <p className="text-sm text-gray-700 mb-3">
        我们使用 Cookie 提升您的使用体验。点击"全部接受"即表示您同意我们的{' '}
        <a href="/legal/cookie-policy" className="underline">Cookie 政策</a>。
      </p>

      {showDetails && (
        <div className="mb-3 space-y-2 text-sm">
          <label className="flex items-center gap-2 text-gray-500">
            <input type="checkbox" checked disabled /> 必要 Cookie（始终开启）
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={consent.analytics}
              onChange={e => setConsent(c => ({ ...c, analytics: e.target.checked }))}
            />
            分析 Cookie（GA4、PostHog）
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={consent.marketing}
              onChange={e => setConsent(c => ({ ...c, marketing: e.target.checked }))}
            />
            营销 Cookie（广告追踪）
          </label>
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        <button onClick={handleAcceptAll}
          className="px-4 py-2 text-sm bg-black text-white rounded hover:bg-gray-800">
          全部接受
        </button>
        <button onClick={handleRejectAll}
          className="px-4 py-2 text-sm border rounded hover:bg-gray-50">
          仅必要
        </button>
        <button onClick={() => showDetails ? handleSavePreferences() : setShowDetails(true)}
          className="px-4 py-2 text-sm text-gray-600 hover:underline">
          {showDetails ? '保存设置' : '自定义'}
        </button>
      </div>
    </div>
  )
}
```

### cookie-consent.ts

```typescript
export type ConsentState = {
  necessary: boolean
  analytics: boolean
  marketing: boolean
}

const STORAGE_KEY = 'cookie_consent'
const CONSENT_VERSION = '1'  // 更新版本号可强制重新弹出同意

export function getConsent(): ConsentState | null {
  if (typeof window === 'undefined') return null
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    // 版本变更时强制重新同意
    if (parsed.version !== CONSENT_VERSION) return null
    return parsed.consent as ConsentState
  } catch {
    return null
  }
}

export function saveConsent(consent: ConsentState): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    version: CONSENT_VERSION,
    consent,
    timestamp: new Date().toISOString(),
  }))
  // 触发自定义事件，让分析工具按需加载
  window.dispatchEvent(new CustomEvent('consent-updated', { detail: consent }))
  // 如有 Supabase，异步记录（不阻塞 UI）
  recordConsentToDb(consent).catch(console.error)
}

async function recordConsentToDb(consent: ConsentState): Promise<void> {
  // 仅在有 Supabase 时记录，匿名记录无需用户 ID
  try {
    await fetch('/api/consent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        consent,
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString(),
      }),
    })
  } catch {
    // 静默失败，不影响用户体验
  }
}

export function hasAnalyticsConsent(): boolean {
  return getConsent()?.analytics ?? false
}

export function hasMarketingConsent(): boolean {
  return getConsent()?.marketing ?? false
}
```

## Phase 2：条件加载分析工具

在 `layout.tsx` 中，只在用户同意后才加载追踪脚本：

```tsx
// 监听同意事件，条件加载 GA4
useEffect(() => {
  const handleConsent = (e: CustomEvent<ConsentState>) => {
    if (e.detail.analytics && !window.gtag) {
      // 动态加载 GA4
      const script = document.createElement('script')
      script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`
      script.async = true
      document.head.appendChild(script)
    }
  }
  window.addEventListener('consent-updated', handleConsent as EventListener)
  return () => window.removeEventListener('consent-updated', handleConsent as EventListener)
}, [])
```

## Phase 3：同意记录入库（可选，Supabase）

```sql
-- supabase/migrations/xxx_cookie_consent.sql
create table if not exists cookie_consents (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid references auth.users(id) on delete set null,  -- 可为空（匿名记录）
  necessary   boolean not null default true,
  analytics   boolean not null default false,
  marketing   boolean not null default false,
  user_agent  text,
  ip_address  inet,
  created_at  timestamptz not null default now()
);

-- 保留 2 年（GDPR 要求能证明同意历史）
comment on table cookie_consents is 'GDPR/PIPL cookie consent audit log. Retain for 2 years.';
```

如不使用 Supabase，仅用 localStorage 也满足基本合规要求；数据库记录是为了有审计证明。

## Phase 4：允许用户撤回同意

在隐私设置页面或 Footer 添加"管理 Cookie 设置"链接，点击后重新显示弹窗：

```tsx
// 在任意位置触发重新显示
<button onClick={() => {
  localStorage.removeItem('cookie_consent')
  window.location.reload()
}}>
  管理 Cookie 设置
</button>
```

## 注意事项

- **GDPR 要求**：页面加载时不能预先勾选分析/营销 Cookie，必须用户主动同意
- **PIPL 要求**：同意必须是明确、主动的行为，不能用"继续使用即视为同意"
- **必要 Cookie 豁免**：登录状态、CSRF token 等无需同意即可设置
- **同意记录**：建议保留同意时间戳和版本号，作为合规审计证明
