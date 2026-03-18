# Vue SPA / 通用 HTML — SEO 实现参考

> 适用于无 SSR 的 Vue SPA、React SPA 或纯 HTML 站点。
> 注意：纯 SPA 对搜索引擎不友好，建议考虑升级到 SSR（Nuxt/Next.js）。

## Meta Tags：vue-meta 或 @vueuse/head

### Vue 3 + @vueuse/head

安装：
```bash
npm install @vueuse/head
```

`main.ts`：
```typescript
import { createHead } from '@vueuse/head'
const head = createHead()
app.use(head)
```

`App.vue`（全局默认）：
```vue
<script setup>
import { useHead } from '@vueuse/head'

useHead({
  title: '网站名称',
  meta: [
    { name: 'description', content: '网站描述' },
    { property: 'og:title', content: '网站名称' },
    { property: 'og:description', content: '网站描述' },
    { property: 'og:image', content: 'https://DOMAIN/og-default.png' },
    { property: 'og:type', content: 'website' },
    { name: 'twitter:card', content: 'summary_large_image' },
  ],
  link: [
    { rel: 'canonical', href: 'https://DOMAIN' },
    { rel: 'alternate', hreflang: 'zh-CN', href: 'https://DOMAIN/zh' },
    { rel: 'alternate', hreflang: 'en', href: 'https://DOMAIN/en' },
  ],
})
</script>
```

---

## sitemap.xml：静态生成

对于 SPA，sitemap 通常在构建时生成（静态文件）。

使用 `vite-plugin-sitemap`：
```bash
npm install vite-plugin-sitemap
```

`vite.config.ts`：
```typescript
import Sitemap from 'vite-plugin-sitemap'

export default defineConfig({
  plugins: [
    Sitemap({
      hostname: 'https://DOMAIN',
      dynamicRoutes: ['/zh', '/en', '/zh/about', '/en/about'],
      outDir: 'dist',
    }),
  ],
})
```

或手动创建 `public/sitemap.xml`：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://DOMAIN/zh</loc>
    <xhtml:link rel="alternate" hreflang="zh-CN" href="https://DOMAIN/zh"/>
    <xhtml:link rel="alternate" hreflang="en" href="https://DOMAIN/en"/>
    <lastmod>2026-03-17</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <!-- 更多页面... -->
</urlset>
```

---

## robots.txt：public/robots.txt

```
User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/

Sitemap: https://DOMAIN/sitemap.xml
```

---

## JSON-LD：index.html

在 `index.html` 的 `<head>` 中添加：

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "name": "网站名称",
      "url": "https://DOMAIN"
    },
    {
      "@type": "Organization",
      "name": "组织名称",
      "url": "https://DOMAIN",
      "logo": "https://DOMAIN/logo.png"
    }
  ]
}
</script>
```

---

## SPA SEO 局限性说明

纯 SPA 的 meta tags 由 JavaScript 动态设置，部分搜索引擎爬虫可能无法正确抓取。建议：
1. 使用 `prerender.io` 或 `rendertron` 进行预渲染
2. 或迁移到 Nuxt（Vue）/ Next.js（React）以获得更好的 SEO
