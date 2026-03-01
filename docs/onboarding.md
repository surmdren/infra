# 新项目接入指南

## 共享基础设施一览

| 服务 | 用途 | 内网地址 | 公网域名 |
|------|------|----------|----------|
| **Supabase** | 数据库 / Auth / Storage / REST API | `http://172.18.0.2:30086` | `https://supabase-dev.dreamwiseai.com` |
| **Chatwoot** | 客服聊天系统 | `http://172.18.0.2:30091` | `https://chatwoot.dreamwiseai.com` |

---

## 5 分钟接入流程

### Step 1：在 platform 创建项目 schema

```bash
cd /path/to/infra
./scripts/new-project.sh <your-project-name>
```

脚本会输出该项目的连接配置，复制保存。

### Step 2：在项目代码中配置环境变量

```bash
# 在你的项目根目录 .env 中添加
SUPABASE_URL=http://your-server:8000
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_KEY=xxx
DB_SCHEMA=your-project-name
```

### Step 3：安装 Supabase SDK

```bash
# Node.js / Next.js 项目
npm install @supabase/supabase-js

# Python 项目
pip install supabase
```

### Step 4：初始化客户端

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!,
  {
    db: { schema: process.env.DB_SCHEMA || 'public' }
  }
)
```

### Step 5：在 Studio 中建表

访问 http://your-server:3000，选择你的 schema，直接可视化建表。

或者写 SQL migration：

```sql
-- 在你的项目 schema 下建表
CREATE TABLE your_project_name.users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 常用功能示例

### 用户认证

```typescript
// 注册
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password'
})

// 登录
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password'
})
```

### 数据库操作

```typescript
// 查询
const { data } = await supabase
  .from('your_table')
  .select('*')
  .eq('user_id', userId)

// 插入
const { data } = await supabase
  .from('your_table')
  .insert({ title: 'Hello', user_id: userId })
```

### 文件存储

```typescript
// 上传文件
const { data } = await supabase.storage
  .from('your-bucket')
  .upload('folder/file.png', file)

// 获取公开 URL
const { data } = supabase.storage
  .from('your-bucket')
  .getPublicUrl('folder/file.png')
```

### AI 向量搜索（pgvector）

```sql
-- 建表时添加向量列
ALTER TABLE your_project_name.documents
  ADD COLUMN embedding vector(1536);

-- 语义搜索
SELECT * FROM your_project_name.documents
ORDER BY embedding <-> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

---

## 接入 Chatwoot 客服系统

### Step 1：创建 Inbox

1. 登录 [https://chatwoot.dreamwiseai.com](https://chatwoot.dreamwiseai.com)
2. Settings → Inboxes → New Inbox → **Website**
3. 填入你的 SaaS 域名，完成创建
4. 复制生成的 `website_token`

### Step 2：嵌入 Widget

在前端 HTML `<body>` 底部或 Next.js 的 `layout.tsx` 里加入：

```html
<!-- 纯 HTML 项目 -->
<script>
  window.chatwootSettings = {
    position: 'right',
    locale: 'zh_CN',
  };
  (function(d,t) {
    var BASE_URL = "https://chatwoot.dreamwiseai.com";
    var g = d.createElement(t), s = d.getElementsByTagName(t)[0];
    g.src = BASE_URL + "/packs/js/sdk.js";
    g.defer = true;
    g.async = true;
    s.parentNode.insertBefore(g, s);
    g.onload = function() {
      window.chatwootSDK.run({
        websiteToken: 'YOUR_INBOX_TOKEN',  // ← 每个 SaaS 不同
        baseUrl: BASE_URL
      });
    };
  })(document, "script");
</script>
```

```typescript
// Next.js layout.tsx
import Script from 'next/script'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Script id="chatwoot" strategy="afterInteractive">{`
          window.chatwootSettings = { position: 'right', locale: 'zh_CN' };
          (function(d,t) {
            var BASE_URL = "https://chatwoot.dreamwiseai.com";
            var g = d.createElement(t), s = d.getElementsByTagName(t)[0];
            g.src = BASE_URL + "/packs/js/sdk.js";
            g.defer = true; g.async = true;
            s.parentNode.insertBefore(g, s);
            g.onload = function() {
              window.chatwootSDK.run({
                websiteToken: process.env.NEXT_PUBLIC_CHATWOOT_TOKEN,
                baseUrl: BASE_URL
              });
            };
          })(document, "script");
        `}</Script>
      </body>
    </html>
  )
}
```

### Step 3：环境变量

```bash
# .env
NEXT_PUBLIC_CHATWOOT_TOKEN=your_inbox_token_here
```

### Step 4（可选）：识别登录用户

让客服能看到是哪个用户在咨询：

```typescript
// 用户登录后调用
window.$chatwoot?.setUser(user.id, {
  name: user.name,
  email: user.email,
})
```
