# 新项目接入指南

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
