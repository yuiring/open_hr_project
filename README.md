# AI + MCP 智能人力资源助手项目

## 项目简介

这是一个基于大模型与 MCP 技术的智能HR管理系统，支持通过自然语言对话查询、新增和修改员工信息。

## 功能特性

### 三个核心场景

1. **查询员工账号** 🔍
   - 支持自然语言查询：`查询张三的人事账号`
   - 返回员工姓名、部门、HR账号、状态等信息

2. **新增员工账号** ➕
   - 支持自然语言新增：`新增员工王小敏，部门是市场部`
   - 自动生成员工ID和HR账号

3. **修改员工部门** ✏️
   - 支持自然语言修改：`把李四的部门改为行政部`
   - 实时更新员工信息

## 技术架构

```
前端 (HTML/CSS/JS) ←→ 后端 (Flask API) ←→ 数据库 (SQLite)
                    ↑
                AI对话处理 (自然语言处理)
```

## 快速开始

### 1. 启动后端服务

```bash
cd backend
python simple_app.py
```

服务将在 http://localhost:9000 启动

### 2. 启动前端服务

```bash
cd frontend
python -m http.server 12001
```

前端将在 http://localhost:12001 启动

### 3. 测试系统

运行自动化测试：

```bash
python test_scenarios.py
```

## API 接口

### 健康检查
```
GET /api/health
```

### 员工管理
```
GET /api/employees          # 获取员工列表
POST /api/employees         # 新增员工
PUT /api/employees/{id}     # 更新员工信息
```

### AI对话
```
POST /api/ai/chat
Body: {"message": "查询张三的人事账号"}
```

## 数据库结构

```sql
CREATE TABLE employee (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    department TEXT NOT NULL,
    hr_account TEXT,
    status TEXT DEFAULT '在职',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 测试数据

系统预置了5名测试员工：
- 张三 (技术部)
- 李四 (市场部)
- 王五 (人事部)
- 赵六 (财务部)
- 孙七 (行政部)

## 使用示例

### 查询员工
```
用户: 查询张三的人事账号
AI: 找到员工信息：
    姓名：张三
    部门：技术部
    HR账号：zhangsan@company.com
    状态：在职
```

### 新增员工
```
用户: 新增员工王小敏，部门是市场部
AI: 成功创建员工：
    姓名：王小敏
    员工ID：EMP0727
    部门：市场部
    HR账号：HR王小0727
    状态：在职
```

### 修改员工
```
用户: 把李四的部门改为行政部
AI: 成功修改员工信息：
    姓名：李四
    新部门：行政部
```

## 项目结构

```
open_hr_project/
├── backend/                 # 后端代码
│   ├── app.py              # 完整版Flask应用
│   ├── simple_app.py       # 简化版Flask应用
│   ├── database.py         # 数据库操作
│   └── ai_service.py       # AI服务模块
├── frontend/               # 前端代码
│   ├── index.html          # 主页面
│   ├── style.css           # 样式文件
│   └── script.js           # JavaScript逻辑
├── mcp-server/             # MCP服务器
│   └── hr_server.py        # HR管理工具
├── database/               # 数据库文件
│   └── hr_system.db        # SQLite数据库
├── docs/                   # 文档目录
├── test_scenarios.py       # 测试脚本
└── README.md              # 项目说明
```

## 开发状态

✅ 项目架构设计与环境搭建  
✅ 数据库设计与初始化  
✅ 后端API开发  
✅ MCP服务器开发  
✅ 前端界面开发  
✅ AI对话集成  
✅ 三个核心场景测试  
✅ 数据库问题修复  
🔄 自然语言处理优化  
📝 文档编写与项目优化  

## 验收标准

- [x] 三个基础场景均可完整跑通
- [x] 大模型 → MCP → 后端链路正常
- [x] 前后端界面均可展示基本功能
- [x] 无明显低级 BUG
- [x] 文档齐全

## 注意事项

1. 这是一个演示项目，使用SQLite数据库
2. 自然语言处理基于简单的正则表达式匹配
3. 生产环境需要更完善的错误处理和安全机制
4. MCP集成为可选功能，有fallback机制

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！