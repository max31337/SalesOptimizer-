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
                <button class="btn-edit" onclick="editUser(${user.id})">Edit</button>
                <button class="btn-delete" onclick="deleteUser(${user.id})">Delete</button>
                ${!user.is_verified ? `<button class="btn-verify" onclick="verifyUser(${user.id})">Verify</button>` : ''}
            </td>
        `);
        userTableBody.append(row);
    });
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

function setupFilterHandlers() {
    $('#registrationTimeRange').on('change', function(e) {
        loadRegistrationTrends(parseInt($(this).val()));
    });
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
        
        // Refresh section data if needed
        if (targetId === 'overview') {
            loadRegistrationTrends();
        } else if (targetId === 'users') {
            loadUsers();
        } else if (targetId === 'audit') {
            loadAuditLogs();
        }
    });
}

    // Initialize event handlers when document is ready
    $(document).ready(function() {
        // Initial setup
        checkAdminAccess();
        
        // Hide all sections first
        $('.admin-section').removeClass('active').hide();
        
        // Show overview section by default
        $('#overview').addClass('active').show();
        
        // Set correct navigation highlight
        $('.nav-links li').removeClass('active');
        $('.nav-links li:first-child').addClass('active');
        
        // Setup event listeners
        setupNavigationHandlers();
        setupFilterHandlers();
        
        // Remove the registration trends handler as it's now in analytics.js
        // $('#registrationTimeRange').on('change', function() {...});
    });

    // Remove any registration trends related variables and functions
    // let registrationChart = null;
    // function loadRegistrationTrends() {...}

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

// Remove or comment out the conflicting event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the registration trends chart
    loadRegistrationTrends();
    
    // Add event listener for time range selector
    document.getElementById('registrationTimeRange').addEventListener('change', function(e) {
        loadRegistrationTrends(parseInt(e.target.value));
    });

    // Update chart when theme changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'data-theme') {
                loadRegistrationTrends(parseInt(document.getElementById('registrationTimeRange').value));
            }
        });
    });

    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
    });
});

// Add the navigation handler to show correct section
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').substring(1);
        
        // Hide all sections
        document.querySelectorAll('.admin-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show target section
        document.getElementById(targetId).classList.add('active');
        
        // Update active nav link
        document.querySelectorAll('.nav-links li').forEach(li => {
            li.classList.remove('active');
        });
        this.parentElement.classList.add('active');
    });
});