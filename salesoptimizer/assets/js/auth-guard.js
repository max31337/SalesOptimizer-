function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/salesoptimizer/pages/404.html';
    }
}

// Run check immediately when script loads
checkAuth();