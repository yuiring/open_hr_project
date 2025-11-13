#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI服务模块 - 处理自然语言请求并调用MCP工具
"""

import re
import json
import asyncio
from typing import Dict, Any, List, Optional
from database import execute_query

class AIService:
    """AI服务类，处理自然语言请求"""
    
    def __init__(self):
        self.intent_patterns = {
            'query': [
                r'查询|查找|搜索|找.*?([^\s，。！？的]+)',
                r'([^\s，。！？]+).*?信息|账号|资料',
                r'.*?([^\s，。！？]+).*?在.*?部门',
            ],
            'create': [
                r'新增|添加|创建.*?员工.*?([^\s，。！？]+).*?部门.*?([^\s，。！？]+部)',
                r'员工.*?([^\s，。！？]+).*?部门.*?([^\s，。！？]+部)',
                r'添加.*?([^\s，。！？]+).*?到.*?([^\s，。！？]+部)',
            ],
            'update': [
                r'修改|更改|改.*?([^\s，。！？]+).*?部门.*?([^\s，。！？]+部)',
                r'把.*?([^\s，。！？]+).*?改为|修改为|更改为.*?([^\s，。！？]+部)',
                r'([^\s，。！？]+).*?转到|调到.*?([^\s，。！？]+部)',
            ]
        }
    
    def extract_intent_and_entities(self, message: str) -> Dict[str, Any]:
        """提取用户意图和实体"""
        message = message.strip()
        
        # 查询意图
        for pattern in self.intent_patterns['query']:
            match = re.search(pattern, message)
            if match:
                return {
                    'intent': 'query',
                    'entities': {
                        'name': match.group(1) if match.group(1) else None
                    }
                }
        
        # 创建意图
        for pattern in self.intent_patterns['create']:
            match = re.search(pattern, message)
            if match:
                if len(match.groups()) >= 2:
                    return {
                        'intent': 'create',
                        'entities': {
                            'name': match.group(1),
                            'department': match.group(2)
                        }
                    }
        
        # 更新意图
        for pattern in self.intent_patterns['update']:
            match = re.search(pattern, message)
            if match:
                if len(match.groups()) >= 2:
                    return {
                        'intent': 'update',
                        'entities': {
                            'name': match.group(1),
                            'department': match.group(2)
                        }
                    }
        
        return {
            'intent': 'unknown',
            'entities': {}
        }
    
    async def process_query_intent(self, entities: Dict[str, Any]) -> str:
        """处理查询意图"""
        name = entities.get('name')
        if not name:
            return "请提供要查询的员工姓名。"
        
        try:
            employees = execute_query("SELECT * FROM employee WHERE name LIKE ? ORDER BY name", (f"%{name}%",))
            
            if not employees:
                return f"未找到姓名包含'{name}'的员工。"
            
            if len(employees) == 1:
                emp = employees[0]
                return f"""找到员工信息：
• 姓名：{emp['name']}
• 工号：{emp['employee_id']}
• 部门：{emp['department']}
• HR账号：{emp['hr_account']}
• 状态：{emp['status']}"""
            else:
                result = f"找到 {len(employees)} 名员工：\n\n"
                for emp in employees:
                    result += f"• {emp['name']} ({emp['employee_id']}) - {emp['department']} - {emp['status']}\n"
                return result
                
        except Exception as e:
            return f"查询员工信息时出现错误：{str(e)}"
    
    async def process_create_intent(self, entities: Dict[str, Any]) -> str:
        """处理创建意图"""
        name = entities.get('name')
        department = entities.get('department')
        
        if not name or not department:
            return "请提供完整的员工信息，包括姓名和部门。"
        
        try:
            # 生成员工工号
            result = execute_query("SELECT employee_id FROM employee WHERE employee_id LIKE 'EMP%' ORDER BY employee_id DESC LIMIT 1")
            if result:
                last_id = result[0]['employee_id']
                num = int(last_id[3:]) + 1
                employee_id = f"EMP{num:03d}"
            else:
                employee_id = "EMP001"
            
            # 生成HR账号
            hr_account = f"{name.lower()}@company.com"
            
            # 检查工号是否已存在
            existing = execute_query("SELECT id FROM employee WHERE employee_id = ?", (employee_id,))
            if existing:
                return f"工号 {employee_id} 已存在，请重试。"
            
            # 插入新员工
            sql = """
                INSERT INTO employee (name, employee_id, department, hr_account, status)
                VALUES (?, ?, ?, ?, '在职')
            """
            execute_query(sql, (name, employee_id, department, hr_account))
            
            return f"""员工创建成功！
• 姓名：{name}
• 工号：{employee_id}
• 部门：{department}
• HR账号：{hr_account}
• 状态：在职"""
            
        except Exception as e:
            return f"创建员工时出现错误：{str(e)}"
    
    async def process_update_intent(self, entities: Dict[str, Any]) -> str:
        """处理更新意图"""
        name = entities.get('name')
        new_department = entities.get('department')
        
        if not name or not new_department:
            return "请提供要修改的员工姓名和新的部门信息。"
        
        try:
            # 查找员工
            employees = execute_query("SELECT * FROM employee WHERE name = ?", (name,))
            
            if not employees:
                return f"未找到员工'{name}'。"
            
            if len(employees) > 1:
                result = f"找到多个名为'{name}'的员工，请提供更具体的信息：\n"
                for emp in employees:
                    result += f"• {emp['name']} ({emp['employee_id']}) - {emp['department']}\n"
                return result
            
            employee = employees[0]
            old_department = employee['department']
            
            # 更新员工信息
            execute_query(
                "UPDATE employee SET department = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_department, employee['id'])
            )
            
            return f"已成功将{name}的部门从'{old_department}'修改为'{new_department}'。"
            
        except Exception as e:
            return f"修改员工信息时出现错误：{str(e)}"
    
    async def process_message(self, message: str) -> str:
        """处理用户消息"""
        # 提取意图和实体
        result = self.extract_intent_and_entities(message)
        intent = result['intent']
        entities = result['entities']
        
        # 根据意图处理请求
        if intent == 'query':
            return await self.process_query_intent(entities)
        elif intent == 'create':
            return await self.process_create_intent(entities)
        elif intent == 'update':
            return await self.process_update_intent(entities)
        else:
            return self.get_help_message()
    
    def get_help_message(self) -> str:
        """获取帮助信息"""
        return """我可以帮您：

🔍 **查询员工信息**
• "查询张三的人事账号"
• "搜索李四的信息"
• "找王五的资料"

➕ **新增员工**
• "新增一个员工王小敏，部门是市场部"
• "添加员工赵六到技术部"
• "创建员工孙七，部门财务部"

✏️ **修改员工信息**
• "把李四的部门改为行政部"
• "修改张三的部门为人事部"
• "将王五调到市场部"

请告诉我您需要什么帮助？"""

# 全局AI服务实例
ai_service = AIService()

async def process_ai_request(message: str) -> str:
    """处理AI请求的入口函数"""
    return await ai_service.process_message(message)