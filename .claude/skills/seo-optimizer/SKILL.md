---
name: seo-optimizer
description: 为已部署的 Web 项目执行两阶段 SEO 优化：Phase 1 审计现有代码输出问题清单，Phase 2 自动注入修复（meta tags、sitemap、robots.txt、JSON-LD、canonical + hreflang）。自动检测框架（Next.js App Router/Pages Router、Nuxt、Vue SPA），输出 SEO/seo-audit-report.md 和 SEO/hreflang-map.md。专为多语言站点和 k8s 自托管部署优化（非 Vercel）。SDLC 位置：utm-injector 之后、monitoring-setup 之前。当用户提到"SEO优化"、"搜索引擎优化"、"sitemap"、"meta tags"、"hreflang"、"多语言SEO"、"OG标签"、"robots.txt"、"structured data"、"JSON-LD"、"seo-optimizer"时立即触发。
---

# SEO Optimizer

为 Web 项目自动化 SEO 优化，两阶段执行：先审计找问题，确认后自动修复。

```
SDLC: utm-injector → seo-optimizer → monitoring-setup
                           ↑ 【在此阶段执行】
```

## 覆盖范围（5项）

| 项目 | 优先级 | 自动修复 | 说明 |
|------|--------|---------|------|
| Meta tags + OG + Twitter Card | P0 | ✅ | 注入 layout / head 文件 |
| sitemap.xml + robots.txt | P0 | ✅ | 生成静态文件或动态路由 |
| canonical URL + hreflang | P0 | ✅ | 多语言站点必需，防重复内容 |
| JSON-LD 结构化数据 | P1 | ✅ | WebSite + Organization 基础类型 |
| 图片 alt 属性 | P1 | ✅ | 静态扫描，补全空 alt |

---

## Phase 1：Audit（审计）

### Step 1：检测框架

扫描项目文件识别框架：

```
Next.js App Router:   app/layout.tsx 或 app/layout.js
Next.js Pages Router: pages/_app.tsx 或 pages/_document.tsx
Nuxt:                 nuxt.config.ts 或 nuxt.config.js
Vue SPA:              vite.config.ts + src/App.vue（无 SSR）
其他/未知:            index.html 或通用处理
```

记录框架版本和路由模式，后续步骤按框架分支处理（详见 references/ 目录）。

### Step 2：扫描 5 类 SEO 问题

并行扫描以下内容，每项记录状态（缺失 / 不完整 / 正常）：

#### 2.1 Meta Tags + OG + Twitter Card
- 检查 layout 文件是否有 `<title>`、`description`、`og:title`、`og:description`、`og:image`、`twitter:card`
- Next.js App Router：检查 `export const metadata` 或 `generateMetadata`
- Nuxt：检查 `useHead` / `useSeoMeta` 调用
- 标记缺失字段，记录需要注入的文件路径

#### 2.2 sitemap.xml + robots.txt
- 检查 `public/sitemap.xml`（静态）或 `app/sitemap.ts`（动态，Next.js App Router）
- 检查 `public/robots.txt` 是否存在且包含正确的 `Sitemap:` 指令
- 多语言站点：sitemap 应包含所有语言版本的 URL（`hreflang` alternate 链接）

#### 2.3 canonical URL + hreflang
- 检查每个页面是否设置了 `canonical` 链接
- 检查是否有 `hreflang` alternate 标签（多语言必需）
- 检查语言配置文件（`i18n.config.ts`、`next-i18next.config.js` 等）提取支持的语言列表

#### 2.4 JSON-LD 结构化数据
- 搜索 `application/ld+json` script 标签
- 检查是否包含 `WebSite` 和 `Organization` 基础 Schema

#### 2.5 图片 alt 属性
- 扫描所有 `.tsx`、`.vue`、`.html` 文件中的 `<img` 标签
- 找出 `alt=""` 或缺少 `alt` 属性的图片，记录文件路径和行号

### Step 3：输出审计报告

生成 `SEO/seo-audit-report.md`，格式如下：

```markdown
# SEO Audit Report

生成时间: YYYY-MM-DD HH:MM UTC
框架: [检测到的框架]
多语言: [是/否，语言列表]

## 问题汇总

| 项目 | 状态 | 优先级 | 影响文件数 |
|------|------|--------|-----------|
| Meta tags + OG | ⚠️ 不完整 | P0 | 3 |
| sitemap.xml | ❌ 缺失 | P0 | - |
| canonical + hreflang | ❌ 缺失 | P0 | - |
| JSON-LD | ❌ 缺失 | P1 | - |
| 图片 alt | ⚠️ 部分缺失 | P1 | 5 |

## 详细问题

### ❌ sitemap.xml — 缺失
预计改动：新建 app/sitemap.ts
...

### ⚠️ Meta tags — 不完整
缺少字段：og:image, twitter:card
预计改动：修改 app/layout.tsx
...
```

