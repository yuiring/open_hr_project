// 全局变量
const API_BASE_URL = 'http://localhost:9000/api';
let currentEmployees = [];
let currentEditingEmployee = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadEmployees();
    loadDepartments();
    loadStatistics();
});

// 标签切换功能
function showTab(tabName) {
    // 隐藏所有标签内容
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));
    
    // 移除所有标签按钮的激活状态
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => btn.classList.remove('active'));
    
    // 显示选中的标签内容
    document.getElementById(tabName).classList.add('active');
    
    // 激活对应的标签按钮
    event.target.classList.add('active');
    
    // 根据标签加载相应数据
    if (tabName === 'employee-list') {
        loadEmployees();
    } else if (tabName === 'statistics') {
        loadStatistics();
    }
}

// 显示加载动画
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

// 隐藏加载动画
function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// 显示消息提示
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    // 插入到容器顶部
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 3000);
}

// API请求封装
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || '请求失败');
        }
        
        return data;
    } catch (error) {
        console.error('API请求错误:', error);
        throw error;
    }
}

// AI对话功能
function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 添加用户消息到聊天界面
    addMessageToChat(message, 'user');
    input.value = '';
    
    // 显示AI正在思考
    const thinkingMsg = addMessageToChat('正在处理您的请求...', 'assistant');
    
    try {
        // 解析用户意图并调用相应的API
        const response = await processUserMessage(message);
        
        // 移除思考消息
        thinkingMsg.remove();
        
        // 添加AI回复
        addMessageToChat(response, 'assistant');
        
    } catch (error) {
        // 移除思考消息
        thinkingMsg.remove();
        
        // 显示错误消息
        addMessageToChat(`抱歉，处理您的请求时出现错误: ${error.message}`, 'assistant');
    }
}

function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (sender === 'user') {
        contentDiv.innerHTML = `<strong>您：</strong>${message}`;
    } else {
        contentDiv.innerHTML = `<strong>AI助手：</strong>${message}`;
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv;
}

// 处理用户消息 - 调用后端AI接口
async function processUserMessage(message) {
    try {
        const response = await apiRequest('/ai/chat', {
            method: 'POST',
            body: JSON.stringify({ message: message })
        });
        
        if (response.success) {
            return response.data.response;
        } else {
            return `处理请求时出现错误：${response.message}`;
        }
    } catch (error) {
        return `AI服务暂时不可用：${error.message}`;
    }
}

