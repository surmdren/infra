# Nuxt — SEO 实现参考

## Meta Tags：useSeoMeta + useHead

### app.vue 或 layouts/default.vue（全局默认）

```vue
<script setup lang="ts">
useSeoMeta({
  title: '网站名称',
  description: '网站描述',
  ogTitle: '网站名称',
  ogDescription: '网站描述',
  ogImage: 'https://DOMAIN/og-default.png',
  ogType: 'website',
  ogSiteName: '网站名称',
  twitterCard: 'summary_large_image',
  twitterTitle: '网站名称',
  twitterDescription: '网站描述',
  twitterImage: 'https://DOMAIN/og-default.png',
})

useHead({
  link: [
    { rel: 'canonical', href: 'https://DOMAIN' },
    // hreflang（多语言）
    { rel: 'alternate', hreflang: 'zh-CN', href: 'https://DOMAIN/zh' },
    { rel: 'alternate', hreflang: 'en', href: 'https://DOMAIN/en' },
    { rel: 'alternate', hreflang: 'x-default', href: 'https://DOMAIN/en' },
  ],
})
</script>
```

### 各页面（动态覆盖）

```vue
<script setup lang="ts">
const route = useRoute()

useSeoMeta({
  title: '页面标题',
  description: '页面描述',
})

useHead({
  link: [
    { rel: 'canonical', href: `https://DOMAIN${route.path}` },
    { rel: 'alternate', hreflang: 'zh-CN', href: `https://DOMAIN/zh${route.path.replace(/^\/[a-z]{2}/, '')}` },
    { rel: 'alternate', hreflang: 'en', href: `https://DOMAIN/en${route.path.replace(/^\/[a-z]{2}/, '')}` },
  ],
})
</script>
```

---

## sitemap.xml：@nuxtjs/sitemap

安装：
```bash
npm install @nuxtjs/sitemap
```

`nuxt.config.ts`：

```typescript
export default defineNuxtConfig({
  modules: ['@nuxtjs/sitemap'],
  site: {
    url: 'https://DOMAIN',
    name: '网站名称',
  },
  sitemap: {
    // 多语言站点：自动为每个语言生成 alternate 链接
    i18n: {
      locales: ['zh', 'en'],
      routesNameSeparator: '___',
    },
    // 排除不需要的路由
    exclude: ['/admin/**', '/api/**'],
  },
})
```

---

## robots.txt：nuxt-simple-robots

安装：
```bash
npm install nuxt-simple-robots
```

`nuxt.config.ts`：
```typescript
export default defineNuxtConfig({
  modules: ['nuxt-simple-robots'],
  robots: {
    disallow: ['/admin', '/api'],
    sitemap: 'https://DOMAIN/sitemap.xml',
  },
})
```

---

## JSON-LD：useSchemaOrg 或手动注入

使用 `nuxt-schema-org`（推荐）：

```bash
npm install nuxt-schema-org
```

`app.vue`：
```vue
<script setup>
useSchemaOrg([
  defineWebSite({ name: '网站名称' }),
  defineOrganization({
    name: '组织名称',
    logo: 'https://DOMAIN/logo.png',
  }),
])
</script>
```

或手动注入（不安装额外依赖）：

```vue
<script setup>
useHead({
  script: [{
    type: 'application/ld+json',
    children: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      name: '网站名称',
      url: 'https://DOMAIN',
    }),
  }],
})
</script>
```
