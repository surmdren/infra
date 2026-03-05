# UAT 测试代码示例

## 数据播种脚本

```typescript
// UAT/scripts/seed-data.ts
// 运行：npx ts-node UAT/scripts/seed-data.ts

const BASE_URL = 'http://localhost:3000'

async function seed() {
  // 1. 用商家账号创建商品（确保列表有数据可点）
  const sellerToken = await login('seller@test.com', 'Test1234!')
  const product = await fetch(`${BASE_URL}/api/products`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${sellerToken}` },
    body: JSON.stringify({ name: 'UAT测试商品', price: 99, stock: 10 })
  }).then(r => r.json())

  // 2. 用管理员账号审核通过（确保买家能看到商品）
  const adminToken = await login('admin@test.com', 'Admin1234!')
  await fetch(`${BASE_URL}/api/admin/products/${product.id}/approve`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${adminToken}` }
  })

  // 3. 用买家账号创建订单（确保订单列表有数据）
  const buyerToken = await login('buyer@test.com', 'Test1234!')
  await fetch(`${BASE_URL}/api/orders`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${buyerToken}` },
    body: JSON.stringify({ productId: product.id, quantity: 1 })
  })

  console.log('✅ 测试数据播种完成')
}
seed()
```

## 基础正向场景示例

```typescript
// 文件命名：UAT/tests/{角色}-{场景编号}-{场景名}.spec.ts
// 示例：UAT/tests/buyer-01-register-and-purchase.spec.ts

test('买家可以注册账号并完成首次购买', async ({ page }) => {
  // 模拟真实用户操作，不调用 API
  await page.goto('http://localhost:3000/register')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'SecurePass123!')
  await page.click('button[type="submit"]')
  // 验证用户视角可见的结果
  await expect(page.locator('.welcome-message')).toBeVisible()
})
```

## 跨角色交互链条示例（商家→管理员→买家）

```typescript
// UAT/tests/cross-role-01-product-lifecycle.spec.ts
test('商家发布 → 管理员审核 → 买家购买 完整链条', async ({ browser }) => {
  // Role 1: 商家发布商品
  const sellerCtx = await browser.newContext()
  const sellerPage = await sellerCtx.newPage()
  await loginAs(sellerPage, 'seller@test.com')
  await sellerPage.goto('/seller/products/new')
  await sellerPage.fill('[name="name"]', '链条测试商品')
  await sellerPage.click('[data-testid="submit"]')
  await expect(sellerPage.locator('text=待审核')).toBeVisible()

  // Role 2: 管理员审核通过
  const adminCtx = await browser.newContext()
  const adminPage = await adminCtx.newPage()
  await loginAs(adminPage, 'admin@test.com')
  await adminPage.goto('/admin/products?status=pending')
  await adminPage.locator('text=链条测试商品').first().click()
  await adminPage.click('[data-testid="approve-btn"]')
  await expect(adminPage.locator('text=已上架')).toBeVisible()

  // Role 3: 买家能搜到并购买
  const buyerCtx = await browser.newContext()
  const buyerPage = await buyerCtx.newPage()
  await loginAs(buyerPage, 'buyer@test.com')
  await buyerPage.goto('/')
  await buyerPage.fill('[placeholder="搜索"]', '链条测试商品')
  await buyerPage.press('[placeholder="搜索"]', 'Enter')
  await expect(buyerPage.locator('text=链条测试商品')).toBeVisible()
})
```

## 权限边界（负向场景）示例

```typescript
// UAT/tests/permission-boundary.spec.ts
test('买家无法访问商家后台', async ({ page }) => {
  await loginAs(page, 'buyer@test.com')
  await page.goto('/seller/dashboard')
  // 应跳转到首页或显示 403，不能直接渲染后台
  await expect(page).not.toHaveURL('/seller/dashboard')
})

test('未登录用户访问个人中心应跳转到登录页', async ({ page }) => {
  await page.goto('/profile')
  await expect(page).toHaveURL(/\/login/)
})
```

## 异步副作用验证示例（轮询状态变更）

```typescript
// UAT/tests/buyer-04-order-status.spec.ts
test('下单后订单状态变为处理中', async ({ page }) => {
  await loginAs(page, 'buyer@test.com')
  // 下单
  await page.goto('/cart')
  await page.click('[data-testid="checkout-btn"]')
  await page.click('[data-testid="confirm-order"]')
  // 等待异步状态更新（轮询最多 10 秒）
  await expect(async () => {
    await page.reload()
    await expect(page.locator('[data-testid="order-status"]')).toHaveText('处理中')
  }).toPass({ timeout: 10000 })
})
```

## i18n 语言切换场景

```typescript
// UAT/tests/i18n-01-language-switch.spec.ts
test('用户可以切换语言，所有文案正确变换', async ({ page }) => {
  await page.goto('http://localhost:3000/zh')
  // 验证默认中文
  await expect(page.locator('[data-testid="nav-home"]')).toHaveText('首页')

  // 切换到英文
  await page.click('[data-testid="lang-switcher"]')
  await page.click('[data-testid="lang-en"]')
  await expect(page).toHaveURL(/\/en\//)
  await expect(page.locator('[data-testid="nav-home"]')).toHaveText('Home')

  // 切回中文
  await page.click('[data-testid="lang-switcher"]')
  await page.click('[data-testid="lang-zh"]')
  await expect(page).toHaveURL(/\/zh\//)
  await expect(page.locator('[data-testid="nav-home"]')).toHaveText('首页')
})

test('语言偏好在刷新后保持', async ({ page }) => {
  await page.goto('http://localhost:3000/zh')
  // 切换到英文
  await page.click('[data-testid="lang-switcher"]')
  await page.click('[data-testid="lang-en"]')
  await expect(page).toHaveURL(/\/en\//)

  // 刷新页面，应保持英文（cookie 持久化）
  await page.reload()
  await expect(page).toHaveURL(/\/en\//)
  await expect(page.locator('[data-testid="nav-home"]')).toHaveText('Home')
})
```

## 移动端视口测试

```typescript
// 在关键场景上追加移动端测试
test('买家可在手机端完成购买', async ({ browser }) => {
  const ctx = await browser.newContext({
    viewport: { width: 390, height: 844 },  // iPhone 14
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'
  })
  const page = await ctx.newPage()
  // 同样的购买流程在移动端验证
})
```

## Pre-flight 检查代码片段

```typescript
// 验证数据 ID 是真实格式
// ❌ 禁止
await page.goto('/orders/test-order-id')

// ✅ 从列表页取真实 ID 再跳转
await page.goto('/orders')
const firstOrderLink = page.locator('[data-testid="order-row"] a').first()
const href = await firstOrderLink.getAttribute('href')
// href 应为 /orders/550e8400-e29b-41d4-a716-446655440000 （真实 UUID）
expect(href).toMatch(/\/orders\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/)

// 覆盖「点击已有数据」跳转路径
await expect(page.locator('[data-testid="list-item"]').first()).toBeVisible()
await page.locator('[data-testid="list-item"]').first().click()
await expect(page).toHaveURL(/\/detail\/[0-9a-f-]{36}/)
await expect(page.locator('[data-testid="detail-content"]')).not.toBeEmpty()

// 确认页面错误有可见提示
// 模拟网络错误，确认错误提示出现
await page.route('**/api/**', route => route.abort())
await page.click('[data-testid="submit-btn"]')
await expect(page.locator('[role="alert"], .error-toast, [data-testid="error-msg"]')).toBeVisible()
```
