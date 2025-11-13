#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HR系统后端API服务
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import uuid
import asyncio
from datetime import datetime
from database import execute_query, get_connection
from models import Employee, EmployeeQuery, APIResponse
from ai_service import process_ai_request

app = Flask(__name__)
CORS(app)  # 允许跨域请求

def generate_employee_id():
    """生成新的员工工号"""
    # 查询当前最大的员工编号
    result = execute_query("SELECT employee_id FROM employee WHERE employee_id LIKE 'EMP%' ORDER BY employee_id DESC LIMIT 1")
    
    if result:
        last_id = result[0]['employee_id']
        # 提取数字部分并加1
        num = int(last_id[3:]) + 1
        return f"EMP{num:03d}"
    else:
        return "EMP001"

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify(APIResponse(True, "服务正常运行").to_dict())

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """获取员工列表"""
    try:
        # 获取查询参数
        name = request.args.get('name')
        employee_id = request.args.get('employee_id')
        department = request.args.get('department')
        status = request.args.get('status')
        
        # 构建查询条件
        query = EmployeeQuery(name=name, employee_id=employee_id, department=department, status=status)
        where_clause, params = query.to_sql_where()
        
        sql = f"SELECT * FROM employee WHERE {where_clause} ORDER BY created_at DESC"
        employees = execute_query(sql, params)
        
        return jsonify(APIResponse(
            True, 
            f"查询成功，共找到 {len(employees)} 名员工",
            {'employees': employees}
        ).to_dict())
        
    except Exception as e:
        return jsonify(APIResponse(False, f"查询失败: {str(e)}").to_dict()), 500

@app.route('/api/employees/<int:emp_id>', methods=['GET'])
def get_employee_by_id(emp_id):
    """根据ID获取员工信息"""
    try:
        employees = execute_query("SELECT * FROM employee WHERE id = ?", (emp_id,))
        
        if not employees:
            return jsonify(APIResponse(False, "员工不存在").to_dict()), 404
        
        return jsonify(APIResponse(
            True, 
            "查询成功",
            {'employee': employees[0]}
        ).to_dict())
        
    except Exception as e:
        return jsonify(APIResponse(False, f"查询失败: {str(e)}").to_dict()), 500

@app.route('/api/employees/search', methods=['GET'])
def search_employees_by_name():
    """根据姓名搜索员工（支持模糊匹配）"""
    try:
        name = request.args.get('name')
        if not name:
            return jsonify(APIResponse(False, "请提供员工姓名").to_dict()), 400
        
        employees = execute_query("SELECT * FROM employee WHERE name LIKE ? ORDER BY name", (f"%{name}%",))
        
        if not employees:
            return jsonify(APIResponse(False, f"未找到姓名包含'{name}'的员工").to_dict())
        
        return jsonify(APIResponse(
            True, 
            f"找到 {len(employees)} 名员工",
            {'employees': employees}
        ).to_dict())
        
    except Exception as e:
        return jsonify(APIResponse(False, f"搜索失败: {str(e)}").to_dict()), 500

@app.route('/api/employees', methods=['POST'])
def create_employee():
    """创建新员工"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(APIResponse(False, "请提供员工信息").to_dict()), 400
        
        # 创建员工对象
        employee = Employee.from_dict(data)
        
        # 如果没有提供工号，自动生成
        if not employee.employee_id:
            employee.employee_id = generate_employee_id()
        
        # 如果没有提供HR账号，根据姓名生成
        if not employee.hr_account:
            # 简单的拼音转换（实际项目中可能需要更复杂的逻辑）
            employee.hr_account = f"{employee.name.lower()}@company.com"
        
        # 验证数据
        errors = employee.validate()
        if errors:
            return jsonify(APIResponse(False, f"数据验证失败: {', '.join(errors)}").to_dict()), 400
        
        # 检查工号是否已存在
        existing = execute_query("SELECT id FROM employee WHERE employee_id = ?", (employee.employee_id,))
        if existing:
            return jsonify(APIResponse(False, f"工号 {employee.employee_id} 已存在").to_dict()), 400
        
        # 插入数据库
        sql = """
            INSERT INTO employee (name, employee_id, department, hr_account, status)
            VALUES (?, ?, ?, ?, ?)
        """
        execute_query(sql, (employee.name, employee.employee_id, employee.department, 
                           employee.hr_account, employee.status))
        
        # 获取新创建的员工信息
        new_employee = execute_query("SELECT * FROM employee WHERE employee_id = ?", (employee.employee_id,))
        
        return jsonify(APIResponse(
            True, 
            f"员工 {employee.name} 创建成功",
            {'employee': new_employee[0]}
        ).to_dict()), 201
        
    except Exception as e:
        return jsonify(APIResponse(False, f"创建失败: {str(e)}").to_dict()), 500

@app.route('/api/employees/<int:emp_id>', methods=['PUT'])
def update_employee(emp_id):
    """更新员工信息"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(APIResponse(False, "请提供更新信息").to_dict()), 400
        
        # 检查员工是否存在
        existing = execute_query("SELECT * FROM employee WHERE id = ?", (emp_id,))
        if not existing:
            return jsonify(APIResponse(False, "员工不存在").to_dict()), 404
        
        # 构建更新语句
        update_fields = []
        params = []
        
        allowed_fields = ['name', 'department', 'hr_account', 'status']
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if not update_fields:
            return jsonify(APIResponse(False, "没有提供有效的更新字段").to_dict()), 400
        
        # 添加更新时间
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(emp_id)
        
        sql = f"UPDATE employee SET {', '.join(update_fields)} WHERE id = ?"
        execute_query(sql, params)
        
        # 获取更新后的员工信息
        updated_employee = execute_query("SELECT * FROM employee WHERE id = ?", (emp_id,))
        
        return jsonify(APIResponse(
            True, 
            f"员工信息更新成功",
            {'employee': updated_employee[0]}
        ).to_dict())
        
    except Exception as e:
        return jsonify(APIResponse(False, f"更新失败: {str(e)}").to_dict()), 500

