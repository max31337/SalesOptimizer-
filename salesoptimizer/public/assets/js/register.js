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

            // Add password validation
            if (password !== confirmPassword) {
                $("#registerErrorMessage")
                    .text("Passwords do not match")
                    .addClass('show');
                return;
            }

            // Add password length validation
            if (password.length < 8) {
                $("#registerErrorMessage")
                    .text("Password must be at least 8 characters long")
                    .addClass('show');
                return;
            }

            const registrationData = {
                username: username,
                password: password,
                confirm_password: confirmPassword,  // Added this field
                invitation_token: token
            };

            $.ajax({
                url: `${apiConfig.apiUrl}/auth/register-invited/`,
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(registrationData),
                success: function(response) {
                    console.log('Registration successful:', response);
                    localStorage.setItem('token', response.access_token);
                    localStorage.setItem('userName', username);
                    localStorage.setItem('userRole', response.role);
                    window.location.href = response.role === 'admin' ? '/admin/dashboard.html' : '/pages/dashboard.html';
                },
                error: function(xhr) {
                    console.error('Registration error:', xhr);
                    $("#registerErrorMessage")
                        .text(xhr.responseJSON?.detail || "Registration failed")
                        .addClass('show');
                }
            });
        });
    } catch (error) {
        console.error('Token decode error:', error); // Debug decode error
        $('#registerErrorMessage').text('Failed to decode token');
        return;
    }
});