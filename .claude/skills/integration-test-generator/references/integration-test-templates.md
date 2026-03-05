# 集成测试代码模板

## Python (pytest + httpx)

```python
"""
Integration Tests: {场景名称}
测试流程：{API1} → {API2} → {API3}
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

def test_{scenario_name}_success(client, base_url, auth_headers):
    """
    测试场景：{场景描述}
    步骤：1. {步骤1}  2. {步骤2}  3. {步骤3}
    """
    # Step 1
    response_1 = client.post(
        f"{base_url}/api/{endpoint1}",
        json={"field1": "value1"},
        headers=auth_headers
    )
    assert response_1.status_code == 201, f"Step 1 failed: {response_1.text}"
    resource_id = response_1.json()["id"]

    # Step 2
    response_2 = client.post(
        f"{base_url}/api/{endpoint2}",
        json={"ref_id": resource_id, "field2": "value2"},
        headers=auth_headers
    )
    assert response_2.status_code == 201, f"Step 2 failed: {response_2.text}"
    related_id = response_2.json()["id"]

    # Step 3: 验证最终状态
    response_3 = client.get(
        f"{base_url}/api/{endpoint3}/{related_id}",
        headers=auth_headers
    )
    assert response_3.status_code == 200, f"Step 3 failed: {response_3.text}"
    assert response_3.json()["status"] == "expected_status"

def test_{scenario_name}_step2_fails(client, base_url, auth_headers):
    response_1 = client.post(f"{base_url}/api/{endpoint1}", json={"field1": "value1"}, headers=auth_headers)
    assert response_1.status_code == 201
    resource_id = response_1.json()["id"]

    response_2 = client.post(
        f"{base_url}/api/{endpoint2}",
        json={"ref_id": resource_id, "field2": "invalid_value"},
        headers=auth_headers
    )
    assert response_2.status_code == 400
```

---

## Node.js (Vitest + supertest)

```typescript
/**
 * Integration Tests: {场景名称}
 * 测试流程：{API1} → {API2} → {API3}
 */
import { describe, it, expect, beforeAll, afterEach } from 'vitest';
import request from 'supertest';

const BASE_URL = process.env.TEST_API_URL || 'http://localhost:3000';
let authToken: string;

beforeAll(async () => {
  const response = await request(BASE_URL)
    .post('/api/auth/login')
    .send({ username: 'test_user', password: 'test_password' });
  authToken = response.body.token;
});

describe('{场景名称}', () => {
  let createdResourceId: string;

  afterEach(async () => {
    if (createdResourceId) {
      await request(BASE_URL)
        .delete(`/api/resources/${createdResourceId}`)
        .set('Authorization', `Bearer ${authToken}`);
      createdResourceId = '';
    }
  });

  it('完整流程：所有步骤成功', async () => {
    // Step 1
    const response1 = await request(BASE_URL)
      .post('/api/{endpoint1}')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ field1: 'value1' });
    expect(response1.status).toBe(201);
    createdResourceId = response1.body.id;

    // Step 2
    const response2 = await request(BASE_URL)
      .post('/api/{endpoint2}')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ refId: createdResourceId, field2: 'value2' });
    expect(response2.status).toBe(201);
    const relatedId = response2.body.id;

    // Step 3: 验证最终状态
    const response3 = await request(BASE_URL)
      .get(`/api/{endpoint3}/${relatedId}`)
      .set('Authorization', `Bearer ${authToken}`);
    expect(response3.status).toBe(200);
    expect(response3.body.status).toBe('expected_status');
  });

  it('错误处理：中间步骤失败', async () => {
    const response1 = await request(BASE_URL)
      .post('/api/{endpoint1}')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ field1: 'value1' });
    expect(response1.status).toBe(201);

    const response2 = await request(BASE_URL)
      .post('/api/{endpoint2}')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ refId: response1.body.id, field2: 'invalid' });
    expect(response2.status).toBe(400);
  });
});
```

---

## Go (testing + testify)

