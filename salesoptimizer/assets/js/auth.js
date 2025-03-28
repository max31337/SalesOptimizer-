$(document).ready(function () {
    // Login Function
    $("#loginForm").submit(function (event) {
        event.preventDefault();

        let email = $("#email").val();
        let password = $("#password").val();

        $.ajax({
            url: "http://127.0.0.1:8000/api/auth/login/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ email: email, password: password }),
            success: function (response) {
                console.log("✅ Login successful:", response);

                // Store token and user details
                localStorage.setItem("token", response.access_token);
                localStorage.setItem("userName", response.name);

                // Redirect to dashboard
                window.location.href = "/salesoptimizer/pages/dashboard.html";
            },
            error: function (xhr) {
                console.error("❌ Login failed:", xhr.responseJSON.detail);
                $("#errorMessage").text(xhr.responseJSON.detail);
            }
        });
    });

    // Register Function
    $("#registerForm").submit(function (event) {
        event.preventDefault();

        let name = $("#name").val();
        let email = $("#email").val();
        let password = $("#password").val();
        let confirmPassword = $("#confirmPassword").val();

        if (password !== confirmPassword) {
            $("#registerErrorMessage").text("Passwords do not match!");
            return;
        }

        $.ajax({
            url: "http://127.0.0.1:8000/api/auth/register/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ name: name, email: email, password: password }),
            success: function (response) {
                console.log("✅ Registration successful:", response);
        
                // Debugging: Check if name is present in the response
                if (!response.name) {
                    console.error("⚠️ Response does not contain 'name'.", response);
                }
        
                // Store user details in localStorage
                localStorage.setItem("token", response.access_token);
                localStorage.setItem("userName", response.name);
        
                // Redirect to dashboard
                window.location.href = "/salesoptimizer/pages/dashboard.html";
            },
            error: function (xhr) {
                console.error("❌ Registration failed:", xhr.responseJSON.detail);
                $("#registerErrorMessage").text(xhr.responseJSON.detail);
            }
        });
    });
});
