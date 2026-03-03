# 开发指南

开发规范、最佳实践和常见任务说明。

## 开发环境设置

### IDE 推荐

- **Java**: IntelliJ IDEA / Eclipse
- **Python**: PyCharm / VS Code
- **前端**: VS Code / WebStorm

### 必要插件

**IntelliJ IDEA**:
- Lombok
- Spring Boot Assistant
- Database Tools and SQL

**VS Code**:
- Python
- Pylance
- Vue - Official
- Prettier
- ESLint

### 代码风格

#### Java

```java
// 使用 Google Java Style Guide
// 缩进: 4 个空格
// 行长: 100 字符

public class UserService {
    private final UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public User getUserById(String id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new NotFoundException("User not found"));
    }
}
```

#### Python

```python
# 使用 PEP 8 风格
# 缩进: 4 个空格
# 行长: 100 字符

from typing import List, Optional

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """获取用户信息"""
        return self.user_repository.find_by_id(user_id)
```

#### Vue/TypeScript

```typescript
// 使用 Prettier 格式化
// 缩进: 2 个空格
// 行长: 100 字符

<script setup lang="ts">
import { ref, computed } from 'vue'

interface User {
  id: string
  name: string
  email: string
}

const users = ref<User[]>([])

const activeUsers = computed(() => {
  return users.value.filter(u => u.status === 'active')
})
</script>
```

---

## 项目结构

### Java 后端

```
src/main/java/com/riskcontrol/
├── controller/          # API 控制器
│   ├── RiskCaseController.java
│   ├── UserController.java
│   ├── PromptTemplateController.java
│   ├── CaseAuditLogController.java
│   └── AnalyticsController.java
├── service/             # 业务逻辑
│   ├── RiskCaseService.java
│   ├── UserService.java
│   ├── PromptTemplateService.java
│   ├── CaseAuditLogService.java
│   ├── AnalyticsService.java
│   └── AIService.java
├── entity/              # 数据实体
│   ├── User.java
│   ├── RiskCase.java
│   ├── AIDecisionRecord.java
│   ├── PromptTemplate.java
│   ├── CaseAuditLog.java
│   └── AIPromptLog.java
├── repository/          # 数据访问
│   ├── UserRepository.java
│   ├── RiskCaseRepository.java
│   ├── AIDecisionRecordRepository.java
│   ├── PromptTemplateRepository.java
│   └── CaseAuditLogRepository.java
├── dto/                 # 数据传输对象
│   ├── UserDTO.java
│   ├── RiskCaseDTO.java
│   ├── AIAnalysisDTO.java
│   ├── PromptTemplateDTO.java
│   └── CaseAuditLogDTO.java
├── config/              # 配置类
│   ├── SecurityConfig.java
│   ├── RestTemplateConfig.java
│   └── SwaggerConfig.java
├── exception/           # 异常处理
│   ├── GlobalExceptionHandler.java
│   ├── NotFoundException.java
│   └── BusinessException.java
└── client/              # 外部服务客户端
    └── AIClient.java
```

### Python AI 服务

```
ai-service/
├── src/
│   ├── agent/           # AI Agent
│   │   ├── agent.py
│   │   ├── tools.py
│   │   ├── executor.py
│   │   └── __init__.py
│   ├── api/             # API 路由
│   │   ├── ai_routes.py
│   │   ├── rag_routes.py
│   │   └── routes.py
│   ├── database/        # 数据库
│   │   ├── connection.py
│   │   └── models.py
│   ├── embedding/       # 向量化
│   │   └── embedding_model.py
│   ├── llm/             # LLM 客户端
│   │   └── client.py
│   ├── prompt/          # Prompt 管理
│   │   └── manager.py
│   ├── rag/             # RAG 检索
│   │   └── retriever.py
│   ├── services/        # 业务服务
│   │   └── ai_service.py
│   └── utils/           # 工具函数
│       └── logger.py
├── scripts/             # 脚本
│   ├── generate_mock_data.py
│   └── load_mock_data.py
├── app.py               # 应用入口
├── config.py            # 配置
└── requirements.txt     # 依赖
```

### 前端

