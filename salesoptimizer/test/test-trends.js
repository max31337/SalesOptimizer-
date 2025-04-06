let trendsChart = null;

$(document).ready(function() {
    $('#fetchData').click(function() {
        const token = $('#tokenInput').val();
        const days = $('#daysSelect').val();
        
        if (!token) {
            alert('Please enter an admin token');
            return;
        }

        fetchTrendsData(token, days);
    });
});

function fetchTrendsData(token, days) {
    $.ajax({
        url: `http://localhost:8000/api/analytics/registration-trends?days=${days}`,
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        success: function(response) {
            // Display raw response
            $('#rawResponse').text(JSON.stringify(response, null, 2));
            
            // Update chart
            updateChart(response);
        },
        error: function(xhr) {
            const errorMessage = xhr.responseJSON?.detail || 'Failed to fetch data';
            $('#rawResponse').text(`Error: ${errorMessage}`);
            console.error('Error:', xhr);
        }
    });
}

function updateChart(data) {
    const ctx = document.getElementById('trendsChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (trendsChart) {
        trendsChart.destroy();
    }

    // Format dates for better display
    const formattedDates = data.dates.map(date => {
        return new Date(date).toLocaleDateString();
    });

    trendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: formattedDates,
            datasets: [{
                label: 'New Registrations',
                data: data.counts,
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
}