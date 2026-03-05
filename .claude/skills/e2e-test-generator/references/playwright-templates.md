# Playwright 代码模板

## TypeScript

```typescript
/**
 * E2E Test: {flow_name}
 * 保护目标：{description}
 *
 * 用户流程：
 * 1. {step1}
 * 2. {step2}
 * 3. {step3}
 */
import { test, expect, Page } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:3000';
const TEST_USER = {
  email: process.env.E2E_TEST_EMAIL || 'test@example.com',
  password: process.env.E2E_TEST_PASSWORD || 'testpassword123',
};

// ============ Page Helpers ============

async function login(page: Page, email: string, password: string) {
  await page.goto(`${BASE_URL}/login`);
  await page.getByLabel('邮箱').fill(email);
  await page.getByLabel('密码').fill(password);
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForURL('**/dashboard');
}

async function addToCart(page: Page, productId: string) {
  await page.goto(`${BASE_URL}/products/${productId}`);
  await page.getByRole('button', { name: '加入购物车' }).click();
  await expect(page.getByTestId('cart-count')).toHaveText('1');
}

async function checkout(page: Page) {
  await page.goto(`${BASE_URL}/cart`);
  await page.getByRole('button', { name: '去结算' }).click();
  await page.getByLabel('收货人').fill('测试用户');
  await page.getByLabel('手机号').fill('13800138000');
  await page.getByLabel('地址').fill('测试地址');
  await page.getByRole('button', { name: '提交订单' }).click();
  await page.waitForURL('**/order/success');
}

// ============ Test ============

test.describe('核心购物流程', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER.email, TEST_USER.password);
  });

  test('用户可以完成完整的购物流程', async ({ page }) => {
    await addToCart(page, 'product-123');
    await checkout(page);

    await expect(page.getByTestId('order-success-message')).toBeVisible();
    await expect(page.getByTestId('order-id')).toHaveText(/^ORD-/);

    await page.getByRole('link', { name: '查看订单详情' }).click();
    await expect(page.getByTestId('order-status')).toHaveText('待支付');
  });
});
```

---

## Python

```python
"""
E2E Test: {flow_name}
保护目标：{description}

用户流程：
1. {step1}
2. {step2}
3. {step3}
"""
import re
import os
import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.getenv('E2E_BASE_URL', 'http://localhost:3000')
TEST_USER = {
    'email': os.getenv('E2E_TEST_EMAIL', 'test@example.com'),
    'password': os.getenv('E2E_TEST_PASSWORD', 'testpassword123'),
}

def login(page: Page, email: str, password: str):
    page.goto(f'{BASE_URL}/login')
    page.get_by_label('邮箱').fill(email)
    page.get_by_label('密码').fill(password)
    page.get_by_role('button', name='登录').click()
    page.wait_for_url('**/dashboard')

def add_to_cart(page: Page, product_id: str):
    page.goto(f'{BASE_URL}/products/{product_id}')
    page.get_by_role('button', name='加入购物车').click()
    expect(page.get_by_test_id('cart-count')).to_have_text('1')

def checkout(page: Page):
    page.goto(f'{BASE_URL}/cart')
    page.get_by_role('button', name='去结算').click()
    page.get_by_label('收货人').fill('测试用户')
    page.get_by_label('手机号').fill('13800138000')
    page.get_by_label('地址').fill('测试地址')
    page.get_by_role('button', name='提交订单').click()
    page.wait_for_url('**/order/success')

@pytest.fixture
def logged_in_page(page: Page):
    login(page, TEST_USER['email'], TEST_USER['password'])
    yield page

class TestCoreShoppingFlow:
    def test_user_can_complete_shopping_flow(self, logged_in_page: Page):
        page = logged_in_page
        add_to_cart(page, 'product-123')
        checkout(page)

        expect(page.get_by_test_id('order-success-message')).to_be_visible()
        expect(page.get_by_test_id('order-id')).to_have_text(re.compile(r'^ORD-'))

        page.get_by_role('link', name='查看订单详情').click()
        expect(page.get_by_test_id('order-status')).to_have_text('待支付')
```

---

## Java

```java
/**
 * E2E Test: {flow_name}
 * 保护目标：{description}
 */
package com.example.e2e;

import com.microsoft.playwright.*;
import com.microsoft.playwright.options.*;
import org.junit.jupiter.api.*;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.*;

class CoreShoppingFlowTest {

    private static final String BASE_URL = System.getenv().getOrDefault("E2E_BASE_URL", "http://localhost:3000");
    private static final String TEST_EMAIL = System.getenv().getOrDefault("E2E_TEST_EMAIL", "test@example.com");
    private static final String TEST_PASSWORD = System.getenv().getOrDefault("E2E_TEST_PASSWORD", "testpassword123");

    private static Playwright playwright;
    private static Browser browser;
    private BrowserContext context;
    private Page page;

    @BeforeAll static void setupClass() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch();
    }

    @AfterAll static void teardownClass() {
        browser.close();
        playwright.close();
    }

    @BeforeEach void setup() {
        context = browser.newContext();
        page = context.newPage();
        login(page, TEST_EMAIL, TEST_PASSWORD);
    }

    @AfterEach void teardown() { context.close(); }

    private void login(Page page, String email, String password) {
        page.navigate(BASE_URL + "/login");
        page.getByLabel("邮箱").fill(email);
        page.getByLabel("密码").fill(password);
        page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("登录")).click();
        page.waitForURL("**/dashboard");
    }

    private void addToCart(Page page, String productId) {
        page.navigate(BASE_URL + "/products/" + productId);
        page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("加入购物车")).click();
        assertThat(page.getByTestId("cart-count")).hasText("1");
    }

    private void checkout(Page page) {
        page.navigate(BASE_URL + "/cart");
        page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("去结算")).click();
        page.getByLabel("收货人").fill("测试用户");
        page.getByLabel("手机号").fill("13800138000");
        page.getByLabel("地址").fill("测试地址");
        page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("提交订单")).click();
        page.waitForURL("**/order/success");
    }

    @Test
    @DisplayName("用户可以完成完整的购物流程")
    void userCanCompleteShoppingFlow() {
        addToCart(page, "product-123");
        checkout(page);

        assertThat(page.getByTestId("order-success-message")).isVisible();
        assertThat(page.getByTestId("order-id")).hasText(java.util.regex.Pattern.compile("^ORD-"));

        page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("查看订单详情")).click();
        assertThat(page.getByTestId("order-status")).hasText("待支付");
    }
}
```

---

## playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 60_000,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [['html', { open: 'never' }], ['list']],
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## GitHub Actions CI

```yaml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npm run dev &
      - run: npx wait-on http://localhost:3000
      - run: npx playwright test
        env:
          E2E_BASE_URL: http://localhost:3000
          E2E_TEST_EMAIL: ${{ secrets.E2E_TEST_EMAIL }}
          E2E_TEST_PASSWORD: ${{ secrets.E2E_TEST_PASSWORD }}
      - if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
```
