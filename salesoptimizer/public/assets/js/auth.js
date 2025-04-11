import { apiConfig } from './config.js';

$(document).ready(function () {
    const errorMessage = $("#errorMessage");
    
    $("#loginForm").submit(function (event) {
        event.preventDefault();
        const email = $("#email").val();
        const password = $("#password").val();
        
        console.log("Login attempt with:", { email, apiUrl: apiConfig.apiUrl });
        
        $.ajax({
            url: `${apiConfig.apiUrl}/auth/login/`,
            method: "POST",
            contentType: "application/json",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({ email, password }),
            success: function(response) {
                console.log("Login successful:", response);
                localStorage.setItem('token', response.access_token);
                localStorage.setItem('userName', response.name);
                localStorage.setItem('userRole', response.role);
                
                console.log("Stored user role:", response.role);
                console.log("Redirecting to dashboard...");
                
                if (response.role === 'admin') {
                    window.location.href = '/admin/dashboard.html';
                } else {
                    window.location.href = '/pages/dashboard.html';
                }
            },
            error: function(xhr) {
                console.error("Login failed:", {
                    status: xhr.status,
                    response: xhr.responseText,
                    headers: xhr.getAllResponseHeaders()
                });
                $("#errorMessage")
                    .text(xhr.responseJSON?.detail || "Login failed")
                    .addClass('show');
            }
        });
    });
});
