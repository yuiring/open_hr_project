#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HR系统MCP服务器
提供员工信息管理的工具函数供AI调用
"""

import asyncio
import json
import sys
import os
import sqlite3
import requests
from typing import Any, Dict, List, Optional

# 添加父目录到路径，以便导入backend模块
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel
    )
    MCP_AVAILABLE = True
except ImportError:
    print("MCP库未安装，将使用简化版本")
    MCP_AVAILABLE = False

from backend.database import execute_query, get_connection

# 后端API基础URL
API_BASE_URL = "http://localhost:5000/api"

class HRMCPServer:
    """HR系统MCP服务器"""
    
    def __init__(self):
        if MCP_AVAILABLE:
            self.server = Server("hr-assistant")
        self.tools = self._register_tools()
    
    def _register_tools(self):
        """注册工具函数"""
        tools = {
            "search_employee": {
                "name": "search_employee",
                "description": "根据姓名搜索员工信息，支持模糊匹配",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "员工姓名（支持部分匹配）"
                        }
                    },
                    "required": ["name"]
                }
            },
            "get_employee_by_id": {
                "name": "get_employee_by_id",
                "description": "根据工号获取员工详细信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "员工工号，如EMP001"
                        }
                    },
                    "required": ["employee_id"]
                }
            },
            "create_employee": {
                "name": "create_employee",
                "description": "创建新员工记录",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "员工姓名"
                        },
                        "department": {
                            "type": "string",
                            "description": "所属部门"
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "员工工号（可选，不提供则自动生成）"
                        },
                        "hr_account": {
                            "type": "string",
                            "description": "HR账号（可选，不提供则自动生成）"
                        }
                    },
                    "required": ["name", "department"]
                }
            },
            "update_employee": {
                "name": "update_employee",
                "description": "更新员工信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "员工姓名（用于查找员工）"
                        },
                        "department": {
                            "type": "string",
                            "description": "新的部门名称（可选）"
                        },
                        "hr_account": {
                            "type": "string",
                            "description": "新的HR账号（可选）"
                        },
                        "status": {
                            "type": "string",
                            "description": "员工状态：在职或离职（可选）"
                        }
                    },
                    "required": ["name"]
                }
            },
            "list_employees": {
                "name": "list_employees",
                "description": "获取员工列表，支持按部门和状态筛选",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "department": {
                            "type": "string",
                            "description": "部门名称（可选）"
                        },
                        "status": {
                            "type": "string",
                            "description": "员工状态：在职或离职（可选）"
                        }
                    }
                }
            },
            "get_departments": {
                "name": "get_departments",
                "description": "获取所有部门列表",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
        return tools
    
    async def search_employee(self, name: str) -> Dict[str, Any]:
        """搜索员工"""
        try:
            employees = execute_query("SELECT * FROM employee WHERE name LIKE ? ORDER BY name", (f"%{name}%",))
            
            if not employees:
                return {
                    "success": False,
                    "message": f"未找到姓名包含'{name}'的员工",
                    "data": {"employees": []}
                }
            
            return {
                "success": True,
                "message": f"找到 {len(employees)} 名员工",
                "data": {"employees": employees}
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"搜索失败: {str(e)}",
                "data": {"employees": []}
            }
    
    async def get_employee_by_id(self, employee_id: str) -> Dict[str, Any]:
        """根据工号获取员工信息"""
        try:
            employees = execute_query("SELECT * FROM employee WHERE employee_id = ?", (employee_id,))
            
            if not employees:
                return {
                    "success": False,
                    "message": f"未找到工号为'{employee_id}'的员工"
                }
            
            return {
                "success": True,
                "message": "查询成功",
                "data": {"employee": employees[0]}
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"查询失败: {str(e)}"
            }
    
    async def create_employee(self, name: str, department: str, employee_id: str = None, hr_account: str = None) -> Dict[str, Any]:
        """创建新员工"""
        try:
            # 如果没有提供工号，自动生成
            if not employee_id:
                result = execute_query("SELECT employee_id FROM employee WHERE employee_id LIKE 'EMP%' ORDER BY employee_id DESC LIMIT 1")
                if result:
                    last_id = result[0]['employee_id']
                    num = int(last_id[3:]) + 1
                    employee_id = f"EMP{num:03d}"
                else:
                    employee_id = "EMP001"
            
            # 如果没有提供HR账号，自动生成
            if not hr_account:
                hr_account = f"{name.lower()}@company.com"
            
            # 检查工号是否已存在
            existing = execute_query("SELECT id FROM employee WHERE employee_id = ?", (employee_id,))
            if existing:
                return {
                    "success": False,
                    "message": f"工号 {employee_id} 已存在"
                }
            
            # 插入新员工
            sql = """
                INSERT INTO employee (name, employee_id, department, hr_account, status)
                VALUES (?, ?, ?, ?, '在职')
            """
            execute_query(sql, (name, employee_id, department, hr_account))
            
            # 获取新创建的员工信息
            new_employee = execute_query("SELECT * FROM employee WHERE employee_id = ?", (employee_id,))
            
            return {
                "success": True,
                "message": f"员工 {name} 创建成功",
                "data": {"employee": new_employee[0]}
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"创建失败: {str(e)}"
            }
    
    async def update_employee(self, name: str, **kwargs) -> Dict[str, Any]:
        """更新员工信息"""
        try:
            # 先查找员工
            employees = execute_query("SELECT * FROM employee WHERE name = ?", (name,))
            
            if not employees:
                return {
                    "success": False,
                    "message": f"未找到员工 {name}"
                }
            
            if len(employees) > 1:
                return {
                    "success": False,
                    "message": f"找到多个名为 {name} 的员工，请提供更具体的信息",
                    "data": {"employees": employees}
                }
            
            employee = employees[0]
            emp_id = employee['id']
            
            # 构建更新语句
            update_fields = []
            params = []
            
            allowed_fields = ['department', 'hr_account', 'status']
            for field in allowed_fields:
                if field in kwargs and kwargs[field]:
                    update_fields.append(f"{field} = ?")
                    params.append(kwargs[field])
            
            if not update_fields:
                return {
                    "success": False,
                    "message": "没有提供有效的更新字段"
                }
            
            # 添加更新时间
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(emp_id)
            
            sql = f"UPDATE employee SET {', '.join(update_fields)} WHERE id = ?"
            execute_query(sql, params)
            
            # 获取更新后的员工信息
            updated_employee = execute_query("SELECT * FROM employee WHERE id = ?", (emp_id,))
            
            return {
                "success": True,
                "message": f"员工 {name} 信息更新成功",
                "data": {"employee": updated_employee[0]}
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"更新失败: {str(e)}"
            }
    
    async def list_employees(self, department: str = None, status: str = None) -> Dict[str, Any]:
        """获取员工列表"""
        try:
            conditions = []
            params = []
            
            if department:
                conditions.append("department = ?")
                params.append(department)
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            sql = f"SELECT * FROM employee WHERE {where_clause} ORDER BY created_at DESC"
            
            employees = execute_query(sql, params)
            
            return {
                "success": True,
                "message": f"查询成功，共找到 {len(employees)} 名员工",
                "data": {"employees": employees}
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"查询失败: {str(e)}",
                "data": {"employees": []}
            }
    
    async def get_departments(self) -> Dict[str, Any]:
        """获取部门列表"""
        try:
            departments = execute_query("SELECT DISTINCT department FROM employee WHERE status = '在职' ORDER BY department")
            dept_list = [dept['department'] for dept in departments]
            
            return {
                "success": True,
                "message": f"共有 {len(dept_list)} 个部门",
                "data": {"departments": dept_list}
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"查询失败: {str(e)}",
                "data": {"departments": []}
            }
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用"""
        if tool_name == "search_employee":
            return await self.search_employee(arguments["name"])
        elif tool_name == "get_employee_by_id":
            return await self.get_employee_by_id(arguments["employee_id"])
        elif tool_name == "create_employee":
            return await self.create_employee(**arguments)
        elif tool_name == "update_employee":
            return await self.update_employee(**arguments)
        elif tool_name == "list_employees":
            return await self.list_employees(
                arguments.get("department"),
                arguments.get("status")
            )
        elif tool_name == "get_departments":
            return await self.get_departments()
        else:
            return {
                "success": False,
                "message": f"未知的工具: {tool_name}"
            }

