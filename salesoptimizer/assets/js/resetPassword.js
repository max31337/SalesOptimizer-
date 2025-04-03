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

        // Reset message styling
        messageElement.removeClass("error-message success-message");

        // Validate passwords match
        if (password !== confirmPassword) {
            messageElement
                .text("Passwords do not match!")
                .addClass("error-message");
            return;
        }

        // Validate password strength
        if (password.length < 8) {
            messageElement
                .text("Password must be at least 8 characters long!")
                .addClass("error-message");
            return;
        }

        // Send password reset request
        $.ajax({
            url: `http://localhost:8000/api/auth/reset-password/${token}`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ password: password }),
            success: function(response) {
                messageElement
                    .text("Password reset successful! Redirecting to login...")
                    .addClass("success-message");
                
                // Clear the form
                $("#resetPasswordForm")[0].reset();
                
                // Redirect to login page after 3 seconds
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