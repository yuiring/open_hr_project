#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库配置和初始化模块
"""

import sqlite3
import os
from datetime import datetime

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'hr_system.db')

def init_database():
    """初始化数据库，创建表结构"""
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建员工表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            employee_id TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            hr_account TEXT,
            status TEXT DEFAULT '在职',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_employee_name ON employee(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_employee_id ON employee(employee_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_department ON employee(department)')
    
    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")

def insert_sample_data():
    """插入示例数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查是否已有数据
    cursor.execute('SELECT COUNT(*) FROM employee')
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_employees = [
            ('张三', 'EMP001', '技术部', 'zhangsan@company.com', '在职'),
            ('李四', 'EMP002', '市场部', 'lisi@company.com', '在职'),
            ('王五', 'EMP003', '人事部', 'wangwu@company.com', '在职'),
            ('赵六', 'EMP004', '财务部', 'zhaoliu@company.com', '离职'),
            ('孙七', 'EMP005', '技术部', 'sunqi@company.com', '在职'),
        ]
        
        cursor.executemany('''
            INSERT INTO employee (name, employee_id, department, hr_account, status)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_employees)
        
        conn.commit()
        print(f"插入了 {len(sample_employees)} 条示例数据")
    else:
        print(f"数据库中已有 {count} 条记录，跳过示例数据插入")
    
    conn.close()

def get_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)

def execute_query(query, params=None):
    """执行查询语句"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    if query.strip().upper().startswith('SELECT'):
        result = cursor.fetchall()
        # 获取列名
        columns = [description[0] for description in cursor.description]
        # 转换为字典列表
        result = [dict(zip(columns, row)) for row in result]
    else:
        conn.commit()
        result = cursor.rowcount
    
    conn.close()
    return result

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    # 插入示例数据
    insert_sample_data()
    
    # 验证数据
    employees = execute_query('SELECT * FROM employee')
    print(f"\n当前员工数据：")
    for emp in employees:
        print(f"- {emp['name']} ({emp['employee_id']}) - {emp['department']} - {emp['status']}")