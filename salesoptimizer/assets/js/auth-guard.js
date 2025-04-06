function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.replace('/salesoptimizer/pages/404.html');
    }
}

function checkAdminAuth() {
    const token = localStorage.getItem('token');
    const userRole = localStorage.getItem('userRole');
    
    if (!token || userRole !== 'admin') {
        window.location.replace('/salesoptimizer/pages/404.html');
    }
}

// Run auth check when script loads
if (window.location.href.includes('/admin/')) {
    checkAdminAuth();
} else {
    checkAuth();
}