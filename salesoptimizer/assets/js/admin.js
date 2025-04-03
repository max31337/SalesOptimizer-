let currentPage = 1;  
const itemsPerPage = 10;
let selectedUserId = null;

$(document).ready(function() {
    checkAdminAccess();
    loadUsers();
    loadAuditLogs();
    setupEventListeners();
});

function checkAdminAccess() {
    const token = localStorage.getItem('token');
    const userRole = localStorage.getItem('userRole');

    if (!token || userRole !== 'admin') {
        window.location.href = '../auth/login.html';
        return;
    }

    $.ajax({
        url: 'http://localhost:8000/api/auth/me',
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(response) {
            if (response.role !== 'admin' || !response.is_active) {
                localStorage.clear();
                window.location.href = '../auth/login.html';
                return;
            }
            $('#adminName').text(response.name);
        },
        error: function(xhr) {
            if (xhr.status === 401 || xhr.status === 403) {
                localStorage.clear();
                window.location.href = '../auth/login.html';
            } else {
                console.error('Error checking admin access:', xhr.responseJSON?.detail);
            }
        }
    });
}

function loadUsers() {
    const token = localStorage.getItem('token');
    const search = $('#searchUser').val();
    const role = $('#roleFilter').val();
    const status = $('#statusFilter').val();

    const params = new URLSearchParams({
        skip: (currentPage-1)*itemsPerPage,
        limit: itemsPerPage
    });

    if (search) params.append('search', search);
    if (role) params.append('role', role);
    if (status !== '') {
        params.append('is_active', status === 'true');
    }

    $.ajax({
        url: `http://localhost:8000/api/admin/users/?${params.toString()}`,
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(response) {
            if (response && response.users) {
                displayUsers(response.users);
                updatePagination(response.total);
            } else {
                displayUsers([]);
                showNotification('No users found', 'info');
            }
        },
        error: function(xhr) {
            console.error('Error loading users:', xhr);
            showNotification(xhr.responseJSON?.detail || 'Failed to load users', 'error');
        }
    });
}

function updatePagination(total) {
    const totalPages = Math.ceil(total / itemsPerPage);
    $('#pageInfo').text(`Page ${currentPage} of ${totalPages}`);
    $('#prevPage').prop('disabled', currentPage <= 1);
    $('#nextPage').prop('disabled', currentPage >= totalPages);
}

$(document).ready(function() {    
    $('#prevPage').click(() => {
        if (currentPage > 1) {
            currentPage--;
            loadUsers();
        }
    });

    $('#nextPage').click(() => {
        currentPage++;
        loadUsers();
    });
    loadUsers();
});

function displayUsers(users) {
    const tbody = $('#usersTable tbody');
    tbody.empty();

    if (!users || users.length === 0) {
        tbody.append(`
            <tr>
                <td colspan="5" class="text-center">No users found</td>
            </tr>
        `);
        return;
    }

    users.forEach(user => {
        tbody.append(`
            <tr>
                <td>${user.name || 'N/A'}</td>
                <td>${user.email}</td>
                <td>${user.role}</td>
                <td>${user.is_active ? 'Active' : 'Inactive'}</td>
                <td>
                    <button onclick="editUser(${user.id})" class="btn-primary">Edit</button>
                    <button onclick="deleteUser(${user.id})" class="btn-danger">Delete</button>
                </td>
            </tr>
        `);
    });
}

function loadAuditLogs() {
    const token = localStorage.getItem('token');
    const fromDate = $('#auditDateFrom').val();
    const toDate = $('#auditDateTo').val();
    const action = $('#auditActionFilter').val();

    const params = new URLSearchParams({
        skip: (currentPage - 1) * itemsPerPage,
        limit: itemsPerPage
    });

    if (fromDate) params.append('from_date', fromDate);
    if (toDate) params.append('to_date', toDate);
    if (action) params.append('action', action);

    $.ajax({
        url: `http://localhost:8000/api/audit-logs?${params.toString()}`,
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(response) {
            displayAuditLogs(response.logs);
            updatePagination(response.total);
        },
        error: function(xhr) {
            showNotification('Failed to load audit logs', 'error');
        }
    });
}

function updatePagination(total) {
    const totalPages = Math.ceil(total / itemsPerPage);
    $('#pageInfo').text(`Page ${currentPage} of ${totalPages}`);
    $('#prevPage').prop('disabled', currentPage <= 1);
    $('#nextPage').prop('disabled', currentPage >= totalPages);
}

$(document).ready(function() {    
    $('#prevPage').click(() => {
        if (currentPage > 1) {
            currentPage--;
            loadAuditLogs();
        }
    });

    $('#nextPage').click(() => {
        currentPage++;
        loadAuditLogs();
    });
    loadAuditLogs();
});

