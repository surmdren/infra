# Supabase 连接信息

**环境：** K3s 生产环境  
**部署方式：** Helm (supabase-community/supabase-kubernetes)

---

## 访问地址

| 服务 | URL |
|------|-----|
| API Gateway (Kong) | `https://supabase.dreamwiseai.com` |
| Studio 管理界面 | `https://supabase-studio.dreamwiseai.com` |
| REST API | `https://supabase.dreamwiseai.com/rest/v1/` |
| Auth | `https://supabase.dreamwiseai.com/auth/v1/` |
| Storage | `https://supabase.dreamwiseai.com/storage/v1/` |
| Realtime | `wss://supabase.dreamwiseai.com/realtime/v1/` |

---

## API Keys

```
# Anon Key（前端公开使用）
eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJyb2xlIjogImFub24iLCAiaXNzIjogInN1cGFiYXNlIiwgImlhdCI6IDE2NDE3NjkyMDAsICJleHAiOiAxOTk5OTk5OTk5fQ.cz4Oj_3OgbdZ5bwZqqR-jKuQUdTt514h7Vi6_gzt1SI

# Service Role Key（后端使用，保密）
eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJyb2xlIjogInNlcnZpY2Vfcm9sZSIsICJpc3MiOiAic3VwYWJhc2UiLCAiaWF0IjogMTY0MTc2OTIwMCwgImV4cCI6IDE5OTk5OTk5OTl9.1YfCEGK185VCwWsqH5V0tZ1gMjVoEPq4esds0wIC8bE
```

---

## Studio 登录

```
用户名: supabase
密码:   cmXyBGFZpC3v5vd
```

---

## 数据库直连（集群内部）

```
Host:     supabase-supabase-db.supabase.svc.cluster.local
Port:     5432
Database: postgres
User:     postgres
Password: CARQM2Xytte0dycLTFgtBuKk
```

---

## 客户端 SDK 使用示例

### JavaScript / TypeScript

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://supabase.dreamwiseai.com'
const supabaseAnonKey = 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJyb2xlIjogImFub24iLCAiaXNzIjogInN1cGFiYXNlIiwgImlhdCI6IDE2NDE3NjkyMDAsICJleHAiOiAxOTk5OTk5OTk5fQ.cz4Oj_3OgbdZ5bwZqqR-jKuQUdTt514h7Vi6_gzt1SI'

const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### Python

```python
from supabase import create_client

url = "https://supabase.dreamwiseai.com"
key = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJyb2xlIjogImFub24iLCAiaXNzIjogInN1cGFiYXNlIiwgImlhdCI6IDE2NDE3NjkyMDAsICJleHAiOiAxOTk5OTk5OTk5fQ.cz4Oj_3OgbdZ5bwZqqR-jKuQUdTt514h7Vi6_gzt1SI"

supabase = create_client(url, key)
```

### curl

```bash
# REST API 查询示例
curl https://supabase.dreamwiseai.com/rest/v1/your_table \
  -H "apikey: <anon_key>" \
  -H "Authorization: Bearer <anon_key>"

# 使用 service_role key（绕过 RLS）
curl https://supabase.dreamwiseai.com/rest/v1/your_table \
  -H "apikey: <service_role_key>" \
  -H "Authorization: Bearer <service_role_key>"
```

---

## JWT Secret

```
EFbGXZV7rOSvXjTJoBxyxTxULr6mX7WgD2pT7kFI
```

用于自行签发 JWT token（如需要自定义 claims）。

---

## MinIO (S3 兼容存储) 内部访问

```
Endpoint: http://supabase-minio.supabase.svc.cluster.local:9000
Bucket:   supabase-storage
Key ID:   259ae341c053c74fb0475be67320310f
Secret:   f9065dcfcaefc280fe5a1d3deb406e0d61cf3ded22bfa19b9cf6937a7721781a
```
