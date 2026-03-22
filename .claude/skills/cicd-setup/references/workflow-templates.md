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
    runs-on: [self-hosted, linux, x64, cicd]

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

## deploy-prod.yml — Tag 触发，人工审批后部署 Prod

> **本地 staging 测试用 `/dev-deploy` 直接部署到本地 k3s，不走 GitHub Actions，节省 CI minutes。**
> 只有部署到生产环境才触发此 workflow。

```yaml
name: Deploy Prod

on:
  push:
    tags:
      - 'v*.*.*'

env:
  ACR_REGISTRY: {{ACR_REGISTRY}}
  IMAGE_NAME: {{IMAGE_NAME}}
  K8S_NAMESPACE: {{K8S_NAMESPACE_PROD}}

jobs:
  build-and-push:
    runs-on: [self-hosted, linux, x64, cicd]
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
            ${{ env.IMAGE_NAME }}:latest
          cache-from: type=registry,ref=${{ env.IMAGE_NAME }}:latest
          cache-to: type=inline

  deploy-prod:
    needs: build-and-push
    runs-on: [self-hosted, linux, x64, cicd]
    environment: production    # 触发 GitHub Environment 手动审批门控

    steps:
      - uses: actions/checkout@v4

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

      - name: Deploy to prod
        run: |
          kubectl set image deployment/{{APP_NAME}} \
            {{APP_NAME}}=${{ env.IMAGE_NAME }}:${{ needs.build-and-push.outputs.image-tag }} \
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

      - name: Write deployment summary
        if: always()
        run: |
          STATUS="${{ job.status }}"
          ICON=$([ "$STATUS" = "success" ] && echo "✅" || echo "❌")
          echo "## Prod Deployment Summary ${ICON}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "| 项目 | 值 |" >> $GITHUB_STEP_SUMMARY
          echo "|------|-----|" >> $GITHUB_STEP_SUMMARY
          echo "| Image | \`${{ env.IMAGE_NAME }}:${{ needs.build-and-push.outputs.image-tag }}\` |" >> $GITHUB_STEP_SUMMARY
          echo "| Namespace | \`${{ env.K8S_NAMESPACE }}\` |" >> $GITHUB_STEP_SUMMARY
          echo "| Smoke test | $([ "$STATUS" = "success" ] && echo "✅ Passed" || echo "❌ Failed") |" >> $GITHUB_STEP_SUMMARY
          echo "| Time | $(date -u '+%Y-%m-%d %H:%M UTC') |" >> $GITHUB_STEP_SUMMARY
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
| `{{K8S_NAMESPACE_PROD}}` | `my-app-prod-backend` | 用户提供（格式：`<project>-prod-<component>`） |
