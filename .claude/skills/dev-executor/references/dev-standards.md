# 开发规范与错误处理指南

### 开发规范

#### 业界最佳实践

**1. SOLID 原则**
```
S - 单一职责原则 (SRP): 类/函数只负责一件事
O - 开闭原则 (OCP): 对扩展开放，对修改关闭
L - 里氏替换原则 (LSP): 子类可替换父类
I - 接口隔离原则 (ISP): 客户端不应依赖它不需要的接口
D - 依赖倒置原则 (DIP): 依赖抽象而非具体实现
```

**2. Clean Code 原则**
- 函数保持短小（不超过 20 行）
- 有意义的命名
- 避免深层嵌套（不超过 3 层）
- DRY (Don't Repeat Yourself)
- KISS (Keep It Simple, Stupid)
- YAGNI (You Aren't Gonna Need It)

**3. 设计模式应用**
| 场景 | 推荐模式 |
|------|---------|
| 数据访问 | Repository Pattern |
| 依赖注入 | Dependency Injection |
| 对象创建 | Factory / Builder |
| 行为变化 | Strategy Pattern |
| 状态管理 | Observer / Pub-Sub |

**4. TDD 开发流程**
```
Red:   先写失败的测试
Green: 编写最少代码使测试通过
Refactor: 重构优化代码
```

**5. 代码审查清单**
- [ ] 代码符合团队规范
- [ ] 测试覆盖率 > 80%
- [ ] 无硬编码配置
- [ ] 错误处理完善
- [ ] 性能考虑合理
- [ ] 安全漏洞检查
- [ ] 注释清晰必要

#### 代码规范

**命名规范**:
```typescript
// 类名: PascalCase
class UserService {}

// 函数/变量: camelCase
const getUserById = async (id: string) => {};

// 常量: UPPER_SNAKE_CASE
const MAX_RETRY_COUNT = 3;

// 私有成员: # 或 _
class Example {
  #privateField = '';
}
```

**注释规范**:
```typescript
/**
 * 获取用户信息
 * @param userId - 用户ID
 * @returns 用户对象
 */
async getUser(userId: string) {
  // 实现
}
```

#### 测试规范

**测试文件命名**: `{源文件名}.spec.ts` 或 `{源文件名}.test.ts`

**测试结构**:
```typescript
describe('UserService', () => {
  describe('getUserById', () => {
    it('should return user when valid id provided', async () => {
      // Arrange
      const userId = 'user-123';

      // Act
      const result = await userService.getUserById(userId);

      // Assert
      expect(result).toBeDefined();
      expect(result.id).toBe(userId);
    });

    it('should throw error when user not found', async () => {
      // 测试不存在的情况
    });

    it('should throw error when invalid id provided', async () => {
      // 测试无效输入
    });
  });

  describe('createUser', () => {
    // 测试创建用户的场景
  });
});
```

**Mock 策略**:
```typescript
// Mock 外部依赖
jest.mock('../lib/database');
jest.mock('../lib/email');

// Mock 函数
const mockDb = database as jest.Mocked<typeof database>;
mockDb.query.mockResolvedValue(expectedUser);
```

#### Git 提交规范

每个模块完成后提交代码：
```bash
git add .
git commit -m "feat(module): implement {模块名称}

- 实现核心功能
- 添加单元测试（覆盖率 > 80%）
- 通过代码审查

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 错误处理策略

#### 编译错误
```bash
# 查看具体错误
npm run build

# 常见问题：
# - TypeScript 类型错误：检查类型定义
# - 依赖缺失：npm install
# - 配置错误：检查 tsconfig.json
```

#### 测试失败
```typescript
// 1. 分析失败原因
// 使用 only 单独运行失败的测试
it.only('failing test', () => {
  // ...
});

// 2. 添加调试日志
console.log('Expected:', expected);
console.log('Actual:', actual);

// 3. 检查 Mock 配置
// 确保外部依赖正确 Mock

// 4. 逐步验证
// 分步骤调试，找出问题点
```

#### 覆盖率不足
```bash
# 生成详细覆盖率报告
npm run test:coverage -- --verbose

# 查看未覆盖的代码
open coverage/lcov-report/index.html

# 补充测试用例：
# - 分支覆盖：if/else 的所有分支
# - 条件覆盖：复杂的条件表达式
# - 行覆盖：未执行的代码行
```
