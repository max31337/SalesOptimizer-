import { apiConfig } from './config.js';

$(document).ready(function() {
    const messageElement = $("#message");

    $("#forgotPasswordForm").on("submit", function(e) {
        e.preventDefault();
        
        const email = $("#email").val();
        messageElement.removeClass("error-message success-message");
        
        $.ajax({
            url: `${apiConfig.apiUrl}/auth/forgot-password/`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ email: email }),
            success: function(response) {
                console.log('Password reset response:', response);
                messageElement
                    .text("If the email exists, password reset instructions have been sent.")
                    .addClass("success-message");
                
                $("#email").val("");
                
                setTimeout(() => {
                    window.location.href = "login.html";
                }, 3000);
            },
            error: function(xhr) {
                console.error('Password reset error:', xhr);
                messageElement
                    .text(xhr.responseJSON?.detail || "An error occurred. Please try again.")
                    .addClass("error-message");
            }
        });
    });
});