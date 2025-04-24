import { apiConfig } from './config.js';

$(document).ready(function() {
    const messageElement = $("#message");
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (!token) {
        messageElement
            .text("Invalid reset link. Please request a new password reset.")
            .addClass("error-message");
        return;
    }

    $("#resetPasswordForm").on("submit", function(e) {
        e.preventDefault();
        
        const password = $("#password").val();
        const confirmPassword = $("#confirmPassword").val();

        messageElement.removeClass("error-message success-message");

        if (password !== confirmPassword) {
            messageElement
                .text("Passwords do not match")
                .addClass("error-message");
            return;
        }
        
        $.ajax({
            url: `${apiConfig.apiUrl}/auth/reset-password/${token}`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                password: password,
                confirm_password: confirmPassword
            }),
            success: function(response) {
                messageElement
                    .text("Password reset successful! Redirecting to login...")
                    .addClass("success-message");
                
                $("#resetPasswordForm")[0].reset();
                
                setTimeout(() => {
                    window.location.href = "login.html";
                }, 3000);
            },
            error: function(xhr) {
                messageElement
                    .text(xhr.responseJSON?.detail || "An error occurred. Please try again.")
                    .addClass("error-message");
            }
        });
    });
});