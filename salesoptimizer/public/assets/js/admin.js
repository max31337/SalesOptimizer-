import { apiConfig } from './config.js';
import { initializeAllCharts } from './analytics.js';


let currentPage = 1;  
const itemsPerPage = 10;

// Add this check before any admin.js operations
function verifyLocalStorage() {
    if (!localStorage.getItem('token') || 
        !localStorage.getItem('userRole') || 
        !localStorage.getItem('userName')) {
        window.location.href = '/auth/login.html';
    }
}

$(document).ready(function() {
    checkAdminAccess();
    verifyLocalStorage();
    setupEventListeners();
    setupNavigationHandlers();
    setupFilterHandlers();
    loadUsers(); 
    $('.admin-section').removeClass('active').hide();
    $('#overview').addClass('active').show();
});


function checkAdminAccess() {
    const token = localStorage.getItem('token');
    const userRole = localStorage.getItem('userRole');

    if (!token || userRole !== 'admin') {
        window.location.href = '/auth/login.html';
        return;
    }

    $.ajax({
        url: `${apiConfig.apiUrl}/auth/me`,  // Fixed template literal
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

    let url = `${apiConfig.apiUrl}/admin/users/list/?skip=${skip}&limit=${limit}`;
    
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
        url: `${apiConfig.apiUrl}/admin/verify-user/${userId}`,
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
        url: `${apiConfig.apiUrl}/audit-logs?${params.toString()}`,
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

// Remove the duplicate setupEventListeners function and merge its content into the existing one
function setupEventListeners() {
    // Debounced search input handler
    $('#userSearch').on('input', debounce(() => loadUsers(1), 500));

    // Filter change handlers
    $('#roleFilter, #statusFilter').on('change', () => loadUsers(1));

    // Pagination button handlers
    $('#prevPage').on('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadUsers(currentPage);
        }
    });
    $('#nextPage').on('click', () => {
        currentPage++;
        loadUsers(currentPage);
    });

    // Edit User Form Submission
    $('#editUserForm').on('submit', function(e) {
        e.preventDefault();
        const userId = $('#editUserId').val();
        const userData = {
            name: $('#editName').val(),
            email: $('#editEmail').val(),
            role: $('#editRole').val(),
            is_active: $('#editStatus').val() === 'true'
        };

        const token = localStorage.getItem('token');
        
        $.ajax({
            url: `${apiConfig.apiUrl}/admin/users/update/${userId}`,
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            data: JSON.stringify(userData),
            success: function(response) {
                closeEditModal();
                $('#updateSuccessModal').css('display', 'flex').hide().fadeIn();
                lucide.createIcons();
                loadUsers(); // Refresh the user list
            },
            error: function(xhr) {
                showNotification(xhr.responseJSON?.detail || 'Failed to update user', 'error');
            }
        });
    });

    // Invite User Form Submission
    $('#inviteUserForm').on('submit', function(e) {
        e.preventDefault();
        const email = $('#inviteEmail').val();
        const name = $('#inviteName').val();
        const role = $('#inviteRole').val();
        const token = localStorage.getItem('token');
        const submitButton = $(this).find('button[type="submit"]');
    
        submitButton.prop('disabled', true).html('Sending...');
    
        $.ajax({
            url: `${apiConfig.apiUrl}/admin/users/invite/`,
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({ email, name, role }),
            success: function(response) {
                $('#inviteUserForm').closest('.modal-overlay').hide();
                showNotification('Invite sent successfully! ✅', 'success');
                $('#inviteUserForm')[0].reset();
                loadUsers();
            },
            error: function(xhr) {
                showNotification(xhr.responseJSON?.detail || 'Failed to send invitation', 'error');
            },
            complete: function() {
                submitButton.prop('disabled', false).html('Send Invitation');
            }
        });
    });

    // Registration Time Range Change Handler
    $('#registrationTimeRange').on('change', function() {
        const days = $(this).val();
        loadRegistrationTrends(days);
    });

    // Settings Form Submission
    $('#adminSettingsForm').on('submit', function(e) {
        e.preventDefault();
        updateAdminSettings();
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
        url: '${apiConfig.apiUrl}/admin/settings',
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
        url: '${apiConfig.apiUrl}/admin/setup-2fa',
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

// Keep only one version of each function and remove duplicates
function showNotification(message, type = 'success') {
    const notification = $('<div>')
        .addClass(`notification ${type}`)
        .text(message)
        .appendTo('body');
    
    setTimeout(() => notification.remove(), 3000);
}

function setupNavigationHandlers() {
    const navLinks = document.querySelectorAll('.nav-links a');
    
    // Initialize charts if overview is active on page load
    if (document.getElementById('overview').classList.contains('active')) {
        initializeAllCharts();
    }
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            
            // Hide all sections
            document.querySelectorAll('.admin-section').forEach(section => {
                section.style.display = 'none';
                section.classList.remove('active');
            });
            
            // Show target section
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.style.display = 'block';
                targetSection.classList.add('active');
                
                // Initialize charts when overview section is shown
                if (targetId === 'overview') {
                    initializeAllCharts();
                }
            }
            
            // Update active state in navigation
            navLinks.forEach(link => link.parentElement.classList.remove('active'));
            this.parentElement.classList.add('active');
        });
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
        url: `${apiConfig.apiUrl}/admin/users/${userId}`,  
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

function logout() {
        // Clear local storage
        localStorage.removeItem('token');
        localStorage.removeItem('userRole');
        localStorage.removeItem('userName');

        // Redirect to login page
        window.location.href = '/auth/login.html';
    }

// Explicitly attach logout to the window object
window.logout = logout;

// Make sure to call this after any dynamic content is added
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
});


// Expose necessary functions to window object
window.editUser = editUser;
window.closeEditModal = closeEditModal;
window.deleteUser = deleteUser;
window.verifyUser = verifyUser;

function editUser(userId) {
    const token = localStorage.getItem('token');
    
    $.ajax({
        url: `${apiConfig.apiUrl}/admin/users/details/${userId}`,
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        method: 'GET',
        success: function(user) {
            if (user) {
                // Populate the edit form
                $('#editUserId').val(user.id);
                $('#editName').val(user.name);
                $('#editEmail').val(user.email);
                $('#editRole').val(user.role);
                $('#editStatus').val(user.is_active.toString());
                
                // Show the modal using jQuery
                $('#editUserModal').css('display', 'flex').hide().fadeIn();
                
                // Refresh Lucide icons
                lucide.createIcons();
            } else {
                showNotification('User not found', 'error');
            }
        },
        error: function(xhr) {
            console.error('Error:', xhr);
            showNotification(xhr.responseJSON?.detail || 'Failed to fetch user details', 'error');
        }
    });
}

function closeEditModal() {
    $('#editUserModal').fadeOut();
    $('#editUserForm')[0].reset();
}

// Add this new function
function closeSuccessModal() {
    $('#updateSuccessModal').fadeOut();
}

// Add to window object
window.closeSuccessModal = closeSuccessModal;

// Add invite modal handlers
$('#inviteUserBtn').on('click', function() {
    $('#inviteUserModal').css('display', 'flex').hide().fadeIn();
});

// Close modal when clicking outside
$('#inviteUserModal').on('click', function(e) {
    if (e.target === this) {
        closeInviteModal();
    }
});

function closeInviteModal() {
    $('#inviteUserModal').fadeOut();
    $('#inviteUserForm')[0].reset();
}

// Add to window object for HTML onclick access
window.closeInviteModal = closeInviteModal;