```
frontend/
├── src/
│   ├── views/           # 页面组件
│   │   ├── Dashboard.vue
│   │   ├── CaseList.vue
│   │   ├── CaseDetail.vue
│   │   ├── PromptManagement.vue
│   │   ├── Analytics.vue
│   │   ├── AuditTrail.vue
│   │   ├── UserManagement.vue
│   │   └── Login.vue
│   ├── components/      # 可复用组件
│   │   ├── CaseForm.vue
│   │   ├── AIAnalysis.vue
│   │   └── ...
│   ├── api/             # API 调用
│   │   ├── caseApi.ts
│   │   ├── promptApi.ts
│   │   └── analyticsApi.ts
│   ├── stores/          # Pinia 状态管理
│   │   ├── case.ts
│   │   ├── user.ts
│   │   └── ...
│   ├── router/          # 路由配置
│   │   └── index.ts
│   ├── App.vue          # 根组件
│   └── main.ts          # 入口文件
├── public/              # 静态资源
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## 常见开发任务

### 1. 添加新的 API 端点

#### 步骤 1: 创建 Entity

```java
@Entity
@Table(name = "new_entity")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class NewEntity {
    @Id
    private String id;
    
    @Column(nullable = false)
    private String name;
    
    @CreationTimestamp
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    private LocalDateTime updatedAt;
}
```

#### 步骤 2: 创建 Repository

```java
@Repository
public interface NewEntityRepository extends JpaRepository<NewEntity, String> {
    Optional<NewEntity> findByName(String name);
    List<NewEntity> findByCreatedAtAfter(LocalDateTime date);
}
```

#### 步骤 3: 创建 DTO

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class NewEntityDTO {
    private String id;
    private String name;
    private LocalDateTime createdAt;
}
```

#### 步骤 4: 创建 Service

```java
@Service
@Slf4j
public class NewEntityService {
    private final NewEntityRepository repository;
    
    public NewEntityService(NewEntityRepository repository) {
        this.repository = repository;
    }
    
    public NewEntityDTO create(NewEntityDTO dto) {
        NewEntity entity = new NewEntity();
        entity.setId(UUID.randomUUID().toString());
        entity.setName(dto.getName());
        
        NewEntity saved = repository.save(entity);
        return convertToDTO(saved);
    }
    
    public NewEntityDTO getById(String id) {
        return repository.findById(id)
            .map(this::convertToDTO)
            .orElseThrow(() -> new NotFoundException("Entity not found"));
    }
    
    private NewEntityDTO convertToDTO(NewEntity entity) {
        return new NewEntityDTO(
            entity.getId(),
            entity.getName(),
            entity.getCreatedAt()
        );
    }
}
```

#### 步骤 5: 创建 Controller

```java
@RestController
@RequestMapping("/api/new-entities")
@Slf4j
public class NewEntityController {
    private final NewEntityService service;
    
    public NewEntityController(NewEntityService service) {
        this.service = service;
    }
    
    @PostMapping
    @ApiOperation("创建新实体")
    public ResponseEntity<NewEntityDTO> create(@RequestBody NewEntityDTO dto) {
        return ResponseEntity.ok(service.create(dto));
    }
    
    @GetMapping("/{id}")
    @ApiOperation("获取实体详情")
    public ResponseEntity<NewEntityDTO> getById(@PathVariable String id) {
        return ResponseEntity.ok(service.getById(id));
    }
}
```

#### 步骤 6: 编写测试

```java
@SpringBootTest
class NewEntityServiceTest {
    @MockBean
    private NewEntityRepository repository;
    
    @InjectMocks
    private NewEntityService service;
    
    @Test
    void testCreate() {
        NewEntityDTO dto = new NewEntityDTO(null, "Test", null);
        NewEntity entity = new NewEntity("1", "Test", LocalDateTime.now(), LocalDateTime.now());
        
        when(repository.save(any())).thenReturn(entity);
        
        NewEntityDTO result = service.create(dto);
        
        assertNotNull(result.getId());
        assertEquals("Test", result.getName());
    }
}
```

### 2. 添加新的 Tool

#### 步骤 1: 创建 Tool 类

```python
from src.agent.tools import Tool

class NewTool(Tool):
    def __init__(self):
        super().__init__(
            name="new_tool",
            description="新工具的描述"
        )
    
    def execute(self, **kwargs):
        """执行工具"""
        try:
            # 实现工具逻辑
            result = self._do_something(**kwargs)
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _do_something(self, **kwargs):
        # 具体实现
        pass
```

#### 步骤 2: 注册 Tool

```python
# src/agent/tools.py

def get_tools():
    return [
        RetrieveSimilarCasesTool(),
        QueryRuleEngineTool(),
        AnalyzeSimilarCasesTool(),
        QueryTransactionHistoryTool(),
        NewTool()  # 添加新工具
    ]
```

#### 步骤 3: 编写测试

```python
import pytest
from src.agent.tools import NewTool

def test_new_tool():
    tool = NewTool()
    result = tool.execute(param1="value1")
    
    assert result["status"] == "success"
    assert "data" in result
```

### 3. 添加新的前端页面

#### 步骤 1: 创建 Vue 组件

```vue
<template>
  <div class="new-page">
    <a-card title="新页面">
      <a-table :columns="columns" :data-source="data" />
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getNewEntities } from '@/api/newEntityApi'

interface NewEntity {
  id: string
  name: string
  createdAt: string
}

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id' },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt' }
]

const data = ref<NewEntity[]>([])

onMounted(async () => {
  const response = await getNewEntities()
  data.value = response.data
})
</script>

<style scoped>
.new-page {
  padding: 20px;
}
</style>
```

#### 步骤 2: 创建 API 调用

