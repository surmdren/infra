# Next.js Pages Router — SEO 实现参考

## Meta Tags：使用 next/head

### _document.tsx（全局默认）

```tsx
import { Html, Head, Main, NextScript } from 'next/document'

export default function Document() {
  return (
    <Html lang="zh-CN">
      <Head>
        <meta name="description" content="网站描述" />
        <meta property="og:type" content="website" />
        <meta property="og:site_name" content="网站名称" />
        <meta property="og:image" content="https://DOMAIN/og-default.png" />
        <meta name="twitter:card" content="summary_large_image" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  )
}
```

### 各页面（动态覆盖）

```tsx
import Head from 'next/head'

export default function Page() {
  return (
    <>
      <Head>
        <title>页面标题 | 网站名称</title>
        <meta name="description" content="页面描述" />
        <meta property="og:title" content="页面标题" />
        <meta property="og:description" content="页面描述" />
        <link rel="canonical" href="https://DOMAIN/page-path" />
        {/* hreflang */}
        <link rel="alternate" hrefLang="zh-CN" href="https://DOMAIN/zh/page-path" />
        <link rel="alternate" hrefLang="en" href="https://DOMAIN/en/page-path" />
        <link rel="alternate" hrefLang="x-default" href="https://DOMAIN/en/page-path" />
      </Head>
      {/* 页面内容 */}
    </>
  )
}
```

---

## sitemap.xml：next-sitemap

安装依赖：
```bash
npm install next-sitemap
```

创建 `next-sitemap.config.js`：

```javascript
/** @type {import('next-sitemap').IConfig} */
module.exports = {
  siteUrl: 'https://DOMAIN',
  generateRobotsTxt: true,
  robotsTxtOptions: {
    policies: [
      { userAgent: '*', allow: '/', disallow: ['/api/', '/admin/'] },
    ],
  },
  // 多语言支持
  alternateRefs: [
    { href: 'https://DOMAIN/zh', hreflang: 'zh-CN' },
    { href: 'https://DOMAIN/en', hreflang: 'en' },
  ],
}
```

在 `package.json` 中添加 postbuild 脚本：
```json
{
  "scripts": {
    "postbuild": "next-sitemap"
  }
}
```

---

## JSON-LD：注入 _document.tsx

在 `<Head>` 中添加：

```tsx
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify({
      '@context': 'https://schema.org',
      '@graph': [
        { '@type': 'WebSite', name: '网站名称', url: 'https://DOMAIN' },
        { '@type': 'Organization', name: '组织名称', url: 'https://DOMAIN', logo: 'https://DOMAIN/logo.png' },
      ],
    }),
  }}
/>
```
