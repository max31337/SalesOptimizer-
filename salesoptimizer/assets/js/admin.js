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

function loadUsers(page = 1) {
    const token = localStorage.getItem('token');
    const searchTerm = $('#userSearch').val();
    const roleFilter = $('#roleFilter').val();
    const statusFilter = $('#statusFilter').val();
    const limit = 10;
    const skip = (page - 1) * limit;

    let url = `http://localhost:8000/api/admin/users/?skip=${skip}&limit=${limit}`;
    
    if (searchTerm) {
        url += `&search=${encodeURIComponent(searchTerm)}`;
    }
    if (roleFilter && roleFilter !== 'all') {
        url += `&role=${encodeURIComponent(roleFilter)}`;
    }
    if (statusFilter && statusFilter !== 'all') {
        url += `&is_active=${statusFilter === 'active'}`;
    }

    $.ajax({
        url: url,
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(response) {
            displayUsers(response.users);
            updatePagination(response.total, page, limit);
        },
        error: function(xhr) {
            showNotification(xhr.responseJSON?.detail || 'Failed to load users', 'error');
        }
    });
}

// Add event listeners for search and filters
$(document).ready(function() {
    $('#userSearch').on('input', debounce(() => loadUsers(1), 300));
    $('#roleFilter, #statusFilter').on('change', () => loadUsers(1));
});

// Debounce function to prevent too many API calls
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
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
        // Format role display
        const roleDisplay = {
            'admin': 'Admin',
            'analyst': 'Analyst',
            'sales-rep': 'Sales Rep'
        }[user.role] || user.role;

        tbody.append(`
            <tr>
                <td>${user.name || 'N/A'}</td>
                <td>${user.email}</td>
                <td>${roleDisplay}</td>
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
        limit: itemsPerPage,
        include_names: true  
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
        const date = new Date(log.timestamp);
        const formattedDate = date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        let formattedDetails = log.details;
        if (log.details.startsWith('Updated user details:')) {
            try {
                const detailsStr = log.details.replace('Updated user details:', '').trim();
                const details = JSON.parse(detailsStr.replace(/'/g, '"'));
                
                const changes = [];
                if (details.role) {
                    const readableRole = details.role
                        .split('-')
                        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                        .join(' ');
                    changes.push(`role changed to ${readableRole}`);
                }
                if (details.is_active !== undefined) {
                    changes.push(details.is_active ? 'account activated' : 'account deactivated');
                }
                formattedDetails = changes.join(' and ');
            } catch (e) {
                console.error('Error parsing details:', e);
            }
        }

        const formattedAction = log.action.toLowerCase()
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');

        tbody.append(`
            <tr>
                <td>${formattedDate}</td>
                <td>${log.user_name} (${log.user_email})</td>
                <td>${formattedAction}</td>
                <td>${formattedDetails}</td>
                <td>${log.performer_name} (${log.performer_email})</td>
            </tr>
        `);
    });
}

function setupEventListeners() {
    $('.nav-links a').click(function(e) {
        e.preventDefault();
        const targetId = $(this).attr('href').substring(1);
        
        // Hide all sections
        $('.admin-section').removeClass('active').hide();
        $(`#${targetId}`).addClass('active').show();
        $('.nav-links li').removeClass('active');
        $(this).parent().addClass('active');

        if (targetId === 'audit') {
            loadAuditLogs();
        } else if (targetId === 'users') {
            loadUsers();
        } else if (targetId === 'settings') {
            loadAdminSettings();
        }
    });
}

$(document).ready(function() {
    $('#users').addClass('active').show();
    $('.nav-links li:first-child').addClass('active');
    $('.admin-section:not(#users)').removeClass('active').hide();
});

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
            const statusDiv = $('#settingsStatus');
            statusDiv.removeClass('error').addClass('success')
                .html('<p>Settings saved successfully!</p>')
                .show();
            
            setTimeout(() => {
                statusDiv.fadeOut();
            }, 3000);

            applyTheme(data.theme);
            
            if (data.two_factor_auth) {
                setupTwoFactorAuth();
            }
        },
        error: function(xhr) {
            const statusDiv = $('#settingsStatus');
            statusDiv.removeClass('success').addClass('error')
                .html('<p>Failed to save settings. Please try again.</p>')
                .show();
        }
    });
}

function setupTwoFactorAuth() {
    const token = localStorage.getItem('token');
    
    $.ajax({
        url: 'http://localhost:8000/api/admin/setup-2fa',
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'POST',
        success: function(response) {
            showQRCodeModal(response.qr_code);
        },
        error: function(xhr) {
            showNotification('Failed to setup 2FA', 'error');
        }
    });
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('admin-theme', theme);
}

function showInviteModal() {
    $('#inviteModal').show();
}

$(document).ready(function() {
    $('#inviteForm').on('submit', function(e) {
        e.preventDefault();
        inviteUser();
    });

    // Add close button handler for invite modal
    $('.modal').click(function(event) {
        if ($(event.target).is('.modal')) {
            $(this).hide();
        }
    });
});

function inviteUser() {
    const token = localStorage.getItem('token');
    const data = {
        email: $('#inviteEmail').val(),
        name: $('#inviteName').val(),
        role: $('#inviteRole').val()
    };

    $.ajax({
        url: 'http://localhost:8000/api/admin/invite/',
        headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        method: 'POST',
        data: JSON.stringify(data),
        success: function(response) {
            // Remove any existing success message
            $('#inviteModal .modal-content .success-message').remove();
            
            // Add new success message
            $('<p class="success-message">Invitation sent successfully!</p>')
                .css({
                    'color': '#28a745',
                    'font-weight': 'bold',
                    'margin-top': '10px',
                    'text-align': 'center'
                })
                .appendTo('#inviteModal .modal-content');
            
            // Clear the form
            $('#inviteForm')[0].reset();
            
            // Refresh user list
            loadUsers();
            
            // Hide modal after delay
            setTimeout(() => {
                $('#inviteModal').hide();
                $('#inviteModal .modal-content .success-message').remove();
            }, 2000);
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

// Add form submission handler
$('#editForm').on('submit', function(e) {
    e.preventDefault();
    updateUser();
});

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
        success: function(response) {
            $('#editModal').hide();
            loadUsers(currentPage); // Maintain current page
            showNotification('User updated successfully');
        },
        error: function(xhr) {
            showNotification(xhr.responseJSON?.detail || 'Failed to update user', 'error');
        }
    });
}

// Initialize event handlers when document is ready
$(document).ready(function() {
    $('#users').addClass('active').show();
    $('.nav-links li:first-child').addClass('active');
    $('.admin-section:not(#users)').removeClass('active').hide();
});

function deleteUser(userId) {
    if (!confirm('Are you sure you want to deactivate this user?')) return;

    const token = localStorage.getItem('token');
    $.ajax({
        url: `http://localhost:8000/api/admin/users/${userId}`,  
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

document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-links a');
    const sections = document.querySelectorAll('.admin-section');

    sections[0].classList.add('active');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            sections.forEach(section => section.classList.remove('active'));
            
            navLinks.forEach(navLink => navLink.parentElement.classList.remove('active'));
            
            link.parentElement.classList.add('active');
            
            const targetId = link.getAttribute('href').substring(1);
            document.getElementById(targetId).classList.add('active');
        });
    });
});

const themeSelect = document.getElementById('themeSelect');

const savedTheme = localStorage.getItem('admin-theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
themeSelect.value = savedTheme;

themeSelect.addEventListener('change', function() {
    const theme = this.value;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('admin-theme', theme);
});