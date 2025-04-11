document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (!token) {
        alert('Invalid registration link');
        window.location.href = '/salesoptimizer/auth/login.html';
        return;
    }

    const form = document.getElementById('registerForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (password !== confirmPassword) {
            document.getElementById('registerErrorMessage').textContent = 'Passwords do not match';
            return;
        }

        try {
            const response = await fetch('${apiConfig.apiUrl}/auth/complete-registration', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token: token,
                    username: username,
                    password: password
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('userName', username);
                alert('Registration completed successfully!');
                window.location.href = '/salesoptimizer/pages/dashboard.html';
            } else {
                document.getElementById('registerErrorMessage').textContent = 
                    data.detail || 'Registration failed';
            }
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('registerErrorMessage').textContent = 
                'An error occurred during registration';
        }
    });
});