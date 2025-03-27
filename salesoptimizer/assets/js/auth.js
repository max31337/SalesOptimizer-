$(document).ready(function() {
    $("#loginForm").submit(function(event) {
        event.preventDefault(); 

        let email = $("#email").val();
        let password = $("#password").val();

        $.ajax({
            url: "http://127.0.0.1:8000/api/auth/login/",  
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ email: email, password: password }),
            success: function(response) {
                console.log("✅ Login successful:", response);

                localStorage.setItem("token", response.access_token);
                localStorage.setItem("userName", response.name); 
                window.location.href = "dashboard.html";  
            },
            error: function(xhr) {
                console.error("❌ Login failed:", xhr.responseJSON.detail);
                $("#errorMessage").text(xhr.responseJSON.detail);
            }
        });
    });
});
