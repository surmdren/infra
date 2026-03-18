# Next.js App Router — SEO 实现参考

## Meta Tags：使用 Metadata API

### 静态 metadata（根 layout）

在 `app/layout.tsx` 中导出 `metadata` 对象：

```typescript
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: {
    default: '网站名称',
    template: '%s | 网站名称',
  },
  description: '网站描述',
  openGraph: {
    type: 'website',
    siteName: '网站名称',
    title: '网站名称',
    description: '网站描述',
    images: [{ url: '/og-default.png', width: 1200, height: 630 }],
  },
  twitter: {
    card: 'summary_large_image',
    title: '网站名称',
    description: '网站描述',
    images: ['/og-default.png'],
  },
  alternates: {
    canonical: 'https://DOMAIN',
    languages: {
      'zh-CN': 'https://DOMAIN/zh',
      'en': 'https://DOMAIN/en',
      // 按实际支持语言列表填写
    },
  },
  robots: {
    index: true,
    follow: true,
  },
}
```

### 动态 metadata（各页面）

在需要个性化 SEO 的页面中使用 `generateMetadata`：

```typescript
export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  return {
    title: '页面标题',
    description: '页面描述',
    alternates: {
      canonical: `https://DOMAIN/${params.slug}`,
      languages: {
        'zh-CN': `https://DOMAIN/zh/${params.slug}`,
        'en': `https://DOMAIN/en/${params.slug}`,
      },
    },
  }
}
```

---

## sitemap.xml：app/sitemap.ts

```typescript
import { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://DOMAIN'
  const languages = ['zh', 'en'] // 从 i18n 配置读取

  const pages = ['', '/about', '/pricing'] // 所有公开页面

  return pages.flatMap((page) =>
    languages.map((lang) => ({
      url: `${baseUrl}/${lang}${page}`,
      lastModified: new Date(),
      changeFrequency: page === '' ? 'daily' : 'weekly',
      priority: page === '' ? 1.0 : 0.8,
      alternates: {
        languages: Object.fromEntries(
          languages.map((l) => [l, `${baseUrl}/${l}${page}`])
        ),
      },
    }))
  )
}
```

---

## robots.txt：app/robots.ts

```typescript
import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/api/', '/admin/'],
    },
    sitemap: 'https://DOMAIN/sitemap.xml',
  }
}
```

---

## JSON-LD：注入 layout.tsx

在 `app/layout.tsx` 的 `<body>` 内添加：

```typescript
const jsonLd = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'WebSite',
      name: '网站名称',
      url: 'https://DOMAIN',
    },
    {
      '@type': 'Organization',
      name: '组织名称',
      url: 'https://DOMAIN',
      logo: 'https://DOMAIN/logo.png',
    },
  ],
}

// 在 <body> 中：
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
/>
```
