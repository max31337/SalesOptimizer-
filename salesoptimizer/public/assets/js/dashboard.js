document.addEventListener("DOMContentLoaded", () => {
    const pages = document.querySelectorAll('.page');
    const navLinks = document.querySelectorAll('.sidebar nav a');
    const logoutButton = document.getElementById('logoutButton'); // Assuming your logout button has id="logoutButton"

    function showPage(pageId) {
        pages.forEach(page => page.style.display = 'none');
        navLinks.forEach(link => link.classList.remove('active'));
        document.getElementById(pageId).style.display = 'block';
        // Ensure the query selector is correct for your navigation structure
        const activeLink = document.querySelector(`.sidebar nav a[href="#${pageId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const pageId = link.getAttribute('href').substring(1);
            showPage(pageId);
        });
    });

    // --- Logout Functionality ---
    function logout() {
        // Clear user-specific data from local storage
        localStorage.removeItem('token');
        localStorage.removeItem('userRole'); // Add any other relevant keys
        localStorage.removeItem('userName');
        localStorage.removeItem('darkMode'); // Clear theme preference if desired

        // Redirect to the login page
        window.location.href = '/auth/login.html'; // Ensure this path is correct
    }

    // Add event listener to the logout button
    if (logoutButton) {
        logoutButton.addEventListener('click', logout);
    } else {
        console.warn('Logout button not found. Ensure it has the ID "logoutButton".');
    }
    // --- End Logout Functionality ---


    // Activate the default page (e.g., 'dashboard')
    // Check if a hash exists, otherwise default to 'dashboard'
    const initialPage = window.location.hash ? window.location.hash.substring(1) : 'dashboard';
    showPage(initialPage);


    // Charts Initialization (if applicable to user dashboard)
    const chartConfig = {
        borderColor: 'rgba(98, 0, 234, 0.8)',
        backgroundColor: 'rgba(98, 0, 234, 0.2)',
        tension: 0.4
    };

    // Example: Sales Chart (Only if relevant for the user dashboard)
    const salesChartCtx = document.getElementById('salesChart');
    if (salesChartCtx) {
        new Chart(salesChartCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Monthly Sales',
                    data: [6500, 5900, 8000, 8100, 5600, 5500], // Replace with actual user data fetching
                    ...chartConfig
                }]
            }
        });
    }

    // Example: Revenue Chart (Only if relevant for the user dashboard)
    const revenueChartCtx = document.getElementById('revenueChart');
    if (revenueChartCtx) {
        new Chart(revenueChartCtx, {
            type: 'doughnut',
            data: {
                labels: ['Product A', 'Product B', 'Product C'],
                // Replace with actual user data fetching
                datasets: [{
                    data: [300, 150, 100],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)'
                    ]
                }]
            }
        });
    }

    // Add other dashboard-specific initializations here...

}); // End DOMContentLoaded