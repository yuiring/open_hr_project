#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版HR系统后端API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import json

app = Flask(__name__)
CORS(app)

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'hr_system.db')

class APIResponse:
    def __init__(self, success=True, message="", data=None):
        self.success = success
        self.message = message
        self.data = data or {}
    
    def to_dict(self):
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data
        }

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify(APIResponse(True, "HR系统运行正常").to_dict())

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """获取员工列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        name = request.args.get('name')
        if name:
            cursor.execute("SELECT * FROM employee WHERE name LIKE ?", (f'%{name}%',))
        else:
            cursor.execute("SELECT * FROM employee")
        
        employees = []
        for row in cursor.fetchall():
            employees.append({
                'id': row['id'],
                'name': row['name'],
                'department': row['department'],
                'hr_account': row['hr_account'],
                'status': row['status']
            })
        
        conn.close()
        return jsonify(APIResponse(True, "查询成功", {'employees': employees}).to_dict())
    
    except Exception as e:
        return jsonify(APIResponse(False, f"查询失败: {str(e)}").to_dict()), 500

@app.route('/api/employees', methods=['POST'])
def create_employee():
    """新增员工"""
    try:
        data = request.get_json()
        name = data.get('name')
        department = data.get('department')
        
        if not name or not department:
            return jsonify(APIResponse(False, "姓名和部门不能为空").to_dict()), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 生成员工ID和HR账号
        employee_id = f"EMP{hash(name) % 10000:04d}"
        hr_account = f"HR{name[:2]}{hash(name) % 10000:04d}"
        
        cursor.execute("""
            INSERT INTO employee (name, employee_id, department, hr_account, status)
            VALUES (?, ?, ?, ?, ?)
        """, (name, employee_id, department, hr_account, '在职'))
        
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify(APIResponse(True, "员工创建成功", {
            'employee': {
                'id': new_id,
                'name': name,
                'employee_id': employee_id,
                'department': department,
                'hr_account': hr_account,
                'status': '在职'
            }
        }).to_dict())
    
    except Exception as e:
        return jsonify(APIResponse(False, f"创建失败: {str(e)}").to_dict()), 500

@app.route('/api/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """更新员工信息"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查员工是否存在
        cursor.execute("SELECT * FROM employee WHERE id = ?", (employee_id,))
        employee = cursor.fetchone()
        
        if not employee:
            conn.close()
            return jsonify(APIResponse(False, "员工不存在").to_dict()), 404
        
        # 更新字段
        update_fields = []
        params = []
        
        if 'department' in data:
            update_fields.append("department = ?")
            params.append(data['department'])
        
        if 'status' in data:
            update_fields.append("status = ?")
            params.append(data['status'])
        
        if update_fields:
            params.append(employee_id)
            cursor.execute(f"UPDATE employee SET {', '.join(update_fields)} WHERE id = ?", params)
            conn.commit()
        
        # 获取更新后的员工信息
        cursor.execute("SELECT * FROM employee WHERE id = ?", (employee_id,))
        updated_employee = cursor.fetchone()
        
        conn.close()
        
        return jsonify(APIResponse(True, "员工信息更新成功", {
            'employee': {
                'id': updated_employee['id'],
                'name': updated_employee['name'],
                'department': updated_employee['department'],
                'hr_account': updated_employee['hr_account'],
                'status': updated_employee['status']
            }
        }).to_dict())
    
    except Exception as e:
        return jsonify(APIResponse(False, f"更新失败: {str(e)}").to_dict()), 500

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """AI对话接口"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify(APIResponse(False, "消息不能为空").to_dict()), 400
        
        # 简单的自然语言处理
        response = process_hr_request(message)
        
        return jsonify(APIResponse(True, "处理成功", {'response': response}).to_dict())
    
    except Exception as e:
        return jsonify(APIResponse(False, f"处理失败: {str(e)}").to_dict()), 500

def process_hr_request(message):
    """处理HR请求"""
    message = message.lower()
    
    # 查询员工信息
    if any(keyword in message for keyword in ['查询', '搜索', '找', '查找']):
        # 提取姓名
        names = ['张三', '李四', '王五', '赵六', '孙七', '王小敏']
        found_name = None
        for name in names:
            if name in message:
                found_name = name
                break
        
        if found_name:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM employee WHERE name = ?", (found_name,))
                employee = cursor.fetchone()
                conn.close()
                
                if employee:
                    return f"找到员工信息：\n姓名：{employee['name']}\n部门：{employee['department']}\nHR账号：{employee['hr_account']}\n状态：{employee['status']}"
                else:
                    return f"未找到员工 {found_name} 的信息"
            except Exception as e:
                return f"查询出错：{str(e)}"
        else:
            return "请提供要查询的员工姓名"
    
    # 新增员工
    elif any(keyword in message for keyword in ['新增', '添加', '创建']):
        # 简单提取姓名和部门
        import re
        name_match = re.search(r'员工([^，,\s到]+)', message)
        dept_match = re.search(r'部门[是为]?([^，,\s]+)', message) or re.search(r'到([^，,\s]*部)', message) or re.search(r'，部门([^，,\s]+)', message)
        
        if name_match and dept_match:
            name = name_match.group(1)
            department = dept_match.group(1)
            
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # 检查员工是否已存在
                cursor.execute("SELECT * FROM employee WHERE name = ?", (name,))
                if cursor.fetchone():
                    conn.close()
                    return f"员工 {name} 已存在"
                
                # 生成员工ID和HR账号
                employee_id = f"EMP{hash(name) % 10000:04d}"
                hr_account = f"HR{name[:2]}{hash(name) % 10000:04d}"
                
                cursor.execute("""
                    INSERT INTO employee (name, employee_id, department, hr_account, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, employee_id, department, hr_account, '在职'))
                
                conn.commit()
                conn.close()
                
                return f"成功创建员工：\n姓名：{name}\n员工ID：{employee_id}\n部门：{department}\nHR账号：{hr_account}\n状态：在职"
            except Exception as e:
                return f"创建员工失败：{str(e)}"
        else:
            return "请提供员工姓名和部门信息，例如：新增员工张三，部门是技术部"
    
    # 修改员工信息
    elif any(keyword in message for keyword in ['修改', '改为', '调到', '更新', '把']):
        # 提取姓名和新部门
        import re
        name_match = (re.search(r'把([^，,\s的]+)', message) or 
                     re.search(r'([^，,\s]+)的部门', message) or 
                     re.search(r'将([^，,\s]+)调到', message) or
                     re.search(r'修改([^，,\s]+)的', message))
        dept_match = (re.search(r'改为([^，,\s]+)', message) or 
                     re.search(r'调到([^，,\s]+)', message) or
                     re.search(r'为([^，,\s]+部)', message))
        
        if name_match and dept_match:
            name = name_match.group(1)
            new_department = dept_match.group(1)
            
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # 查找员工
                cursor.execute("SELECT * FROM employee WHERE name = ?", (name,))
                employee = cursor.fetchone()
                
                if not employee:
                    conn.close()
                    return f"未找到员工 {name}"
                
                # 更新部门
                cursor.execute("UPDATE employee SET department = ? WHERE name = ?", (new_department, name))
                conn.commit()
                conn.close()
                
                return f"成功修改员工信息：\n姓名：{name}\n新部门：{new_department}"
            except Exception as e:
                return f"修改员工信息失败：{str(e)}"
        else:
            return "请提供员工姓名和新部门，例如：把张三的部门改为行政部"
    
    else:
        return "我可以帮您：\n1. 查询员工信息（例如：查询张三的人事账号）\n2. 新增员工（例如：新增员工王小敏，部门是市场部）\n3. 修改员工部门（例如：把李四的部门改为行政部）"

if __name__ == '__main__':
    print("启动简化版HR系统后端服务...")
    print("API文档: http://localhost:9000/api/health")
    print("AI对话接口: http://localhost:9000/api/ai/chat")
    app.run(host='0.0.0.0', port=9000, debug=False)