function displayAuditLogs(logs) {
    const tbody = $('#auditTable tbody');
    tbody.empty();

    if (!logs || logs.length === 0) {
        tbody.append(`
            <tr>
                <td colspan="5" class="text-center">No audit logs found</td>
            </tr>
        `);
        return;
    }

    logs.forEach(log => {
        tbody.append(`
            <tr>
                <td>${new Date(log.timestamp).toLocaleString()}</td>
                <td>${log.user_id}</td>
                <td>${log.action}</td>
                <td>${log.details}</td>
                <td>${log.performed_by}</td>
            </tr>
        `);
    });
}

function setupEventListeners() {
    $('.nav-links a').click(function(e) {
        e.preventDefault();
        const target = $(this).attr('href').substring(1);
        $('.admin-section').addClass('hidden');
        $(`#${target}`).removeClass('hidden');
        $('.nav-links li').removeClass('active');
        $(this).parent().addClass('active');
    });
    $('.modal').click(function(e) {
        if (e.target === this) {
            $(this).hide();
        }
    });
    $('#adminSettingsForm').submit(function(e) {
        e.preventDefault();
        updateAdminSettings();
    });
    let filterTimeout;
    $('#searchUser').on('input', function() {
        clearTimeout(filterTimeout);
        filterTimeout = setTimeout(() => {
            currentPage = 1;
            loadUsers();
        }, 300);
    });

    $('#roleFilter, #statusFilter').on('change', function() {
        currentPage = 1;
        loadUsers();
    });
    $('#prevPage').click(function() {
        if (currentPage > 1) {
            currentPage--;
            loadUsers();
        }
    });

    $('#nextPage').click(function() {
        currentPage++;
        loadUsers();
    });
}

function updateAdminSettings() {
    const token = localStorage.getItem('token');
    const data = {
        email_notifications: $('#emailNotifications').is(':checked'),
        two_factor_auth: $('#twoFactorAuth').is(':checked'),
        theme: $('#themeSelect').val()
    };

    $.ajax({
        url: 'http://localhost:8000/api/admin/settings',
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            showNotification('Settings updated successfully');
        },
        error: function(xhr) {
            showNotification('Failed to update settings', 'error');
        }
    });
}

// Pagination
    $('#prevPage').click(() => {
        if (currentPage > 1) {
            currentPage--;
            loadUsers();
        }
    });

    $('#nextPage').click(() => {
        currentPage++;
        loadUsers();
    });

    // Forms
    $('#inviteForm').submit(function(e) {
        e.preventDefault();
        inviteUser();
    });

    $('#editForm').submit(function(e) {
        e.preventDefault();
        updateUser();
    });

function showInviteModal() {
    $('#inviteModal').show();
}

function inviteUser() {
    const token = localStorage.getItem('token');
    const data = {
        email: $('#inviteEmail').val(),
        name: $('#inviteName').val(),
        role: $('#inviteRole').val()
    };

    $.ajax({
        url: 'http://localhost:8000/api/admin/invite/',
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            $('#inviteModal').hide();
            $('#inviteForm')[0].reset();
            loadUsers();
            showNotification('User invited successfully');
            $('#inviteModal .modal-content .success-message').remove();
            $('<p class="success-message">Invitation sent successfully!</p>')
                .css({
                    'color': '#28a745',
                    'font-weight': 'bold',
                    'margin-top': '10px'
                })
                .appendTo('#inviteModal .modal-content');
        },
        error: function(xhr) {
            showNotification(xhr.responseJSON?.detail || 'Failed to invite user', 'error');
        }
    });
}

function showNotification(message, type = 'success') {
    const notification = $('<div>')
        .addClass(`notification ${type}`)
        .text(message)
        .appendTo('body');
    
    setTimeout(() => notification.remove(), 3000);
}

function editUser(userId) {
    selectedUserId = userId;
    const token = localStorage.getItem('token');
    
    // Get current user data
    $.ajax({
        url: `http://localhost:8000/api/admin/users/${userId}`,
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(user) {
            $('#editRole').val(user.role);
            $('#editStatus').prop('checked', user.is_active);
            $('#editModal').show();
        },
        error: function(xhr) {
            showNotification(xhr.responseJSON?.detail || 'Failed to load user data', 'error');
        }
    });
}

function updateUser() {
    const token = localStorage.getItem('token');
    const data = {
        role: $('#editRole').val(),
        is_active: $('#editStatus').is(':checked')
    };

    $.ajax({
        url: `http://localhost:8000/api/admin/users/${selectedUserId}`,
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function() {
            $('#editModal').hide();
            loadUsers();
            showNotification('User updated successfully');
        },
        error: function(xhr) {
            showNotification(xhr.responseJSON?.detail || 'Failed to update user', 'error');
        }
    });
}

function deleteUser(userId) {
    if (!confirm('Are you sure you want to deactivate this user?')) return;

    const token = localStorage.getItem('token');
    $.ajax({
        url: `http://localhost:8000/api/admin/users/${userId}`,  // Updated endpoint
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'DELETE',
        success: function() {
            loadUsers();
            showNotification('User deactivated successfully');
        },
        error: function(xhr) {
            showNotification(xhr.responseJSON?.detail || 'Failed to deactivate user', 'error');
        }
    });
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userName');
    window.location.href = '../auth/login.html'
}