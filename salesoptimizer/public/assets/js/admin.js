let currentPage = 1;  
const itemsPerPage = 10;
let selectedUserId = null;

$(document).ready(function() {
    checkAdminAccess();
    loadUsers();
    loadAuditLogs();
    setupEventListeners();
    setupNavigationHandlers();
    setupFilterHandlers();
     
    $('.admin-section').removeClass('active').hide();
    $('.modal').hide();
    $('#overview').addClass('active').show();
    
    // Set correct navigation highlight
    $('.nav-links li').removeClass('active');
    $('.nav-links li:first-child').addClass('active');


    $('#userSearch').on('input', debounce(() => loadUsers(1), 300));
    $('#roleFilter, #statusFilter').on('change', () => loadUsers(1));

    $('#users').addClass('active').show();
    $('.nav-links li:first-child').addClass('active');
    $('.admin-section:not(#users)').removeClass('active').hide();

    // Hide all modals on initial load
    $('.modal').hide();

    // Improved modal handling
    $('.modal').click(function(event) {
        if ($(event.target).is('.modal')) {
            $(this).hide();
        }
    });

    // Prevent modal from closing when clicking inside modal content
    $('.modal-content').click(function(event) {
        event.stopPropagation();
    });

    // Close modal when clicking cancel button
    $('.btn-secondary[onclick*="hide"]').click(function() {
        $(this).closest('.modal').hide();
    });

    // Form submission handlers with proper modal handling
    $('#inviteForm').on('submit', function(e) {
        e.preventDefault();
        inviteUser();
    });

    $('#editForm').on('submit', function(e) {
        e.preventDefault();
        updateUser();
    });

    // Ensure modals are properly hidden after form submission
    $('#editUserModal .btn-secondary').click(function() {
        $('#editUserModal').hide();
        // Clear any form data or messages
        $('#editForm')[0].reset();
        $('#editMessage').empty();
    });

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

function checkAdminAccess() {
    const token = localStorage.getItem('token');
    const userRole = localStorage.getItem('userRole');

    if (!token || userRole !== 'admin') {
        window.location.href = '/auth/login.html';
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

    let url = `http://localhost:8000/api/admin/users/list/?skip=${skip}&limit=${limit}`;
    
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

function displayUsers(users) {
    const userTableBody = $('#userTableBody');
    userTableBody.empty();

    users.forEach(user => {
        const row = $('<tr>');
        row.append(`<td>${user.name}</td>`);
        row.append(`<td>${user.email}</td>`);
        row.append(`<td>${user.role}</td>`);
        row.append(`<td><span class="status-badge ${user.is_active ? 'active' : 'inactive'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>`);
        row.append(`<td><span class="verification-badge ${user.is_verified ? 'verified' : 'unverified'}">${user.is_verified ? 'Verified' : 'Unverified'}</span></td>`);
        row.append(`
<td>
                <button class="btn-edit" onclick="editUser(${user.id})">
                    <i data-lucide="edit"></i>
                    Edit
                </button>
                <button class="btn-delete" onclick="deleteUser(${user.id})">
                    <i data-lucide="trash-2"></i>
                    Delete
                </button>
                ${!user.is_verified ? `<button class="btn-verify" onclick="verifyUser(${user.id})">Verify</button>` : ''}
            </td>
        `);
        userTableBody.append(row);
    });

    lucide.createIcons();

}

// Add this new function to handle manual verification
function verifyUser(userId) {
    if (!confirm('Are you sure you want to verify this user?')) return;

    $.ajax({
        url: `http://localhost:8000/api/admin/verify-user/${userId}`,
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        success: function(response) {
            showNotification('User verified successfully', 'success');
            loadUsers(); // Refresh the user list
        },
        error: function(xhr) {
            showNotification(xhr.responseJSON?.detail || 'Failed to verify user', 'error');
        }
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
        // Update the URL to match the backend route
        url: `http://localhost:8000/api/audit-logs?${params.toString()}`,
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(response) {
            displayAuditLogs(response);
            updatePagination(response.total);
        },
        error: function(xhr) {
            showNotification('Failed to load audit logs', 'error');
            console.error('Error loading audit logs:', xhr.responseJSON?.detail);
        }
    });
}

function formatAuditDetails(action, details) {
    // Format based on action type
    switch(action) {
        case 'UPDATE_USER':
            return formatUserUpdate(details);
        case 'DELETE_USER':
            return `User account deleted`;
        case 'VERIFY_USER':
            return `User email verified`;
        case 'INVITE_USER':
            return `New user invited to platform`;
        case 'PASSWORD_RESET':
            return `Password reset requested`;
        default:
            return details;
    }
}

function formatUserUpdate(details) {
    try {
        const changes = [];
        if (details.includes('role')) {
            const roleMatch = details.match(/role to (\w+(-\w+)*)/);
            if (roleMatch) {
                const role = roleMatch[1]
                    .split('-')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
                changes.push(`Role changed to ${role}`);
            }
        }
        if (details.includes('status')) {
            const status = details.includes('activated') ? 'Activated' : 'Deactivated';
            changes.push(`Account ${status.toLowerCase()}`);
        }
        if (details.includes('verified')) {
            changes.push('Email verified');
        }
        return changes.length > 0 ? changes.join(' • ') : details;
    } catch (e) {
        console.error('Error formatting details:', e);
        return details;
    }
}

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
            minute: '2-digit',
            second: '2-digit'
        });

        const formattedAction = log.action
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');

        const formattedDetails = formatAuditDetails(log.action, log.details);

        tbody.append(`
            <tr>
                <td>${formattedDate}</td>
                <td><strong>${log.user_name}</strong><br><small>${log.user_email}</small></td>
                <td><span class="action-badge ${log.action.toLowerCase()}">${formattedAction}</span></td>
                <td>${formattedDetails}</td>
                <td><strong>${log.performer_name}</strong><br><small>${log.performer_email}</small></td>
            </tr>
        `);
    });
}

