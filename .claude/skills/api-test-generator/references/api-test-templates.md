# API 测试代码模板

## Python (pytest + httpx)

```python
"""
API Tests for {endpoint}
保护目标：{description}
"""
import pytest
import httpx
from typing import Generator

@pytest.fixture(scope="module")
def base_url() -> str:
    return "http://localhost:8000"

@pytest.fixture(scope="module")
def auth_headers(base_url: str) -> dict:
    response = httpx.post(f"{base_url}/api/auth/login", json={
        "username": "test_user", "password": "test_password"
    })
    assert response.status_code == 200
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def client() -> Generator[httpx.Client, None, None]:
    with httpx.Client(timeout=30.0) as client:
        yield client

VALID_PAYLOAD = {
    # TODO: 填充有效的请求数据
}

INVALID_PAYLOADS = [
    ({}, "缺失必填字段"),
    ({"field": None}, "字段为 null"),
    ({"field": ""}, "字段为空字符串"),
]

def test_{endpoint_name}_success(client, base_url, auth_headers):
    response = client.post(f"{base_url}/api/{endpoint}", json=VALID_PAYLOAD, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data

@pytest.mark.parametrize("payload,description", INVALID_PAYLOADS)
def test_{endpoint_name}_validation_error(client, base_url, auth_headers, payload, description):
    response = client.post(f"{base_url}/api/{endpoint}", json=payload, headers=auth_headers)
    assert response.status_code in (400, 422), f"场景：{description}"

def test_{endpoint_name}_unauthorized(client, base_url):
    response = client.post(f"{base_url}/api/{endpoint}", json=VALID_PAYLOAD)
    assert response.status_code == 401

def test_{endpoint_name}_forbidden(client, base_url):
    response = client.post(
        f"{base_url}/api/{endpoint}",
        json=VALID_PAYLOAD,
        headers={"Authorization": "Bearer limited_user_token"}
    )
    assert response.status_code == 403
```

---

## Node.js (Vitest + supertest)

```typescript
/**
 * API Tests for {endpoint}
 * 保护目标：{description}
 */
import { describe, it, expect, beforeAll } from 'vitest';
import request from 'supertest';

const BASE_URL = process.env.TEST_API_URL || 'http://localhost:3000';

const VALID_PAYLOAD = { /* TODO */ };
const INVALID_PAYLOADS = [
  { payload: {}, description: '缺失必填字段' },
  { payload: { field: null }, description: '字段为 null' },
  { payload: { field: '' }, description: '字段为空字符串' },
];

let authToken: string;

beforeAll(async () => {
  const res = await request(BASE_URL).post('/api/auth/login')
    .send({ username: 'test_user', password: 'test_password' });
  authToken = res.body.token;
});

describe('{endpoint}', () => {
  describe('Happy Path', () => {
    it('有效参数应返回成功', async () => {
      const response = await request(BASE_URL)
        .post('/api/{endpoint}')
        .set('Authorization', `Bearer ${authToken}`)
        .send(VALID_PAYLOAD);
      expect(response.status).toBe(201);
      expect(response.body).toHaveProperty('id');
    });
  });

  describe('Validation', () => {
    it.each(INVALID_PAYLOADS)('无效参数：$description', async ({ payload }) => {
      const response = await request(BASE_URL)
        .post('/api/{endpoint}')
        .set('Authorization', `Bearer ${authToken}`)
        .send(payload);
      expect([400, 422]).toContain(response.status);
    });
  });

  describe('Auth', () => {
    it('未携带 Token 应返回 401', async () => {
      const response = await request(BASE_URL).post('/api/{endpoint}').send(VALID_PAYLOAD);
      expect(response.status).toBe(401);
    });

    it('无权限用户应返回 403', async () => {
      const response = await request(BASE_URL)
        .post('/api/{endpoint}')
        .set('Authorization', 'Bearer limited_user_token')
        .send(VALID_PAYLOAD);
      expect(response.status).toBe(403);
    });
  });
});
```

---

## Go (testing + testify)