```typescript
// src/api/newEntityApi.ts

import axios from 'axios'

export function getNewEntities() {
  return axios.get('/api/new-entities')
}

export function getNewEntityById(id: string) {
  return axios.get(`/api/new-entities/${id}`)
}

export function createNewEntity(data: any) {
  return axios.post('/api/new-entities', data)
}
```

#### 步骤 3: 添加路由

```typescript
// src/router/index.ts

const routes = [
  {
    path: '/new-page',
    component: () => import('@/views/NewPage.vue'),
    meta: { title: '新页面' }
  }
]
```

#### 步骤 4: 添加菜单

```vue
<!-- src/App.vue -->

<a-menu>
  <a-menu-item key="new-page">
    <router-link to="/new-page">新页面</router-link>
  </a-menu-item>
</a-menu>
```

---

## 测试指南

### 单元测试

```bash
# Java
mvn test

# Python
pytest

# 前端
npm run test
```

### 集成测试

```bash
# Java
mvn verify

# Python
pytest --cov=src
```

### 测试覆盖率

```bash
# Java
mvn jacoco:report

# Python
pytest --cov=src --cov-report=html
```

---

## 调试技巧

### Java 调试

```
1. 在 IDE 中设置断点
2. 以 Debug 模式运行应用
3. 使用 Debug 工具栏单步执行
4. 查看变量值和调用栈
```

### Python 调试

```python
# 使用 pdb
import pdb; pdb.set_trace()

# 或使用 IDE 调试器
# PyCharm: 右键 -> Debug
```

### 前端调试

```
1. 打开浏览器开发者工具 (F12)
2. 在 Sources 标签中设置断点
3. 刷新页面触发断点
4. 使用 Console 查看变量
```

---

## 性能优化

### Java 优化

```java
// 使用缓存
@Cacheable("users")
public User getUserById(String id) {
    return repository.findById(id).orElse(null);
}

// 使用异步处理
@Async
public void processLargeData() {
    // 处理大数据
}

// 使用批量操作
repository.saveAll(entities);
```

### Python 优化

```python
# 使用缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user(user_id):
    return db.query(User).filter(User.id == user_id).first()

# 使用异步
import asyncio

async def process_data():
    await asyncio.gather(task1(), task2())
```

### 前端优化

```typescript
// 代码分割
const NewPage = () => import('@/views/NewPage.vue')

// 虚拟滚动
<a-virtual-list :data="largeList" />

// 防抖和节流
import { debounce } from 'lodash-es'
const handleSearch = debounce(search, 300)
```

---

## 常见问题

### Q1: 如何快速启动开发环境？

A: 使用 Docker Compose:
```bash
docker-compose up -d
```

### Q2: 如何调试 Java-Python 通信？

A: 
1. 在 AIClient 中添加日志
2. 在 Python 服务中添加日志
3. 使用 Postman 测试 API

### Q3: 如何处理数据库迁移？

A: 使用 Flyway 或 Liquibase 管理数据库版本

### Q4: 如何优化前端加载速度？

A:
- 启用 gzip 压缩
- 使用 CDN
- 代码分割
- 图片优化

### Q5: 如何处理并发问题？

A:
- 使用数据库锁
- 使用 Redis 分布式锁
- 使用乐观锁

---

## 最佳实践

### 1. 代码审查

- 所有代码必须通过 Pull Request 审查
- 至少需要 1 个批准
- 必须通过 CI/CD 检查

### 2. 提交信息

```
<type>(<scope>): <subject>

<body>

<footer>

示例:
feat(case): add case filtering
fix(api): fix null pointer exception
docs(readme): update installation guide
```

### 3. 分支管理

```
main: 生产分支
develop: 开发分支
feature/xxx: 功能分支
bugfix/xxx: 修复分支
```

### 4. 版本管理

```
使用 Semantic Versioning
v1.2.3
- 1: 主版本 (breaking changes)
- 2: 次版本 (新功能)
- 3: 修订版本 (bug 修复)
```

### 5. 文档

- 为所有公共 API 添加文档
- 为复杂逻辑添加注释
- 维护 README 和开发指南

---

## 有用的命令

### Java

```bash
# 构建
mvn clean install

# 运行测试
mvn test

# 生成 Javadoc
mvn javadoc:javadoc

# 检查代码质量
mvn sonar:sonar
```

### Python

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest

# 代码格式化
black src/

# 代码检查
flake8 src/
```

### 前端

```bash
# 安装依赖
npm install

# 开发
npm run dev

# 构建
npm run build

# 代码格式化
npm run format

# 代码检查
npm run lint
```

---

## 资源链接

- [Spring Boot 文档](https://spring.io/projects/spring-boot)
- [Flask 文档](https://flask.palletsprojects.com/)
- [Vue 3 文档](https://vuejs.org/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [Docker 文档](https://docs.docker.com/)
- [Kubernetes 文档](https://kubernetes.io/docs/)
