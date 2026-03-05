# 单元测试代码模板

## Python (pytest)

```python
"""
Unit Tests for {module}
保护目标：{description}
"""
import pytest
from unittest.mock import Mock

from app.services.{module} import {ClassName}

# ============ Fixtures ============

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_cache():
    return Mock()

@pytest.fixture
def service(mock_repository, mock_cache):
    return {ClassName}(repository=mock_repository, cache=mock_cache)

# ============ Tests: Happy Path ============

class TestCalculateDiscount:
    def test_vip_user_gets_discount(self, service, mock_repository):
        """VIP 用户应获得折扣"""
        mock_repository.get_user.return_value = User(vip_level=2)

        result = service.calculate_discount(user_id=1, amount=100)

        assert result == 90
        mock_repository.get_user.assert_called_once_with(1)

    def test_normal_user_no_discount(self, service, mock_repository):
        mock_repository.get_user.return_value = User(vip_level=0)
        assert service.calculate_discount(user_id=1, amount=100) == 100

# ============ Tests: Edge Cases ============

class TestCalculateDiscountEdgeCases:
    def test_zero_amount(self, service, mock_repository):
        mock_repository.get_user.return_value = User(vip_level=2)
        assert service.calculate_discount(user_id=1, amount=0) == 0

    def test_user_not_found_raises_error(self, service, mock_repository):
        mock_repository.get_user.return_value = None
        with pytest.raises(UserNotFoundError):
            service.calculate_discount(user_id=999, amount=100)

# ============ Tests: State Machine ============

class TestOrderStateMachine:
    @pytest.mark.parametrize("current_state,action,expected_state", [
        ("pending", "pay", "paid"),
        ("paid", "ship", "shipped"),
        ("shipped", "receive", "completed"),
        ("pending", "cancel", "cancelled"),
    ])
    def test_valid_transitions(self, service, current_state, action, expected_state):
        order = Order(status=current_state)
        service.transition(order, action)
        assert order.status == expected_state

    @pytest.mark.parametrize("current_state,action", [
        ("completed", "cancel"),
        ("cancelled", "pay"),
        ("pending", "ship"),
    ])
    def test_invalid_transitions_raise_error(self, service, current_state, action):
        order = Order(status=current_state)
        with pytest.raises(InvalidTransitionError):
            service.transition(order, action)
```

---

## Node.js (Vitest)

```typescript
/**
 * Unit Tests for {module}
 * 保护目标：{description}
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { {ClassName} } from '@/services/{module}';

const mockRepository = { getUser: vi.fn(), save: vi.fn() };
const mockCache = { get: vi.fn(), set: vi.fn() };

let service: {ClassName};

beforeEach(() => {
  vi.clearAllMocks();
  service = new {ClassName}(mockRepository, mockCache);
});

describe('calculateDiscount', () => {
  describe('Happy Path', () => {
    it('VIP 用户应获得折扣', () => {
      mockRepository.getUser.mockReturnValue({ vipLevel: 2 });

      const result = service.calculateDiscount(1, 100);

      expect(result).toBe(90);
      expect(mockRepository.getUser).toHaveBeenCalledWith(1);
    });

    it('普通用户不享受折扣', () => {
      mockRepository.getUser.mockReturnValue({ vipLevel: 0 });
      expect(service.calculateDiscount(1, 100)).toBe(100);
    });
  });

  describe('Edge Cases', () => {
    it('金额为 0 应返回 0', () => {
      mockRepository.getUser.mockReturnValue({ vipLevel: 2 });
      expect(service.calculateDiscount(1, 0)).toBe(0);
    });

    it('用户不存在应抛出异常', () => {
      mockRepository.getUser.mockReturnValue(null);
      expect(() => service.calculateDiscount(999, 100)).toThrow(UserNotFoundError);
    });
  });
});

describe('OrderStateMachine', () => {
  it.each([
    ['pending', 'pay', 'paid'],
    ['paid', 'ship', 'shipped'],
    ['shipped', 'receive', 'completed'],
    ['pending', 'cancel', 'cancelled'],
  ])('%s + %s -> %s', (currentState, action, expectedState) => {
    const order = { status: currentState };
    service.transition(order, action);
    expect(order.status).toBe(expectedState);
  });

  it.each([
    ['completed', 'cancel'],
    ['cancelled', 'pay'],
    ['pending', 'ship'],
  ])('%s + %s -> Error', (currentState, action) => {
    const order = { status: currentState };
    expect(() => service.transition(order, action)).toThrow(InvalidTransitionError);
  });
});
```

---

## Go (testing + testify)

