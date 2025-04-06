function verifySession() {
    const token = localStorage.getItem('token');
    const userRole = localStorage.getItem('userRole');
    
    if (!token) {
        handleAuthFailure();
        return;
    }

    // Check if admin is trying to access non-admin pages
    const currentPath = window.location.pathname;
    if (currentPath.includes('/pages/') && userRole === 'admin') {
        window.location.href = '/salesoptimizer/admin/dashboard.html';
        return;
    }

    $.ajax({
        url: 'http://localhost:8000/api/auth/check-session',
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(response) {
            if (!response.valid || !response.is_active) {
                handleAuthFailure();
                return;
            }
            
            // Enforce role-based access
            if (response.role === 'admin' && currentPath.includes('/pages/')) {
                window.location.href = '/salesoptimizer/admin/dashboard.html';
            } else if (response.role !== 'admin' && currentPath.includes('/admin/')) {
                window.location.href = '/salesoptimizer/pages/dashboard.html';
            }
        },
        error: function() {
            handleAuthFailure();
        }
    });
}

function handleAuthFailure() {
    localStorage.clear();
    window.location.href = '/salesoptimizer/auth/login.html';
}

// Run verification immediately
verifySession();

// Check periodically
setInterval(verifySession, 60000); // Every minute