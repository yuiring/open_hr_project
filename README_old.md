# AI + MCP 智能人力资源助手项目

## 项目简介

基于大模型与 MCP 技术的智能人力资源管理系统，实现自然语言对话式查询员工账号信息，提高HR工作效率。

## 项目架构

```
open_hr_project/
├── backend/                 # 后端API服务
│   ├── app.py              # Flask应用主文件
│   ├── models.py           # 数据模型
│   ├── database.py         # 数据库配置
│   └── requirements.txt    # Python依赖
├── mcp-server/             # MCP服务器
│   ├── hr_mcp_server.py    # MCP服务器实现
│   └── requirements.txt    # MCP依赖
├── frontend/               # 前端界面
│   ├── index.html          # 主页面
│   ├── style.css           # 样式文件
│   └── script.js           # 前端逻辑
├── database/               # 数据库文件
│   └── hr_system.db        # SQLite数据库
└── docs/                   # 文档目录
    ├── API.md              # API文档
    └── USER_GUIDE.md       # 使用指南

```

## 核心功能

1. **查询员工账号**：通过自然语言查询员工信息
2. **新增员工账号**：对话式添加新员工
3. **修改员工信息**：智能识别并修改员工部门等信息

## 技术栈

- **后端**：Python Flask + SQLite
- **前端**：HTML + CSS + JavaScript
- **MCP**：Model Context Protocol 集成
- **AI**：大模型自然语言处理

## 快速开始

### 1. 安装依赖

```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# MCP服务器依赖
cd ../mcp-server
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
cd backend
python database.py
```

### 3. 启动服务

```bash
# 启动后端API服务
cd backend
python app.py

# 启动MCP服务器
cd ../mcp-server
python hr_mcp_server.py

# 启动前端服务
cd ../frontend
python -m http.server 8080
```

### 4. 访问应用

- 前端界面：http://localhost:8080
- API文档：http://localhost:5000/docs

## 使用示例

### 查询员工
```
用户：查询张三的人事账号
AI：张三的信息如下：
- 姓名：张三
- 工号：EMP001
- 部门：技术部
- HR账号：zhangsan@company.com
- 状态：在职
```

### 新增员工
```
用户：新增一个员工王小敏，部门是市场部
AI：已成功创建员工王小敏，工号为EMP005，部门为市场部
```

### 修改员工信息
```
用户：把李四的部门改为行政部
AI：已成功将李四的部门修改为行政部
```

## 开发说明

本项目采用模块化设计，各组件职责清晰：

- **Backend**：提供RESTful API，处理数据库操作
- **MCP Server**：实现MCP协议，提供工具函数供AI调用
- **Frontend**：提供用户界面，包含传统表单和AI对话功能

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License