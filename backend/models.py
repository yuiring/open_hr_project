#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Employee:
    """员工数据模型"""
    id: Optional[int] = None
    name: str = ""
    employee_id: str = ""
    department: str = ""
    hr_account: str = ""
    status: str = "在职"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'employee_id': self.employee_id,
            'department': self.department,
            'hr_account': self.hr_account,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            employee_id=data.get('employee_id', ''),
            department=data.get('department', ''),
            hr_account=data.get('hr_account', ''),
            status=data.get('status', '在职'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
    
    def validate(self):
        """验证数据有效性"""
        errors = []
        
        if not self.name.strip():
            errors.append("姓名不能为空")
        
        if not self.employee_id.strip():
            errors.append("工号不能为空")
        
        if not self.department.strip():
            errors.append("部门不能为空")
        
        if self.status not in ['在职', '离职']:
            errors.append("状态必须是'在职'或'离职'")
        
        return errors

@dataclass
class EmployeeQuery:
    """员工查询参数"""
    name: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    
    def to_sql_where(self):
        """转换为SQL WHERE条件"""
        conditions = []
        params = []
        
        if self.name:
            conditions.append("name LIKE ?")
            params.append(f"%{self.name}%")
        
        if self.employee_id:
            conditions.append("employee_id = ?")
            params.append(self.employee_id)
        
        if self.department:
            conditions.append("department = ?")
            params.append(self.department)
        
        if self.status:
            conditions.append("status = ?")
            params.append(self.status)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        return where_clause, params

@dataclass
class APIResponse:
    """API响应模型"""
    success: bool
    message: str
    data: Optional[dict] = None
    
    def to_dict(self):
        """转换为字典"""
        result = {
            'success': self.success,
            'message': self.message
        }
        if self.data is not None:
            result['data'] = self.data
        return result