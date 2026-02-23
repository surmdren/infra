# DreamAI Infra - 需求与路线图

## 核心定位

> 所有 DreamAI 项目共享一套基础设施，降低边际成本，快速启动新项目。

---

## Phase 1：基础能力（当前）✅

- [x] PostgreSQL + pgvector（数据库 + AI 向量搜索）
- [x] Supabase Auth（用户认证，支持跨项目 SSO）
- [x] MinIO 文件存储（S3 兼容）
- [x] PostgREST（自动 REST API）
- [x] Realtime WebSocket
- [x] Studio Dashboard（可视化管理）
- [x] `new-project.sh`（新项目 schema 一键创建）
- [x] `backup.sh`（数据库定时备份）

---

## Phase 2：完善生产能力（下一阶段）

### 支付接入层
- [ ] Stripe 统一封装（订阅 + 一次性付费）
- [ ] 支持多项目共用同一 Stripe 账号，按 product 区分
- [ ] Webhook 统一处理，写入各项目 schema

### 邮件服务
- [ ] Resend 或 SMTP 统一发送层
- [ ] 模板管理（注册验证、密码重置、通知）
- [ ] 各项目共用，通过 schema 区分发件人签名

### 任务队列
- [ ] Redis + BullMQ
- [ ] 用于 AI 生成任务（异步处理、重试、进度推送）
- [ ] 所有项目共享队列，按 project 命名空间隔离

---

## Phase 3：AI 基础设施

### LiteLLM 代理（优先级高）
- [ ] 统一 AI 调用入口，所有项目通过代理访问模型
- [ ] 支持：OpenAI / Claude / DeepSeek / 通义千问
- [ ] 按项目统计 token 用量和成本
- [ ] 超额自动限流，防止费用失控
- [ ] 国内模型降级策略（Claude 超时 → 自动切 DeepSeek）

### 图片处理
- [ ] imgproxy 集成（AI 生成图片压缩/裁剪/水印）
- [ ] 与 MinIO 存储联动，URL 参数化转换

### GPU 任务调度（Rick 的核心优势）
- [ ] K8s GPU 节点池（ComfyUI / SD 推理）
- [ ] 任务队列 → GPU 节点弹性调度
- [ ] 支持多项目共享 GPU 资源，按优先级分配

---

## Phase 4：可观测性

- [ ] Prometheus + Grafana（所有服务统一监控）
- [ ] Loki（所有项目日志集中收集）
- [ ] 告警规则（服务挂了 / 数据库慢查询 / API 错误率）
- [ ] 费用仪表盘（AI 调用成本 / 存储用量 / 带宽）

---

## 接入的项目

| 项目 | repo | 接入状态 |
|------|------|---------|
| ai-cofounder | surmdren/ai-cofounder | 计划中 |
| chatseo | surmdren/chatseo | 计划中 |
| sleek-design | 待建 | 计划中 |
| appforge | surmdren/appforge | 计划中 |
| growth-engine | surmdren/growth-engine | 计划中 |

---

## 设计原则

1. **共享底层，隔离数据** — 同一 PostgreSQL 实例，不同 schema
2. **边际成本趋零** — 新项目接入不增加服务器成本
3. **跨项目 SSO** — 用户一个账号打通所有 DreamAI 产品
4. **Rick 优先** — 充分利用 SRE/K8s 背景，自建 > 外购
