let userDistributionChart = null;
let roleDistributionChart = null;
let loginActivityChart = null;
let loginSuccessChart = null;
let registrationChart = null;

function destroyAllCharts() {
    const charts = [
        userDistributionChart,
        roleDistributionChart,
        loginActivityChart,
        loginSuccessChart,
        registrationChart
    ];
    
    charts.forEach(chart => {
        if (chart) {
            chart.destroy();
        }
    });
}

function loadAllAnalytics() {
    destroyAllCharts();
    
    // Add a small delay before recreating charts
    setTimeout(() => {
        loadRegistrationTrends();
        loadActiveUsers();
        loadLoginActivity();
        loadRoleDistribution();
    }, 50);
}

// Update document ready handler
$(document).ready(function() {
    // Only load analytics if we're on the overview section
    if ($('#overview').is(':visible')) {
        loadAllAnalytics();
        
        // Refresh data every 30 seconds only if overview section is visible
        const refreshInterval = setInterval(() => {
            if ($('#overview').is(':visible')) {
                loadAllAnalytics();
            }
        }, 30000);
    }
});

// Export function for use in other files
window.loadAllAnalytics = loadAllAnalytics;
window.destroyAllCharts = destroyAllCharts;


function loadRegistrationTrends(days = 30) {
    const token = localStorage.getItem('token');
    console.log('Loading registration trends...');
    
    $.ajax({
        url: `${apiConfig.apiUrl}/analytics/registration-trends?days=${days}`,
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(response) {
            console.log('Registration trends data:', response);
            $('#trendsDebug').text(JSON.stringify(response, null, 2));
            
            const ctx = document.getElementById('registrationTrendsChart').getContext('2d');
            
            if (registrationChart) {
                registrationChart.destroy();
            }

            const formattedDates = response.dates.map(date => {
                return new Date(date).toLocaleDateString();
            });

            registrationChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedDates,
                    datasets: [{
                        label: 'New Registrations',
                        data: response.counts,
                        borderColor: '#2196F3',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        title: {
                            display: true,
                            text: 'User Registration Trends'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        },
        error: function(xhr) {
            console.error('Failed to load registration trends:', xhr);
            showNotification('Failed to load registration trends', 'error');
            $('#trendsDebug').text('Error: ' + (xhr.responseJSON?.detail || 'Failed to fetch data'));
        }
    });
}

function loadActiveUsers() {
    const token = localStorage.getItem('token');
    
    $.ajax({
        url: '${apiConfig.apiUrl}/analytics/active-users',
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(response) {
            // Update metrics
            $('#totalUsers').text(response.total_users);
            $('#activeUsers').text(response.active_users);
            $('#verifiedUsers').text(response.verified_users);
            
            // Update distribution chart
            const ctx = document.getElementById('userDistributionChart').getContext('2d');
            
            if (userDistributionChart) {
                userDistributionChart.destroy();
            }

            userDistributionChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Active', 'Inactive'],
                    datasets: [{
                        data: [response.active_users, response.inactive_users],
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.8)',
                            'rgba(255, 99, 132, 0.8)'
                        ],
                        borderColor: [
                            'rgba(75, 192, 192, 1)',
                            'rgba(255, 99, 132, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        },
        error: function(xhr) {
            console.error('Failed to load active users:', xhr);
            showNotification('Failed to load active users metrics', 'error');
        }
    });
}

function loadRoleDistribution() {
    const token = localStorage.getItem('token');
    
    $.ajax({
        url: '${apiConfig.apiUrl}/analytics/role-distribution',
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(response) {
            const ctx = document.getElementById('roleDistributionChart').getContext('2d');
            
            if (roleDistributionChart) {
                roleDistributionChart.destroy();
            }

            roleDistributionChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: response.roles.map(role => role.charAt(0).toUpperCase() + role.slice(1)),
                    datasets: [{
                        data: response.counts,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 206, 86, 0.8)',
                            'rgba(75, 192, 192, 0.8)'
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 10,
                                boxWidth: 12
                            }
                        }
                    }
                }
            });
        },
        error: function(xhr) {
            console.error('Failed to load role distribution:', xhr);
            showNotification('Failed to load role distribution', 'error');
        }
    });
}

function loadLoginActivity() {
    const token = localStorage.getItem('token');
    
    $.ajax({
        url: '${apiConfig.apiUrl}/analytics/login-activity',
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(response) {
            // Login Activity Timeline Chart
            const activityCtx = document.getElementById('loginActivityChart').getContext('2d');
            
            if (loginActivityChart) {
                loginActivityChart.destroy();
            }

            loginActivityChart = new Chart(activityCtx, {
                type: 'line',
                data: {
                    labels: response.dates.map(date => new Date(date).toLocaleDateString()),
                    datasets: [{
                        label: 'Daily Logins',
                        data: response.counts,
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 12,
                                padding: 15
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });

            // Login Success Rate Chart
            const successCtx = document.getElementById('loginSuccessChart').getContext('2d');
            
            if (loginSuccessChart) {
                loginSuccessChart.destroy();
            }

            loginSuccessChart = new Chart(successCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Successful', 'Failed'],
                    datasets: [{
                        data: [response.total_success, response.total_failed],
                        backgroundColor: [
                            'rgba(76, 175, 80, 0.8)',
                            'rgba(244, 67, 54, 0.8)'
                        ],
                        borderColor: [
                            'rgba(76, 175, 80, 1)',
                            'rgba(244, 67, 54, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 12,
                                padding: 15
                            }
                        }
                    }
                }
            });

            // Update Failed Login Attempts section
            const failureList = $('.failure-list');
            const ipList = $('.ip-list');
            
            // Clear existing lists
            failureList.empty();
            ipList.empty();

            // Populate recent failures
            if (response.recent_failures && response.recent_failures.length > 0) {
                response.recent_failures.forEach(failure => {
                    const date = new Date(failure.timestamp).toLocaleString();
                    failureList.append(`
                        <li>
                            <span>${date}</span>
                            <span>${failure.ip_address}</span>
                        </li>
                    `);
                });
            } else {
                failureList.append('<li>No recent failed attempts</li>');
            }

            // Populate suspicious IPs
            if (response.suspicious_ips && response.suspicious_ips.length > 0) {
                response.suspicious_ips.forEach(ip => {
                    ipList.append(`
                        <li class="suspicious-ip">
                            <span>${ip.ip}</span>
                            <span>${ip.failure_count} attempts</span>
                        </li>
                    `);
                });
            } else {
                ipList.append('<li>No suspicious IP activity</li>');
            }
        },
        error: function(xhr) {
            console.error('Failed to load login activity:', xhr);
            showNotification('Failed to load login activity', 'error');
            
            // Show error state in the lists
            $('.failure-list').html('<li>Failed to load data</li>');
            $('.ip-list').html('<li>Failed to load data</li>');
        }
    });
}