// 员工列表功能
async function loadEmployees() {
    try {
        showLoading();
        const response = await apiRequest('/employees');
        
        if (response.success) {
            currentEmployees = response.data.employees;
            displayEmployees(currentEmployees);
        } else {
            showMessage(response.message, 'error');
        }
    } catch (error) {
        showMessage(`加载员工列表失败: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

function displayEmployees(employees) {
    const tbody = document.getElementById('employeeTableBody');
    tbody.innerHTML = '';
    
    if (employees.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #6c757d;">暂无员工数据</td></tr>';
        return;
    }
    
    employees.forEach(employee => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${employee.name}</td>
            <td>${employee.employee_id}</td>
            <td>${employee.department}</td>
            <td>${employee.hr_account}</td>
            <td><span class="status-badge ${employee.status === '在职' ? 'status-active' : 'status-inactive'}">${employee.status}</span></td>
            <td>
                <button class="action-btn edit-btn" onclick="openEditModal(${employee.id})">编辑</button>
                <button class="action-btn delete-btn" onclick="deleteEmployee(${employee.id}, '${employee.name}')">删除</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function searchEmployees() {
    const name = document.getElementById('searchName').value.toLowerCase();
    const department = document.getElementById('filterDepartment').value;
    const status = document.getElementById('filterStatus').value;
    
    let filteredEmployees = currentEmployees.filter(employee => {
        const matchName = !name || employee.name.toLowerCase().includes(name);
        const matchDepartment = !department || employee.department === department;
        const matchStatus = !status || employee.status === status;
        
        return matchName && matchDepartment && matchStatus;
    });
    
    displayEmployees(filteredEmployees);
}

// 加载部门列表
async function loadDepartments() {
    try {
        const response = await apiRequest('/departments');
        
        if (response.success) {
            const departments = response.data.departments;
            const filterSelect = document.getElementById('filterDepartment');
            
            // 清空现有选项（保留"所有部门"）
            filterSelect.innerHTML = '<option value="">所有部门</option>';
            
            // 添加部门选项
            departments.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept;
                option.textContent = dept;
                filterSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载部门列表失败:', error);
    }
}

// 新增员工功能
async function addEmployee(event) {
    event.preventDefault();
    
    const name = document.getElementById('employeeName').value.trim();
    const department = document.getElementById('employeeDepartment').value;
    const employeeId = document.getElementById('employeeId').value.trim();
    const hrAccount = document.getElementById('hrAccount').value.trim();
    
    if (!name || !department) {
        showMessage('请填写必填字段', 'error');
        return;
    }
    
    try {
        showLoading();
        
        const employeeData = { name, department };
        if (employeeId) employeeData.employee_id = employeeId;
        if (hrAccount) employeeData.hr_account = hrAccount;
        
        const response = await apiRequest('/employees', {
            method: 'POST',
            body: JSON.stringify(employeeData)
        });
        
        if (response.success) {
            showMessage(response.message, 'success');
            document.getElementById('addEmployeeForm').reset();
            loadEmployees(); // 刷新员工列表
        } else {
            showMessage(response.message, 'error');
        }
    } catch (error) {
        showMessage(`创建员工失败: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// 编辑员工功能
function openEditModal(employeeId) {
    const employee = currentEmployees.find(emp => emp.id === employeeId);
    if (!employee) {
        showMessage('员工信息不存在', 'error');
        return;
    }
    
    currentEditingEmployee = employee;
    
    // 填充表单
    document.getElementById('editEmployeeId').value = employee.id;
    document.getElementById('editName').value = employee.name;
    document.getElementById('editDepartment').value = employee.department;
    document.getElementById('editHrAccount').value = employee.hr_account;
    document.getElementById('editStatus').value = employee.status;
    
    // 显示模态框
    document.getElementById('editModal').style.display = 'block';
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
    currentEditingEmployee = null;
}

async function updateEmployee(event) {
    event.preventDefault();
    
    if (!currentEditingEmployee) {
        showMessage('没有选择要编辑的员工', 'error');
        return;
    }
    
    const department = document.getElementById('editDepartment').value;
    const hrAccount = document.getElementById('editHrAccount').value.trim();
    const status = document.getElementById('editStatus').value;
    
    try {
        showLoading();
        
        const updateData = { department, hr_account: hrAccount, status };
        
        const response = await apiRequest(`/employees/${currentEditingEmployee.id}`, {
            method: 'PUT',
            body: JSON.stringify(updateData)
        });
        
        if (response.success) {
            showMessage(response.message, 'success');
            closeEditModal();
            loadEmployees(); // 刷新员工列表
        } else {
            showMessage(response.message, 'error');
        }
    } catch (error) {
        showMessage(`更新员工信息失败: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// 删除员工功能
async function deleteEmployee(employeeId, employeeName) {
    if (!confirm(`确定要将员工 ${employeeName} 设置为离职状态吗？`)) {
        return;
    }
    
    try {
        showLoading();
        
        const response = await apiRequest(`/employees/${employeeId}`, {
            method: 'DELETE'
        });
        
        if (response.success) {
            showMessage(response.message, 'success');
            loadEmployees(); // 刷新员工列表
        } else {
            showMessage(response.message, 'error');
        }
    } catch (error) {
        showMessage(`删除员工失败: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// 统计信息功能
async function loadStatistics() {
    try {
        const response = await apiRequest('/stats');
        
        if (response.success) {
            const stats = response.data.stats;
            
            // 更新统计卡片
            document.getElementById('totalEmployees').textContent = stats.total_employees;
            document.getElementById('activeEmployees').textContent = stats.active_employees;
            document.getElementById('inactiveEmployees').textContent = stats.inactive_employees;
            
            // 更新部门统计图表
            displayDepartmentChart(stats.department_stats);
        } else {
            showMessage(response.message, 'error');
        }
    } catch (error) {
        showMessage(`加载统计信息失败: ${error.message}`, 'error');
    }
}

function displayDepartmentChart(departmentStats) {
    const chartContainer = document.getElementById('departmentChart');
    chartContainer.innerHTML = '';
    
    if (departmentStats.length === 0) {
        chartContainer.innerHTML = '<p style="text-align: center; color: #6c757d;">暂无部门统计数据</p>';
        return;
    }
    
    const maxCount = Math.max(...departmentStats.map(dept => dept.count));
    
    departmentStats.forEach(dept => {
        const barDiv = document.createElement('div');
        barDiv.className = 'dept-bar';
        
        const percentage = (dept.count / maxCount) * 100;
        
        barDiv.innerHTML = `
            <div class="dept-name">${dept.department}</div>
            <div class="dept-bar-fill">
                <div class="dept-bar-progress" style="width: ${percentage}%"></div>
            </div>
            <div class="dept-count">${dept.count}人</div>
        `;
        
        chartContainer.appendChild(barDiv);
    });
}

// 点击模态框外部关闭
window.onclick = function(event) {
    const modal = document.getElementById('editModal');
    if (event.target === modal) {
        closeEditModal();
    }
}