**在报告末尾询问用户：** "以上是审计结果。是否执行 Phase 2 自动修复？（yes/no）"

---

## Phase 2：Auto-fix（自动修复）

用户确认后执行。每步修改前先读取目标文件，确保不破坏现有代码。

### Step 4：注入 Meta Tags + OG + Twitter Card

按框架处理，详见对应参考文件：
- **Next.js App Router** → `references/nextjs-app-router.md`
- **Next.js Pages Router** → `references/nextjs-pages-router.md`
- **Nuxt** → `references/nuxt.md`
- **Vue SPA / 其他** → `references/generic.md`

注入时需要的信息（从项目文件中推断，推断不到则询问用户）：
- 网站名称（`og:site_name`）
- 默认 OG 图片路径（`og:image`），若无则标记为 TODO
- 网站域名（用于 canonical URL 基础路径）

### Step 5：生成 sitemap.xml + robots.txt

按框架生成，要求：
- 包含所有公开页面的 URL
- 多语言站点：每个 URL 包含所有语言版本的 `<xhtml:link rel="alternate" hreflang="...">` 标签
- `robots.txt` 包含 `Sitemap: https://yourdomain.com/sitemap.xml`

robots.txt 基础模板：
```
User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/

Sitemap: https://DOMAIN/sitemap.xml
```

### Step 6：注入 canonical + hreflang

- **canonical**：每个页面 `<link rel="canonical" href="https://domain.com/[current-path]">`
- **hreflang**：为每个页面生成所有语言版本的 alternate 标签

生成 `SEO/hreflang-map.md` — 多语言 URL 映射表，供人工验证：

```markdown
# Hreflang URL 映射表

| 页面 | zh-CN | en | ja |
|------|-------|----|----|
| 首页 | /zh | /en | /ja |
| 关于 | /zh/about | /en/about | /ja/about |
```

### Step 7：注入 JSON-LD 结构化数据

在根 layout 中注入 WebSite + Organization Schema：

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "name": "网站名称",
      "url": "https://domain.com",
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://domain.com/search?q={search_term_string}",
        "query-input": "required name=search_term_string"
      }
    },
    {
      "@type": "Organization",
      "name": "组织名称",
      "url": "https://domain.com",
      "logo": "https://domain.com/logo.png"
    }
  ]
}
```

### Step 8：修复图片 alt 属性

根据审计结果（Step 2.5），为空 alt 图片补全描述：
- 根据图片文件名、周围文本上下文推断描述
- 纯装饰性图片：`alt=""`（空字符串，符合 WCAG 规范）
- 内容图片：生成描述性 alt 文本

### Step 9：更新审计报告

将所有修复状态更新到 `SEO/seo-audit-report.md`，添加修复摘要：

```markdown
## Phase 2 修复结果

| 项目 | 修复状态 | 改动文件 |
|------|---------|---------|
| Meta tags + OG | ✅ 已修复 | app/layout.tsx |
| sitemap.xml | ✅ 已生成 | app/sitemap.ts |
| robots.txt | ✅ 已生成 | public/robots.txt |
| canonical + hreflang | ✅ 已注入 | app/layout.tsx |
| JSON-LD | ✅ 已注入 | app/layout.tsx |
| 图片 alt | ✅ 12/14 已修复（2张需人工确认） |

### 需要人工处理
- [ ] 替换默认 OG 图片占位符：`public/og-default.png`
- [ ] 验证 hreflang 语言代码与实际路由一致（见 SEO/hreflang-map.md）
- [ ] 为 2 张上下文不明的装饰图添加 alt（见报告详情）
```

---

## 输出文件

```
SEO/
├── seo-audit-report.md   # Phase 1 问题清单 + Phase 2 修复状态
└── hreflang-map.md       # 多语言 URL 映射表（供人工验证）
```

---

## 注意事项

- **幂等设计**：每步先检查文件是否已有对应配置，只修改缺失部分，不覆盖已有的 SEO 设置
- **多语言优先**：检测到 i18n 配置时，自动启用 hreflang 和多语言 sitemap
- **不猜测域名**：canonical 和 sitemap 中的域名从项目配置文件中读取，找不到则询问用户
- **project-manager 模式**：Phase 1 + Phase 2 连续执行，不等待用户确认

## 框架参考文件

| 框架 | 参考文件 |
|------|---------|
| Next.js App Router | `references/nextjs-app-router.md` |
| Next.js Pages Router | `references/nextjs-pages-router.md` |
| Nuxt | `references/nuxt.md` |
| Vue SPA / 其他 | `references/generic.md` |
