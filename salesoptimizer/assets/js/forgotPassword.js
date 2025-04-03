$(document).ready(function() {
    const messageElement = $("#message");

    $("#forgotPasswordForm").on("submit", function(e) {
        e.preventDefault();
        
        const email = $("#email").val();
        
        // Reset message styling
        messageElement.removeClass("error-message success-message");
        
        // Send password reset request
        $.ajax({
            url: "http://localhost:8000/api/auth/forgot-password/",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ email: email }),
            success: function(response) {
                messageElement
                    .text("If the email exists, password reset instructions have been sent.")
                    .addClass("success-message");
                
                // Clear the form
                $("#email").val("");
                
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