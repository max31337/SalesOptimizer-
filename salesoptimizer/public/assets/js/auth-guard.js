import { apiConfig } from './config.js';

function verifySession() {
    const token = localStorage.getItem('token');
    const userRole = localStorage.getItem('userRole');
    
    if (!token) {
        handleAuthFailure();
        return;
    }

    $.ajax({
        url: `${apiConfig.apiUrl}/auth/check-session`,
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(response) {
            if (!response.valid || !response.is_active) {
                handleAuthFailure();
                return;
            }
            
            // Enforce role-based access
            if (response.role === 'admin' && currentPath.includes('/admin/')) {
                window.location.href = '/admin/dashboard.html';;
            } else if (response.role !== 'admin' && currentPath.includes('/admin/')) {
                window.location.href = '/pages/dashboard.html';
            }
        },
        error: function() {
            handleAuthFailure();
        }
    });
}

function handleAuthFailure() {
    localStorage.clear();
    window.location.href = '/auth/login.html';
}

// Run verification immediately
verifySession();

// Check periodically
setInterval(verifySession, 60000); // Every minute