```go
// {endpoint}_test.go
package api_test

import (
	"bytes"
	"encoding/json"
	"net/http"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

var baseURL = getEnv("TEST_API_URL", "http://localhost:8080")
var authToken string

func getEnv(key, fallback string) string {
	if v, ok := os.LookupEnv(key); ok { return v }
	return fallback
}

func TestMain(m *testing.M) {
	resp, _ := http.Post(baseURL+"/api/auth/login", "application/json",
		bytes.NewReader([]byte(`{"username":"test_user","password":"test_password"}`)))
	var body map[string]string
	json.NewDecoder(resp.Body).Decode(&body)
	authToken = body["token"]
	os.Exit(m.Run())
}

type Payload struct{ Field string `json:"field"` }

var validPayload = Payload{Field: "valid_value"}

func Test{Endpoint}_Success(t *testing.T) {
	body, _ := json.Marshal(validPayload)
	req, _ := http.NewRequest("POST", baseURL+"/api/{endpoint}", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+authToken)

	resp, err := (&http.Client{}).Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()
	assert.Equal(t, http.StatusCreated, resp.StatusCode)
}

func Test{Endpoint}_ValidationError(t *testing.T) {
	testCases := []struct{ name string; payload interface{} }{
		{"缺失必填字段", map[string]interface{}{}},
		{"字段为空", Payload{Field: ""}},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			body, _ := json.Marshal(tc.payload)
			req, _ := http.NewRequest("POST", baseURL+"/api/{endpoint}", bytes.NewBuffer(body))
			req.Header.Set("Content-Type", "application/json")
			req.Header.Set("Authorization", "Bearer "+authToken)

			resp, err := (&http.Client{}).Do(req)
			require.NoError(t, err)
			defer resp.Body.Close()
			assert.Contains(t, []int{400, 422}, resp.StatusCode)
		})
	}
}

func Test{Endpoint}_Unauthorized(t *testing.T) {
	body, _ := json.Marshal(validPayload)
	req, _ := http.NewRequest("POST", baseURL+"/api/{endpoint}", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")

	resp, err := (&http.Client{}).Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()
	assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
}
```

---

## Java (JUnit 5 + REST Assured)

```java
/**
 * API Tests for {endpoint}
 * 保护目标：{description}
 */
package com.example.api;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.util.Map;
import java.util.stream.Stream;

import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

class {Endpoint}ApiTest {

    private static String authToken;

    @BeforeAll static void setup() {
        RestAssured.baseURI = System.getenv().getOrDefault("TEST_API_URL", "http://localhost:8080");
        authToken = given()
            .contentType(ContentType.JSON)
            .body("{\"username\":\"test_user\",\"password\":\"test_password\"}")
            .when().post("/api/auth/login")
            .then().extract().path("token");
    }

    private static final Map<String, Object> VALID_PAYLOAD = Map.of("field", "valid_value");

    static Stream<Arguments> invalidPayloads() {
        return Stream.of(
            Arguments.of(Map.of(), "缺失必填字段"),
            Arguments.of(Map.of("field", ""), "字段为空字符串")
        );
    }

    @Test @DisplayName("正常路径：有效参数应返回成功")
    void testSuccess() {
        given()
            .contentType(ContentType.JSON)
            .header("Authorization", "Bearer " + authToken)
            .body(VALID_PAYLOAD)
        .when().post("/api/{endpoint}")
        .then().statusCode(201).body("id", notNullValue());
    }

    @ParameterizedTest(name = "参数校验：{1}")
    @MethodSource("invalidPayloads")
    void testValidationError(Map<String, Object> payload, String description) {
        given()
            .contentType(ContentType.JSON)
            .header("Authorization", "Bearer " + authToken)
            .body(payload)
        .when().post("/api/{endpoint}")
        .then().statusCode(anyOf(is(400), is(422)));
    }

    @Test @DisplayName("未携带 Token 应返回 401")
    void testUnauthorized() {
        given().contentType(ContentType.JSON).body(VALID_PAYLOAD)
        .when().post("/api/{endpoint}")
        .then().statusCode(401);
    }

    @Test @DisplayName("无权限用户应返回 403")
    void testForbidden() {
        given()
            .contentType(ContentType.JSON)
            .header("Authorization", "Bearer limited_user_token")
            .body(VALID_PAYLOAD)
        .when().post("/api/{endpoint}")
        .then().statusCode(403);
    }
}
```

---

## 数据清理示例

```python
# Python：fixture 自动清理
@pytest.fixture
def created_order(client, base_url, auth_headers):
    response = client.post(f"{base_url}/api/orders", json=VALID_PAYLOAD, headers=auth_headers)
    order_id = response.json()["id"]
    yield order_id
    client.delete(f"{base_url}/api/orders/{order_id}", headers=auth_headers)
```

```typescript
// TypeScript：afterEach 清理
let createdOrderId: string;

afterEach(async () => {
  if (createdOrderId) {
    await request(BASE_URL)
      .delete(`/api/orders/${createdOrderId}`)
      .set('Authorization', `Bearer ${authToken}`);
    createdOrderId = undefined;
  }
});
```

---

## 测试报告模板

```markdown
# {资源名称} API 测试报告

| 项目 | 内容 |
|------|------|
| API 端点 | {GET/POST/PUT/DELETE} /api/{resource} |
| 测试目标 | {保护目标说明} |
| 生成时间 | {YYYY-MM-DD HH:mm} |
| 测试框架 | {pytest/supertest/go test/rest assured} |

## 测试用例

| 测试函数 | 场景 | 预期结果 |
|----------|------|----------|
| test_{resource}_success | 正常路径 | 201, 返回资源 ID |
| test_{resource}_validation_error | 参数校验 | 400/422 |
| test_{resource}_unauthorized | 未携带 Token | 401 |
| test_{resource}_forbidden | 无权限 | 403 |

## 成功标准

- [x] 覆盖 Happy Path
- [x] 覆盖参数校验错误
- [x] 覆盖鉴权/权限校验
- [x] 没有使用任何 Mock
```