function setupEventListeners() {
    $('.nav-links a').click(function(e) {
        e.preventDefault();
        const targetId = $(this).attr('href').substring(1);

        if (targetId !== 'overview' && window.destroyAllCharts) {
            destroyAllCharts();
        }
        $('.admin-section').fadeOut(150, function() {
            $('.admin-section').hide();
            $(`#${targetId}`).fadeIn(150);
            
            // Initialize charts after fade in if overview
            if (targetId === 'overview') {
                setTimeout(loadAllAnalytics, 200);
            }
        });
        
        $('.nav-links li').removeClass('active');
        $(this).parent().addClass('active');
    });

        if (targetId === 'audit') {
            loadAuditLogs();
        } else if (targetId === 'users') {
            loadUsers();
        } else if (targetId === 'settings') {
            loadAdminSettings();
        }
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
    // Clear any previous form data and messages
    $('#inviteForm')[0].reset();
    $('.success-message').remove();
    $('#inviteModal').show();
}

// Update the inviteUser function
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

// Keep only one version of each function and remove duplicates
function showNotification(message, type = 'success') {
    const notification = $('<div>')
        .addClass(`notification ${type}`)
        .text(message)
        .appendTo('body');
    
    setTimeout(() => notification.remove(), 3000);
}

function setupNavigationHandlers() {
    $('.nav-links a').click(function(e) {
        e.preventDefault();
        const targetId = $(this).attr('href').substring(1);
        
        // Hide all sections
        $('.admin-section').removeClass('active').hide();
        
        // Show target section
        $(`#${targetId}`).addClass('active').show();
        
        // Update active nav link
        $('.nav-links li').removeClass('active');
        $(this).parent().addClass('active');
        
        // Refresh section data
        if (targetId === 'overview') {
            loadAllAnalytics();
        } else if (targetId === 'users') {
            loadUsers();
        } else if (targetId === 'audit') {
            loadAuditLogs();
        }
    });
}

// Single setupFilterHandlers
function setupFilterHandlers() {
    $('#registrationTimeRange').on('change', function(e) {
        loadRegistrationTrends(parseInt($(this).val()));
    });
}

function deleteUser(userId) {
    if (!confirm('Are you sure you want to deactivate this user?')) return;

    const token = localStorage.getItem('token');
    $.ajax({
        url: `http://localhost:8000/api/admin/users/${userId}`,  
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'DELETE',
        success: function() {
            loadUsers();
            loadAllAnalytics(); // Refresh analytics after user deletion
            showNotification('User deactivated successfully');
        },
        error: function(xhr) {
            showNotification(xhr.responseJSON?.detail || 'Failed to deactivate user', 'error');
        }
    });
}


function editUser(userId) {
    currentEditingUserId = userId;
    const token = localStorage.getItem('token');
          
    $.ajax({
        url: `http://localhost:8000/api/admin/users/${userId}`,
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(user) {
            $('#editRole').val(user.role);
            $('#editActive').prop('checked', user.is_active);
            $('#editMessage').empty();
            $('#editUserModal').show();
        },
        error: function(xhr) {
            showNotification(xhr.responseJSON?.detail || 'Failed to load user data', 'error');
        }
    });
}




    function logout() {
        // Clear local storage
        localStorage.removeItem('token');
        localStorage.removeItem('userRole');
        localStorage.removeItem('userName');
        
        // Redirect to login page
        window.location.href = '/auth/login.html';
    }