document.addEventListener("DOMContentLoaded", () => {
    const logoutButton = document.getElementById("logoutButton");
    const userNameDisplay = document.getElementById("userNameDisplay");

    const userName = localStorage.getItem("userName");
    if (userName) {
        userNameDisplay.textContent = `Hello, ${userName}!`;
    } else {
        userNameDisplay.textContent = "Welcome!";
    }

    logoutButton.addEventListener("click", () => {
        localStorage.removeItem("token");
        localStorage.removeItem("userName");
        window.location.href = "../index.html";
    });

    // Sales Performance Chart (Bar Chart)
    new Chart(document.getElementById("salesChart"), {
        type: "bar",
        data: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            datasets: [{
                label: "Sales ($)",
                data: [1200, 1500, 800, 1800, 2000, 1700],
                backgroundColor: "rgba(75, 192, 192, 0.6)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Recent Transactions Chart (Pie Chart)
    new Chart(document.getElementById("transactionsChart"), {
        type: "pie",
        data: {
            labels: ["Completed", "Pending", "Failed"],
            datasets: [{
                label: "Transactions",
                data: [65, 20, 15],
                backgroundColor: ["#36A2EB", "#FFCE56", "#FF6384"]
            }]
        },
        options: {
            responsive: true
        }
    });

    // Customer Engagement Chart (Line Chart)
    new Chart(document.getElementById("engagementChart"), {
        type: "line",
        data: {
            labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
            datasets: [{
                label: "Engagement Score",
                data: [30, 50, 70, 90],
                fill: false,
                borderColor: "#FF6384",
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});
