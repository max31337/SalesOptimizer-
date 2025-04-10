import { apiConfig } from './config.js';

$(document).ready(function () {
    const errorMessage = $("#errorMessage");
    
    $("#loginForm").submit(function (event) {
        event.preventDefault();
        
        $.ajax({
            url: `${apiConfig.apiUrl}/auth/login/`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                email: $("#email").val(),
                password: $("#password").val()
            }),
            success: function (response) {
                localStorage.setItem('token', response.access_token);
                localStorage.setItem('userName', response.name);
                localStorage.setItem('userRole', response.role);
                
                if (response.role === 'admin') {
                    window.location.href = '../admin/dashboard.html';
                } else {
                    window.location.href = '../dashboard.html';
                }
            },
            error: function (xhr) {
                $("#errorMessage")
                    .text(xhr.responseJSON?.detail || "Login failed")
                    .addClass('show');
            }
        });
    });
});
