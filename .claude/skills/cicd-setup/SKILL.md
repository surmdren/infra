---
name: cicd-setup
description: 为项目生成完整的 GitHub Actions CI/CD 工作流配置。生成 3 个 workflow 文件：CI（PR 自动跑测试+lint）、CD Staging（打 Tag v* 自动构建镜像并部署）、CD Prod（手动审批后部署）。支持阿里云 ACR 镜像仓库 + K8s 部署，主要针对 Node.js/Next.js 项目（可扩展到 Python/Go）。同时生成 GitHub Secrets 配置清单和 Dockerfile（如项目缺失）。应在 dev-deploy 完成后、项目正式上线前执行。当用户提到"搭建CI/CD"、"配置GitHub Actions"、"自动部署"、"CICD工作流"、"cicd-setup"、"打Tag部署"、"Staging部署"、"流水线配置"、"持续集成"、"持续部署"时触发。
---

# CI/CD Setup

为项目生成完整的 GitHub Actions CI/CD 工作流，实现：本地开发 → PR 自动测试 → 打 Tag 触发 Staging 部署 → 手动审批 Prod 部署。

## 工作流架构

```
PR / push to main
      │
   [ci.yml]  lint + test（目标 < 5 分钟）
      │
  merge to main
      │
  git tag v1.2.0
      │
[deploy-staging.yml]
  构建 Docker 镜像 → 推送 ACR → 部署 K8s staging → smoke test
      │
  手动在 GitHub Actions 点击 "Review deployments"
      │
[deploy-prod.yml]
  部署 K8s prod → smoke test
```

## 输出文件

```
.github/
└── workflows/
    ├── ci.yml                  # PR 自动测试
    ├── deploy-staging.yml      # Tag 触发 Staging 部署
    └── deploy-prod.yml         # 手动审批 Prod 部署
Dockerfile                      # 如项目中不存在则生成
docs/
└── cicd-secrets-setup.md       # GitHub Secrets 配置清单
```

## Phase 0：扫描项目

先扫描，只询问扫描后仍然缺失的信息：

```bash
# 读取基础信息
cat package.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps({k:d.get(k) for k in ['name','version','scripts','engines']}, indent=2))"

# 检测现有配置
ls -la | grep -E "Dockerfile|\.nvmrc|\.node-version"
ls .github/workflows/ 2>/dev/null
ls k8s/ deploy/ manifests/ 2>/dev/null
```

整理后向用户展示发现的配置，确认缺失项再询问。

## Phase 1：确认配置

收集完整信息后，汇总展示给用户确认（确认后再生成）：

```
应用名称：       my-app
Node.js 版本：   20
测试命令：       npm test
Build 命令：     npm run build
ACR Registry：   registry.cn-hangzhou.aliyuncs.com/mycompany
镜像名称：       registry.cn-hangzhou.aliyuncs.com/mycompany/my-app
K8s Namespace（staging）：my-app-staging-backend   # <project>-staging-<component>
K8s Namespace（prod）：   my-app-prod-backend      # <project>-prod-<component>
应用端口：       3000
```

## Phase 2：生成 Workflow 文件

读取 `references/workflow-templates.md`，用确认的配置替换变量，生成 3 个文件。

**核心设计原则：**
- `ci.yml`：在每个 PR 和 push to main 时运行，快速失败（lint 先跑，通过才跑 test）
- `deploy-staging.yml`：只在 `v*.*.*` tag 上触发，用 git tag 作为 Docker 镜像 tag
- `deploy-prod.yml`：使用 `environment: production`，配合 GitHub Environment Protection Rules 实现手动审批；复用 staging 已构建的镜像（不重新构建，保证一致性）

## Phase 3：生成 Dockerfile（如缺失）

若项目没有 Dockerfile，生成 Node.js/Next.js 标准多阶段构建：

```dockerfile
# 参考 references/workflow-templates.md 中的 Dockerfile 模板
# 关键要求：
# - node:<版本>-alpine 基础镜像
# - 三阶段：deps → builder → runner
# - Next.js standalone 模式（output: 'standalone'）
# - 非 root 用户运行（nextjs uid=1001）
# - 暴露正确端口
```

同时检查 `next.config.js`，如果没有 `output: 'standalone'`，提示用户添加（standalone 模式让镜像体积从 ~1GB 降到 ~150MB）。

## Phase 4：生成 Secrets 配置清单

生成 `docs/cicd-secrets-setup.md`，详细说明每个 Secret 的作用、如何获取、在哪里配置。

读取 `references/secrets-setup.md` 获取配置步骤模板。

## Phase 5：输出汇总

生成完成后，告知用户后续步骤：

```markdown
## 下一步操作清单

### 1. 配置 GitHub Secrets
前往：Settings → Secrets and variables → Actions
需要配置的 Secrets 见：docs/cicd-secrets-setup.md

### 2. 配置 GitHub Environment（手动审批）
前往：Settings → Environments → 新建 "production"
勾选 "Required reviewers"，添加需要审批的人

### 3. 测试 CI
推送任意 commit 或创建 PR，检查 Actions 是否跑起来

### 4. 测试 Staging 部署
git tag v0.1.0
git push origin v0.1.0
观察 deploy-staging workflow 是否成功

### 5. 测试 Prod 部署
在 GitHub Actions 界面找到 deploy-staging 完成后的 deploy-prod，点击审批
```

---

## 扩展支持

目前主要针对 Node.js/Next.js。如检测到其他技术栈，调整对应部分：

| 技术栈 | 测试命令 | Build 命令 | Dockerfile 基础镜像 |
|--------|---------|-----------|-------------------|
| Python/FastAPI | `pytest` | `pip install` | `python:3.11-slim` |
| Go | `go test ./...` | `go build` | `golang:1.21-alpine` |
| Java/Spring | `mvn test` | `mvn package` | `eclipse-temurin:21-jre` |

核心 workflow 结构（Tag 触发 → ACR 推镜像 → K8s 部署 → 审批 Prod）保持不变，只替换 build/test 步骤。
