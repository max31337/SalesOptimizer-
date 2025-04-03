$(document).ready(function () {
    const errorMessage = $("#errorMessage");
    
    $("#loginForm").submit(function (event) {
        event.preventDefault();
        
        // Hide error message when submitting
        errorMessage.removeClass('show').text('');
        
        const data = {
            email: $("#email").val(),
            password: $("#password").val()
        };

        $.ajax({
            url: 'http://localhost:8000/api/auth/login/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (response) {
                localStorage.setItem('token', response.access_token);
                localStorage.setItem('userName', response.name);
                localStorage.setItem('userRole', response.role);
                
                if (response.role === 'admin') {
                    window.location.href = '../admin/dashboard.html';
                } else {
                    window.location.href = '../pages/dashboard.html';
                }
            },
            error: function (xhr) {
                errorMessage
                    .text(xhr.responseJSON?.detail || "Login failed")
                    .addClass('show');
            }
        });
    });
});