```go
// {module}_test.go
package service

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockRepository struct {
	mock.Mock
}

func (m *MockRepository) GetUser(id int) (*User, error) {
	args := m.Called(id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*User), args.Error(1)
}

func TestCalculateDiscount_VIPUser(t *testing.T) {
	mockRepo := new(MockRepository)
	mockRepo.On("GetUser", 1).Return(&User{VIPLevel: 2}, nil)
	service := NewDiscountService(mockRepo)

	result, err := service.CalculateDiscount(1, 100)

	assert.NoError(t, err)
	assert.Equal(t, 90.0, result)
	mockRepo.AssertExpectations(t)
}

func TestCalculateDiscount_ZeroAmount(t *testing.T) {
	mockRepo := new(MockRepository)
	mockRepo.On("GetUser", 1).Return(&User{VIPLevel: 2}, nil)
	result, err := NewDiscountService(mockRepo).CalculateDiscount(1, 0)
	assert.NoError(t, err)
	assert.Equal(t, 0.0, result)
}

func TestCalculateDiscount_UserNotFound(t *testing.T) {
	mockRepo := new(MockRepository)
	mockRepo.On("GetUser", 999).Return(nil, errors.New("user not found"))
	_, err := NewDiscountService(mockRepo).CalculateDiscount(999, 100)
	assert.Error(t, err)
}

func TestOrderStateMachine_ValidTransitions(t *testing.T) {
	testCases := []struct {
		currentState, action, expected string
	}{
		{"pending", "pay", "paid"},
		{"paid", "ship", "shipped"},
		{"shipped", "receive", "completed"},
		{"pending", "cancel", "cancelled"},
	}

	for _, tc := range testCases {
		t.Run(tc.currentState+"_"+tc.action, func(t *testing.T) {
			order := &Order{Status: tc.currentState}
			err := NewOrderService().Transition(order, tc.action)
			assert.NoError(t, err)
			assert.Equal(t, tc.expected, order.Status)
		})
	}
}

func TestOrderStateMachine_InvalidTransitions(t *testing.T) {
	testCases := []struct{ currentState, action string }{
		{"completed", "cancel"},
		{"cancelled", "pay"},
		{"pending", "ship"},
	}

	for _, tc := range testCases {
		t.Run(tc.currentState+"_"+tc.action, func(t *testing.T) {
			order := &Order{Status: tc.currentState}
			err := NewOrderService().Transition(order, tc.action)
			assert.Error(t, err)
		})
	}
}
```

---

## Java (JUnit 5 + Mockito)

```java
/**
 * Unit Tests for {module}
 * 保护目标：{description}
 */
package com.example.service;

import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class {ClassName}Test {

    @Mock private UserRepository userRepository;
    @Mock private CacheService cacheService;
    @InjectMocks private {ClassName} service;

    @Nested @DisplayName("calculateDiscount")
    class CalculateDiscountTests {

        @Test @DisplayName("VIP 用户应获得折扣")
        void vipUserGetsDiscount() {
            when(userRepository.findById(1L)).thenReturn(Optional.of(new User(1L, 2)));

            double result = service.calculateDiscount(1L, 100);

            assertThat(result).isEqualTo(90);
            verify(userRepository).findById(1L);
        }

        @Test @DisplayName("普通用户不享受折扣")
        void normalUserNoDiscount() {
            when(userRepository.findById(1L)).thenReturn(Optional.of(new User(1L, 0)));
            assertThat(service.calculateDiscount(1L, 100)).isEqualTo(100);
        }

        @Test @DisplayName("金额为 0 应返回 0")
        void zeroAmountReturnsZero() {
            when(userRepository.findById(1L)).thenReturn(Optional.of(new User(1L, 2)));
            assertThat(service.calculateDiscount(1L, 0)).isEqualTo(0);
        }

        @Test @DisplayName("用户不存在应抛出异常")
        void userNotFoundThrowsException() {
            when(userRepository.findById(999L)).thenReturn(Optional.empty());
            assertThatThrownBy(() -> service.calculateDiscount(999L, 100))
                .isInstanceOf(UserNotFoundException.class);
        }
    }

    @Nested @DisplayName("OrderStateMachine")
    class OrderStateMachineTests {

        @ParameterizedTest(name = "{0} + {1} -> {2}")
        @CsvSource({
            "pending, pay, paid",
            "paid, ship, shipped",
            "shipped, receive, completed",
            "pending, cancel, cancelled"
        })
        void validTransitions(String currentState, String action, String expectedState) {
            Order order = new Order(currentState);
            service.transition(order, action);
            assertThat(order.getStatus()).isEqualTo(expectedState);
        }

        @ParameterizedTest(name = "{0} + {1} -> Error")
        @CsvSource({ "completed, cancel", "cancelled, pay", "pending, ship" })
        void invalidTransitionsThrowException(String currentState, String action) {
            Order order = new Order(currentState);
            assertThatThrownBy(() -> service.transition(order, action))
                .isInstanceOf(InvalidTransitionException.class);
        }
    }
}
```

---

## 测试报告模板

```markdown
# {模块名称} 单元测试报告

| 项目 | 内容 |
|------|------|
| 测试模块 | {模块路径} |
| 测试目标 | {保护目标说明} |
| 生成时间 | {YYYY-MM-DD HH:mm} |
| 测试框架 | {pytest/vitest/go test/junit} |

## 测试用例统计

| 测试类/函数 | 场景 | Mock 依赖 | 预期结果 |
|-------------|------|-----------|----------|
| test_vip_user_gets_discount | VIP 用户折扣 | UserRepository | 返回 90 |
| test_invalid_transitions | 无效状态转换 | 无 | 抛出异常 |

## 成功标准

- [x] 只测试高风险/复杂逻辑
- [x] 正确使用 Mock 隔离外部依赖
- [x] 覆盖正常路径和关键边界条件
```
