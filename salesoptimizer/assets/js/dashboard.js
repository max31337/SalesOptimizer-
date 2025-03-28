    document.addEventListener("DOMContentLoaded", () => {
        // Navigation Handling
        const pages = document.querySelectorAll('.page');
        const navLinks = document.querySelectorAll('.sidebar nav a');
        
        function showPage(pageId) {
            pages.forEach(page => page.style.display = 'none');
            navLinks.forEach(link => link.classList.remove('active'));
            document.getElementById(pageId).style.display = 'block';
            document.querySelector(`a[href="#${pageId}"]`).classList.add('active');
        }
    
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const pageId = link.getAttribute('href').substring(1);
                showPage(pageId);
            });
        });
    
        // Initialize Dashboard
        showPage('dashboard');
    
        // Charts Initialization
        const chartConfig = {
            borderColor: 'rgba(98, 0, 234, 0.8)',
            backgroundColor: 'rgba(98, 0, 234, 0.2)',
            tension: 0.4
        };
    
        // Sales Chart
        new Chart(document.getElementById('salesChart'), {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Monthly Sales',
                    data: [6500, 5900, 8000, 8100, 5600, 5500],
                    ...chartConfig
                }]
            }
        });
    
        // Revenue Chart
        new Chart(document.getElementById('revenueChart'), {
            type: 'doughnut',
            data: {
                labels: ['Product A', 'Product B', 'Product C'],
                datasets: [{
                    data: [45, 30, 25],
                    backgroundColor: ['#4CAF50', '#2196F3', '#FF9800']
                }]
            }
        });
    
        // Traffic Chart
        new Chart(document.getElementById('trafficChart'), {
            type: 'bar',
            data: {
                labels: ['Mobile', 'Desktop', 'Tablet'],
                datasets: [{
                    label: 'Visitors',
                    data: [65, 30, 15],
                    backgroundColor: ['#4CAF50', '#2196F3', '#FF9800']
                }]
            }
        });
    
        // Product Chart
        new Chart(document.getElementById('productChart'), {
            type: 'radar',
            data: {
                labels: ['Price', 'Quality', 'Design', 'Features', 'Support'],
                datasets: [{
                    label: 'Product Rating',
                    data: [8, 7, 9, 8, 7],
                    ...chartConfig
                }]
            }
        });
    
        // Demographics Chart
        new Chart(document.getElementById('demographicsChart'), {
            type: 'pie',
            data: {
                labels: ['18-25', '26-35', '36-45', '46+'],
                datasets: [{
                    data: [25, 40, 20, 15],
                    backgroundColor: ['#FF9800', '#4CAF50', '#2196F3', '#9C27B0']
                }]
            }
        });
    
        // Monthly Sales Chart
        new Chart(document.getElementById('monthlySalesChart'), {
            type: 'line',
            data: {
                labels: Array.from({length: 30}, (_, i) => i+1),
                datasets: [{
                    label: 'Daily Sales',
                    data: Array.from({length: 30}, () => Math.floor(Math.random() * 1000)),
                    ...chartConfig
                }]
            }
        });
    
        // Acquisition Chart
        new Chart(document.getElementById('acquisitionChart'), {
            type: 'bar',
            data: {
                labels: ['Direct', 'Social', 'Email', 'Ads'],
                datasets: [{
                    label: 'Customer Acquisition',
                    data: [40, 30, 20, 50],
                    backgroundColor: '#4CAF50'
                }]
            }
        });
    
        // User and Logout Handling (existing code)
    // --- User and Logout ---
    const logoutButton = document.getElementById("logoutButton");
    const userNameDisplay = document.getElementById("userNameDisplay");
    const userName = localStorage.getItem("userName");
    console.log("Retrieved userName from localStorage:", userName);

    if (userName && userName !== "undefined") {
    userNameDisplay.textContent = `Hello, ${userName}!`;
    } else {
    userNameDisplay.textContent = "Hello, Guest!";
    }

    logoutButton.addEventListener("click", () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userName");
    window.location.href = "../index.html";
    });   
 });