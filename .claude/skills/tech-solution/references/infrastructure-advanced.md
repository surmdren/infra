# 基础设施进阶：可观测性 / SLO / 成本优化

## Observability 三支柱

### 指标（Metrics）

```yaml
# 推荐：Prometheus + Grafana（开源免费）
- Prometheus：K8s 指标 + 应用自定义指标
- Grafana：Dashboard 可视化
- AlertManager：邮件/Slack/PagerDuty

# 云托管方案
- AWS：CloudWatch + Container Insights
- 阿里云：ARMS + 云监控
```

**核心告警规则（必须设置）：**

| 指标 | 阈值 | 严重度 |
|------|------|--------|
| Pod CPU 使用率 | > 80% 持续 5min | Warning |
| Pod 内存使用率 | > 85% 持续 5min | Warning |
| Pod 重启次数 | > 3次/小时 | Critical |
| HTTP 错误率 | > 1% 持续 2min | Critical |
| P99 响应时间 | > 2s 持续 5min | Warning |
| 磁盘使用率 | > 80% | Warning |

### 日志（Logs）

```yaml
# 自托管
- Fluentd/Fluent Bit（DaemonSet）→ Elasticsearch → Kibana

# 云托管
- AWS：CloudWatch Logs + Insights
- 阿里云：SLS 日志服务

# 日志规范
- 统一 JSON 格式，含 trace_id / request_id
- 按严重度分级：DEBUG / INFO / WARN / ERROR
- 敏感信息脱敏（密码、token、PII）
```

### 链路追踪（Tracing）

```yaml
# OpenTelemetry（推荐，标准化）
- SDK：应用埋点（自动/手动）
- Collector：数据收集与转发
- 后端：Jaeger（自托管）或 Tempo（Grafana 生态）

# 接入方式（代码无侵入）
- Node.js：@opentelemetry/auto-instrumentations-node
- Python：opentelemetry-instrumentation
- Java：opentelemetry-javaagent
```

---

## SLO / SLI 定义

输出到 `infrastructure/slo.md`：

```markdown
## 服务等级目标（SLO）

| 服务 | SLI | SLO | 错误预算（30天） |
|------|-----|-----|----------------|
| API 可用性 | 成功请求率（2xx/3xx） | 99.9% | 43.8 分钟 |
| API 延迟 | P99 响应时间 | < 500ms | - |
| 数据库可用性 | 连接成功率 | 99.95% | 21.9 分钟 |

## 错误预算策略
- 消耗 > 50%：暂停非关键功能发布
- 消耗 > 80%：冻结所有非紧急发布
- 耗尽：启动 incident review
```

---

## 成本优化

### Spot 实例（节省 60-80%）

```yaml
# AWS 示例
nodeGroups:
  - name: spot-workers
    instancesDistribution:
      instanceTypes: ["t3.medium", "t3.large", "t3a.medium"]
      onDemandPercentageAboveBaseCapacity: 0  # 全部 Spot
      spotAllocationStrategy: diversified
  - name: ondemand-critical
    instanceType: t3.medium  # 数据库等有状态服务
```

### 资源配额（必须与 Namespace 同步创建）

```yaml
# ResourceQuota：Namespace 级别总量上限
apiVersion: v1
kind: ResourceQuota
metadata:
  name: project-quota
  namespace: <your-namespace>
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4"
    limits.memory: 8Gi
    pods: "20"
---
# LimitRange：Pod/Container 级别默认值
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: <your-namespace>
spec:
  limits:
    - type: Container
      default:
        cpu: "500m"
        memory: "512Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      max:
        cpu: "2"
        memory: "4Gi"
```

### 谨慎引入

- **多区域部署**：单区域起步，有明确 latency SLO 或合规要求时再扩展
- **服务网格（Istio）**：10+ 微服务且需要 mTLS 时才值得
- **多云架构**：避免过早引入，vendor lock-in 风险低于多云运维复杂度
