import { apiConfig } from './config.js';

$(document).ready(function () {
    const errorMessage = $("#errorMessage");
    
    $("#loginForm").submit(function (event) {
        event.preventDefault();
        console.log("Attempting login to:", apiConfig.apiUrl); // Add this line
        
        $.ajax({
            url: `${apiConfig.apiUrl}/auth/login/`,
            method: "POST",
            contentType: "application/json",
            xhrFields: {
                withCredentials: false  // Change to false since we're using token-based auth
            },
            headers: {
                'Accept': '*/*',
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                email: $("#email").val(),
                password: $("#password").val()
            }),
            success: function(response) {
                console.log("Login response:", response); 
                localStorage.setItem('token', response.access_token);
                localStorage.setItem('userName', response.name);
                localStorage.setItem('userRole', response.role);
                
                if (response.role === 'admin') {
                    window.location.href = '../admin/dashboard.html';
                } else {
                    window.location.href = '../dashboard.html';
                }
            },
            error: function(xhr) {
                console.error("Login error details:", xhr);  // Enhanced logging
                $("#errorMessage")
                    .text(xhr.responseJSON?.detail || "Login failed")
                    .addClass('show');
            }
        });
    });
});