# 简化版本的MCP服务器（当MCP库不可用时）
class SimplifiedHRServer:
    """简化版HR服务器"""
    
    def __init__(self):
        self.hr_server = HRMCPServer()
    
    async def run_interactive(self):
        """交互式运行模式"""
        print("HR助手MCP服务器 (简化版)")
        print("可用工具:")
        for tool_name, tool_info in self.hr_server.tools.items():
            print(f"  - {tool_name}: {tool_info['description']}")
        
        print("\n输入 'help' 查看帮助，输入 'quit' 退出")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                # 解析命令
                parts = user_input.split(' ', 1)
                tool_name = parts[0]
                
                if tool_name not in self.hr_server.tools:
                    print(f"未知工具: {tool_name}")
                    continue
                
                # 解析参数
                if len(parts) > 1:
                    try:
                        arguments = json.loads(parts[1])
                    except json.JSONDecodeError:
                        # 简单参数解析
                        arguments = {"name": parts[1]} if tool_name in ["search_employee"] else {}
                else:
                    arguments = {}
                
                # 调用工具
                result = await self.hr_server.handle_tool_call(tool_name, arguments)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"错误: {e}")
        
        print("再见！")
    
    def show_help(self):
        """显示帮助信息"""
        print("\n使用方法:")
        print("  search_employee {\"name\": \"张三\"}")
        print("  get_employee_by_id {\"employee_id\": \"EMP001\"}")
        print("  create_employee {\"name\": \"新员工\", \"department\": \"技术部\"}")
        print("  update_employee {\"name\": \"张三\", \"department\": \"新部门\"}")
        print("  list_employees {\"department\": \"技术部\"}")
        print("  get_departments")

async def main():
    """主函数"""
    if MCP_AVAILABLE:
        # 使用完整的MCP服务器
        server = HRMCPServer()
        
        # 注册工具
        @server.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name=tool_info["name"],
                    description=tool_info["description"],
                    inputSchema=tool_info["inputSchema"]
                )
                for tool_info in server.tools.values()
            ]
        
        @server.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
            result = await server.handle_tool_call(name, arguments)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        # 运行服务器
        async with server.server.run_stdio():
            await asyncio.Event().wait()
    else:
        # 使用简化版本
        server = SimplifiedHRServer()
        await server.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())