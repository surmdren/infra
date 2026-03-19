# Workflow Templates

用 `{{变量名}}` 标记需要替换的占位符。

---

## ci.yml — PR 自动测试

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '{{NODE_VERSION}}'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run type-check
        continue-on-error: false

      - name: Test
        run: {{TEST_COMMAND}}
        env:
          NODE_ENV: test
```

---

## deploy-staging.yml — Tag 触发 Staging 部署

```yaml
name: Deploy Staging

on:
  push:
    tags:
      - 'v*.*.*'

env:
  ACR_REGISTRY: {{ACR_REGISTRY}}
  IMAGE_NAME: {{IMAGE_NAME}}
  K8S_NAMESPACE: {{K8S_NAMESPACE_STAGING}}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.version }}

    steps:
      - uses: actions/checkout@v4

      - name: Extract version from tag
        id: meta
        run: echo "version=${GITHUB_REF_NAME}" >> $GITHUB_OUTPUT

      - name: Login to Aliyun ACR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.ACR_REGISTRY }}
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.version }}
            ${{ env.IMAGE_NAME }}:staging-latest
          # staging-latest 仅用于加速下次构建的 Build Cache，不作为部署引用
          # 实际部署始终使用语义化版本 tag（如 v1.2.0）
          cache-from: type=registry,ref=${{ env.IMAGE_NAME }}:staging-latest
          cache-to: type=inline

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure kubeconfig
        run: |
          mkdir -p ~/.kube
          echo "${{ secrets.KUBECONFIG_STAGING }}" | base64 -d > ~/.kube/config

      - name: Deploy to staging
        run: |
          kubectl set image deployment/{{APP_NAME}} \
            {{APP_NAME}}=${{ env.IMAGE_NAME }}:${{ needs.build-and-push.outputs.image-tag }} \
            -n ${{ env.K8S_NAMESPACE }}
          kubectl rollout status deployment/{{APP_NAME}} -n ${{ env.K8S_NAMESPACE }} --timeout=300s

      - name: Smoke test
        run: |
          sleep 10
          STAGING_URL="${{ secrets.STAGING_URL }}"
          curl -f "${STAGING_URL}/api/health" || exit 1
          echo "Staging smoke test passed"

      - name: Write deployment summary
        if: always()
        run: |
          STATUS="${{ job.status }}"
          ICON=$([ "$STATUS" = "success" ] && echo "✅" || echo "❌")
          echo "## Staging Deployment Summary ${ICON}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "| 项目 | 值 |" >> $GITHUB_STEP_SUMMARY
          echo "|------|-----|" >> $GITHUB_STEP_SUMMARY
          echo "| Image | \`${{ env.IMAGE_NAME }}:${{ needs.build-and-push.outputs.image-tag }}\` |" >> $GITHUB_STEP_SUMMARY
          echo "| Namespace | \`${{ env.K8S_NAMESPACE }}\` |" >> $GITHUB_STEP_SUMMARY
          echo "| Smoke test | $([ "$STATUS" = "success" ] && echo "✅ Passed" || echo "❌ Failed") |" >> $GITHUB_STEP_SUMMARY
          echo "| Time | $(date -u '+%Y-%m-%d %H:%M UTC') |" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          if [ "$STATUS" = "success" ]; then
            echo "> Prod deployment pending approval. Review this summary before approving." >> $GITHUB_STEP_SUMMARY
          else
            echo "> ⚠️ Staging failed — prod deployment will NOT be triggered." >> $GITHUB_STEP_SUMMARY
          fi
```

---

## deploy-prod.yml — Staging 成功后自动触发，人工审批后部署 Prod

```yaml
name: Deploy Prod

on:
  workflow_run:
    workflows: ["Deploy Staging"]   # 与 deploy-staging.yml 的 name 保持一致
    types: [completed]

env:
  ACR_REGISTRY: {{ACR_REGISTRY}}
  IMAGE_NAME: {{IMAGE_NAME}}
  K8S_NAMESPACE: {{K8S_NAMESPACE_PROD}}

jobs:
  deploy-prod:
    runs-on: ubuntu-latest
    environment: production    # 触发 GitHub Environment 手动审批门控
    # 只在 staging 成功时才继续；tag push 时 head_branch 即为 tag 名（如 v1.2.0）
    if: ${{ github.event.workflow_run.conclusion == 'success' }}

    steps:
      - uses: actions/checkout@v4

      - name: Get image tag from staging run
        id: tag
        run: |
          IMAGE_TAG="${{ github.event.workflow_run.head_branch }}"
          echo "image-tag=${IMAGE_TAG}" >> $GITHUB_OUTPUT
          echo "Deploying image tag: ${IMAGE_TAG}"

      - name: Setup kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure kubeconfig
        run: |
          mkdir -p ~/.kube
          echo "${{ secrets.KUBECONFIG_PROD }}" | base64 -d > ~/.kube/config

      - name: Login to Aliyun ACR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.ACR_REGISTRY }}
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}

      - name: Verify image exists in ACR
        run: |
          docker pull ${{ env.IMAGE_NAME }}:${{ steps.tag.outputs.image-tag }}
          echo "Image verified: ${{ env.IMAGE_NAME }}:${{ steps.tag.outputs.image-tag }}"

      - name: Deploy to prod
        run: |
          kubectl set image deployment/{{APP_NAME}} \
            {{APP_NAME}}=${{ env.IMAGE_NAME }}:${{ steps.tag.outputs.image-tag }} \
            -n ${{ env.K8S_NAMESPACE }}
          kubectl rollout status deployment/{{APP_NAME}} -n ${{ env.K8S_NAMESPACE }} --timeout=300s

      - name: Smoke test
        run: |
          sleep 15
          PROD_URL="${{ secrets.PROD_URL }}"
          curl -f "${PROD_URL}/api/health" || exit 1
          echo "Prod smoke test passed"

      - name: Rollback on failure
        if: failure()
        run: |
          echo "::error::Prod deployment failed! Rolling back..."
          kubectl rollout undo deployment/{{APP_NAME}} -n ${{ env.K8S_NAMESPACE }}
```

---

## Dockerfile — Next.js 多阶段构建

```dockerfile
# Stage 1: Install dependencies
FROM node:{{NODE_VERSION}}-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --only=production && npm cache clean --force

# Stage 2: Build application
FROM node:{{NODE_VERSION}}-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Production runtime
FROM node:{{NODE_VERSION}}-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# 创建非 root 用户
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 复制 standalone 输出
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE {{APP_PORT}}
ENV PORT={{APP_PORT}}
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

> **前提**：`next.config.js` 中需要设置 `output: 'standalone'`，否则 standalone 目录不会生成。

---

## 占位符替换表

| 占位符 | 示例值 | 来源 |
|--------|-------|------|
| `{{NODE_VERSION}}` | `20` | `.nvmrc` 或 package.json engines |
| `{{TEST_COMMAND}}` | `npm test` | package.json scripts.test |
| `{{ACR_REGISTRY}}` | `registry.cn-hangzhou.aliyuncs.com` | 用户提供 |
| `{{IMAGE_NAME}}` | `registry.cn-hangzhou.aliyuncs.com/myco/my-app` | 用户提供 |
| `{{APP_NAME}}` | `my-app` | package.json name |
| `{{APP_PORT}}` | `3000` | 用户提供或默认 3000 |
| `{{K8S_NAMESPACE_STAGING}}` | `my-app-staging-backend` | 用户提供（格式：`<project>-staging-<component>`） |
| `{{K8S_NAMESPACE_PROD}}` | `my-app-prod-backend` | 用户提供（格式：`<project>-prod-<component>`） |