@app.route('/api/employees/<int:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    """删除员工（软删除，设置状态为离职）"""
    try:
        # 检查员工是否存在
        existing = execute_query("SELECT * FROM employee WHERE id = ?", (emp_id,))
        if not existing:
            return jsonify(APIResponse(False, "员工不存在").to_dict()), 404
        
        # 软删除：设置状态为离职
        execute_query("UPDATE employee SET status = '离职', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (emp_id,))
        
        return jsonify(APIResponse(True, f"员工 {existing[0]['name']} 已设置为离职状态").to_dict())
        
    except Exception as e:
        return jsonify(APIResponse(False, f"删除失败: {str(e)}").to_dict()), 500

@app.route('/api/departments', methods=['GET'])
def get_departments():
    """获取所有部门列表"""
    try:
        departments = execute_query("SELECT DISTINCT department FROM employee WHERE status = '在职' ORDER BY department")
        dept_list = [dept['department'] for dept in departments]
        
        return jsonify(APIResponse(
            True, 
            f"共有 {len(dept_list)} 个部门",
            {'departments': dept_list}
        ).to_dict())
        
    except Exception as e:
        return jsonify(APIResponse(False, f"查询失败: {str(e)}").to_dict()), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """获取统计信息"""
    try:
        # 总员工数
        total = execute_query("SELECT COUNT(*) as count FROM employee")[0]['count']
        
        # 在职员工数
        active = execute_query("SELECT COUNT(*) as count FROM employee WHERE status = '在职'")[0]['count']
        
        # 各部门人数
        dept_stats = execute_query("""
            SELECT department, COUNT(*) as count 
            FROM employee 
            WHERE status = '在职' 
            GROUP BY department 
            ORDER BY count DESC
        """)
        
        stats = {
            'total_employees': total,
            'active_employees': active,
            'inactive_employees': total - active,
            'department_stats': dept_stats
        }
        
        return jsonify(APIResponse(
            True, 
            "统计信息获取成功",
            {'stats': stats}
        ).to_dict())
        
    except Exception as e:
        return jsonify(APIResponse(False, f"统计失败: {str(e)}").to_dict()), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify(APIResponse(False, "接口不存在").to_dict()), 404

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """AI对话接口"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify(APIResponse(False, "请提供消息内容").to_dict()), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify(APIResponse(False, "消息内容不能为空").to_dict()), 400
        
        # 使用asyncio运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(process_ai_request(message))
        finally:
            loop.close()
        
        return jsonify(APIResponse(
            True, 
            "处理成功",
            {'response': response}
        ).to_dict())
        
    except Exception as e:
        return jsonify(APIResponse(False, f"AI处理失败: {str(e)}").to_dict()), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify(APIResponse(False, "接口不存在").to_dict()), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify(APIResponse(False, "服务器内部错误").to_dict()), 500

if __name__ == '__main__':
    print("启动HR系统后端服务...")
    print("API文档: http://localhost:8080/api/health")
    print("AI对话接口: http://localhost:8080/api/ai/chat")
    app.run(host='0.0.0.0', port=8080, debug=True)