import { apiConfig } from './config.js';

$(document).ready(function() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    console.log('Token from URL:', token); // Debug token

    if (!token) {
        $('#registerErrorMessage').text('Invalid invitation token');
        return;
    }

    // Decode JWT token to get email
    const tokenParts = token.split('.');
    console.log('Token parts:', tokenParts.length); // Debug token parts

    try {
        const payload = JSON.parse(atob(tokenParts[1]));
        const email = payload.email;
        console.log('Decoded email:', email); // Debug decoded email

        $('#registerForm').on('submit', function(e) {
            e.preventDefault();

            const username = $('#username').val();
            const password = $('#password').val();
            const confirmPassword = $('#confirmPassword').val();

            console.log('Form data:', { // Debug form data
                email,
                username,
                hasPassword: !!password,
                hasConfirmPassword: !!confirmPassword
            });

            $.ajax({
                url: `${apiConfig.apiUrl}/auth/register-invited/`,
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    email: email,
                    username: username,
                    password: password,
                    confirm_password: confirmPassword,
                    invitation_token: token
                }),
                beforeSend: function(xhr) {
                    console.log('Sending request to:', this.url); // Debug request URL
                    console.log('Request payload:', this.data); // Debug request data
                },
                success: function(response) {
                    console.log('Registration successful:', response);
                    localStorage.setItem('token', response.access_token);
                    localStorage.setItem('userName', response.name);
                    localStorage.setItem('userRole', response.role);

                    if (response.role === 'admin') {
                        window.location.href = '/admin/dashboard.html';
                    } else {
                        window.location.href = '/pages/dashboard.html';
                    }
                },
                error: function(xhr) {
                    console.error('Registration error details:', {
                        status: xhr.status,
                        statusText: xhr.statusText,
                        response: xhr.responseJSON,
                        responseText: xhr.responseText
                    });
                    const error = xhr.responseJSON?.detail || 'Registration failed';
                    $('#registerErrorMessage').text(error).addClass('error');
                }
            });
        });
    } catch (error) {
        console.error('Token decode error:', error); // Debug decode error
        $('#registerErrorMessage').text('Failed to decode token');
        return;
    }
});