```go
// {scenario_name}_integration_test.go
package integration_test

import (
	"bytes"
	"encoding/json"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

var baseURL = "http://localhost:8080"
var authToken string

func TestMain(m *testing.M) {
	resp, _ := http.Post(baseURL+"/api/auth/login", "application/json",
		bytes.NewReader([]byte(`{"username":"test","password":"test"}`)))
	var tokenResp map[string]string
	json.NewDecoder(resp.Body).Decode(&tokenResp)
	authToken = tokenResp["token"]
	m.Run()
}

func Test{ScenarioName}_Success(t *testing.T) {
	client := &http.Client{}

	// Step 1
	body1, _ := json.Marshal(map[string]string{"field1": "value1"})
	req1, _ := http.NewRequest("POST", baseURL+"/api/{endpoint1}", bytes.NewBuffer(body1))
	req1.Header.Set("Authorization", "Bearer "+authToken)
	req1.Header.Set("Content-Type", "application/json")

	resp1, err := client.Do(req1)
	require.NoError(t, err)
	defer resp1.Body.Close()
	assert.Equal(t, 201, resp1.StatusCode)

	var data1 map[string]interface{}
	json.NewDecoder(resp1.Body).Decode(&data1)
	resourceID := data1["id"].(string)

	// Step 2
	body2, _ := json.Marshal(map[string]string{"ref_id": resourceID, "field2": "value2"})
	req2, _ := http.NewRequest("POST", baseURL+"/api/{endpoint2}", bytes.NewBuffer(body2))
	req2.Header.Set("Authorization", "Bearer "+authToken)
	req2.Header.Set("Content-Type", "application/json")

	resp2, err := client.Do(req2)
	require.NoError(t, err)
	defer resp2.Body.Close()
	assert.Equal(t, 201, resp2.StatusCode)

	var data2 map[string]interface{}
	json.NewDecoder(resp2.Body).Decode(&data2)

	// Step 3: 验证最终状态
	req3, _ := http.NewRequest("GET", baseURL+"/api/{endpoint3}/"+data2["id"].(string), nil)
	req3.Header.Set("Authorization", "Bearer "+authToken)

	resp3, err := client.Do(req3)
	require.NoError(t, err)
	defer resp3.Body.Close()
	assert.Equal(t, 200, resp3.StatusCode)

	var data3 map[string]interface{}
	json.NewDecoder(resp3.Body).Decode(&data3)
	assert.Equal(t, "expected_status", data3["status"])
}
```

---

## Java (JUnit 5 + REST Assured)

```java
/**
 * Integration Tests: {场景名称}
 * 测试流程：{API1} → {API2} → {API3}
 */
package com.example.integration;

import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.junit.jupiter.api.*;

import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class {ScenarioName}IntegrationTest {

    private static String authToken;
    private static String createdResourceId;

    @BeforeAll static void setup() {
        RestAssured.baseURI = "http://localhost:8080";
        authToken = given()
            .contentType("application/json")
            .body("{\"username\":\"test\",\"password\":\"test\"}")
            .when().post("/api/auth/login")
            .then().extract().path("token");
    }

    @Test @Order(1) @DisplayName("完整流程：所有步骤成功")
    void testSuccess() {
        // Step 1
        Response response1 = given()
            .contentType("application/json")
            .header("Authorization", "Bearer " + authToken)
            .body("{\"field1\":\"value1\"}")
            .when().post("/api/{endpoint1}")
            .then().statusCode(201).body("id", notNullValue())
            .extract().response();

        createdResourceId = response1.path("id");

        // Step 2
        String relatedId = given()
            .contentType("application/json")
            .header("Authorization", "Bearer " + authToken)
            .body(String.format("{\"ref_id\":\"%s\",\"field2\":\"value2\"}", createdResourceId))
            .when().post("/api/{endpoint2}")
            .then().statusCode(201).extract().path("id");

        // Step 3: 验证最终状态
        given()
            .header("Authorization", "Bearer " + authToken)
            .when().get("/api/{endpoint3}/" + relatedId)
            .then().statusCode(200).body("status", equalTo("expected_status"));
    }

    @AfterAll static void cleanup() {
        if (createdResourceId != null) {
            given().header("Authorization", "Bearer " + authToken)
                .when().delete("/api/resources/" + createdResourceId);
        }
    }
}
```

---

## 测试报告模板

```markdown
# {场景名称} 集成测试报告

| 项目 | 内容 |
|------|------|
| 业务场景 | {场景描述} |
| 测试目标 | {保护目标说明} |
| 生成时间 | {YYYY-MM-DD HH:mm} |
| 测试框架 | {pytest/supertest/go test/junit} |

## 测试流程

```
API1 → API2 → API3 → 验证
```

## 测试用例

| 测试函数 | 场景 | 覆盖的 API |
|----------|------|-----------|
| test_{scenario}_success | 完整流程成功 | POST /api/e1 → POST /api/e2 → GET /api/e3 |
| test_{scenario}_step2_fails | 步骤2失败处理 | POST /api/e1 → POST /api/e2 |

## 成功标准

- [x] 覆盖完整业务流程的 Happy Path
- [x] 覆盖关键步骤的失败场景
- [x] 没有使用任何 Mock
- [x] 测试数据有清理策略
```
