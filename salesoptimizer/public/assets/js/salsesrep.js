import { apiConfig } from './config.js';

let salesChartInstance = null; // Global variable to hold the chart instance

$(document).ready(function() {
    // Ensure config is loaded before proceeding
    if (typeof apiConfig === 'undefined' || !apiConfig.apiUrl) {
        console.error("API configuration is missing. Cannot initialize dashboard.");
        // Optionally display an error message to the user
        $('body').html('<p style="color: red; text-align: center; margin-top: 50px;">Error: Application configuration is missing. Please contact support.</p>');
        return; 
    }
    
    checkSalesRepAccess(); // Check access first
    verifyLocalStorage(); // Verify local storage essentials
    
    // Initial setup: Show overview section and load its data/chart
    $('.content-section').hide(); // Hide all sections initially
    $('#overview').addClass('active').show(); // Show overview section
    loadOverviewData(); // Load overview metrics and chart

    setupNavigationHandlers(); // Setup navigation clicks
});

function verifyLocalStorage() {
    if (!localStorage.getItem('token') || 
        !localStorage.getItem('userRole') || 
        !localStorage.getItem('userName')) {
        // Redirect to login if essential items are missing
        logout(); // Use logout which clears storage and redirects
    }
}

function checkSalesRepAccess() {
    const token = localStorage.getItem('token');
    const userRole = localStorage.getItem('userRole');

    if (!token || userRole !== 'sales-rep') {
        logout(); // Use logout function to clear storage and redirect
        return;
    }

    $.ajax({
        url: `${apiConfig.apiUrl}/auth/me`,
        headers: { 'Authorization': `Bearer ${token}` },
        method: 'GET',
        async: false, // Make this synchronous to ensure user name is loaded before other calls if needed
        success: function(response) {
            if (response.role !== 'sales-rep' || !response.is_active) {
                logout(); // Use logout function
                return;
            }
            // Display the sales rep's name
            $('#salesRepName').text(response.name || 'Sales Rep'); // Use response.name or a default
        },
        error: function(xhr) {
            console.error('Error checking sales rep access:', xhr.status, xhr.responseJSON?.detail);
            if (xhr.status === 401 || xhr.status === 403) {
                logout(); // Use logout function on auth error
            } else {
                // Handle other errors, maybe show a generic error message
                $('#salesRepName').text('Error loading user'); 
                // Consider if the app should proceed or halt on other errors
            }
        }
    });
}

function setupNavigationHandlers() {
    const navLinks = document.querySelectorAll('.sidebar .nav-links a');
    const contentSections = document.querySelectorAll('.main-content .content-section');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            
            // Update active link in sidebar
            navLinks.forEach(nav => nav.parentElement.classList.remove('active'));
            this.parentElement.classList.add('active');

            // Hide all sections
            contentSections.forEach(section => {
                section.style.display = 'none';
                section.classList.remove('active');
            });
            
            // Show target section
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.style.display = 'block'; // Use block or appropriate display style
                targetSection.classList.add('active');

                // Destroy chart if navigating away from overview and it exists
                if (targetId !== 'overview' && salesChartInstance) {
                    salesChartInstance.destroy();
                    salesChartInstance = null;
                }
                
                // Load data based on the target section
                switch (targetId) {
                    case 'overview':
                        loadOverviewData(); // Handles metrics and chart loading
                        break;
                    case 'opportunities':
                        loadOpportunities();
                        break;
                    case 'customers':
                        loadCustomers();
                        break;
                    case 'interactions':
                        loadInteractions();
                        break;
                    default:
                        console.warn(`No data loading function defined for section: ${targetId}`);
                }
            }
        });
    });
}

// --- Data Loading Functions ---

function getAuthHeaders() {
    const token = localStorage.getItem('token');
    if (!token) {
        console.error("Authentication token not found. Redirecting to login.");
        logout(); // Redirect if token is missing
        return null; // Indicate failure
    }
    return { 'Authorization': `Bearer ${token}` };
}

function loadOverviewData() {
    const token = localStorage.getItem('token');
    const headers = getAuthHeaders();
    if (!headers) return; // Stop if no token

    // Fetch summary metrics
    $.ajax({
        url: `${apiConfig.apiUrl}/crm/opportunities/summary/`, // Assuming this endpoint exists
        headers: headers,
        method: 'GET',
        success: function(summary) {
            $('#activeOpportunities').text(summary.active_count || '-');
            $('#pipelineValue').text(summary.total_value ? `$${summary.total_value.toLocaleString()}` : '-');
            $('#winRate').text(summary.win_rate ? `${(summary.win_rate * 100).toFixed(1)}%` : '-');

            console.log('Received summary data:', summary); // Add this line to debug
            
            // Make sure the summary object has the expected properties
            if (!summary) {
                console.error('Summary data is empty or undefined');
                return;
            }
        },
        error: function(xhr) {
            console.error('Error loading overview metrics:', xhr.status, xhr.responseJSON?.detail);
            $('#activeOpportunities').text('Error');
            $('#pipelineValue').text('Error');
            $('#winRate').text('Error');
            if (xhr.status === 401 || xhr.status === 403) logout();
        }
    });

    // Load or reload the chart (will use its own API call)
    loadSalesOverviewChart();
}

function loadSalesOverviewChart() {
    const headers = getAuthHeaders();
    if (!headers) return;

    const ctx = document.getElementById('salesOverviewChart')?.getContext('2d');
    if (!ctx) {
        console.error('Sales Overview Chart canvas element not found.');
        return;
    }

    // Destroy existing chart instance if it exists
    if (salesChartInstance) {
        salesChartInstance.destroy();
        salesChartInstance = null; // Ensure it's cleared
    }

    // Fetch chart data from the API
    $.ajax({
        url: `${apiConfig.apiUrl}/crm/sales/performance`, // Assuming this endpoint exists
        headers: headers,
        method: 'GET',
        success: function(chartApiData) {
            // Assuming API returns data in a format like:
            // { labels: ['Jan', ...], salesValue: [12000, ...], opportunitiesWon: [5, ...] }
            
            const chartData = {
                labels: chartApiData.labels || [],
                datasets: [{
                    label: 'Sales Value ($)',
                    data: chartApiData.salesValue || [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1,
                    fill: true,
                    yAxisID: 'y', // Assign to the primary y-axis
                }, {
                    label: 'Opportunities Won',
                    data: chartApiData.opportunitiesWon || [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1,
                    fill: true,
                    yAxisID: 'y1', // Assign to the second y-axis
                }]
            };

            const config = {
                type: 'line',
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { // Primary Y-axis (Sales Value)
                            beginAtZero: true,
                            position: 'left',
                            title: { display: true, text: 'Sales Value ($)' }
                        },
                        y1: { // Secondary Y-axis (Opportunities Won)
                            beginAtZero: true,
                            position: 'right',
                            title: { display: true, text: 'Opportunities Won' },
                            grid: { drawOnChartArea: false },
                        }
                    },
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: 'Monthly Sales Performance' }
                    }
                },
            };

            // Create the new chart instance
            salesChartInstance = new Chart(ctx, config);
        },
        error: function(xhr) {
            console.error('Error loading sales overview chart data:', xhr.status, xhr.responseJSON?.detail);
            // Optionally display an error message on the chart canvas
            ctx.font = "16px Arial";
            ctx.fillStyle = "red";
            ctx.textAlign = "center";
            ctx.fillText("Error loading chart data.", ctx.canvas.width / 2, ctx.canvas.height / 2);
            if (xhr.status === 401 || xhr.status === 403) logout();
        }
    });
}


function loadOpportunities() {
    const headers = getAuthHeaders();
    if (!headers) return;

    $.ajax({
        url: `${apiConfig.apiUrl}/crm/opportunities/list/`,
        headers: headers,
        method: 'GET',
        success: function(opportunities) {
            const tableBody = $('#opportunitiesTable');
            tableBody.empty(); // Clear existing rows
            if (opportunities.length === 0) {
                tableBody.append('<tr><td colspan="7" class="text-center">No opportunities found.</td></tr>');
                return;
            }
            opportunities.forEach(opp => {
                // Format date nicely (optional)
                const closeDate = opp.expected_close_date ? new Date(opp.expected_close_date).toLocaleDateString() : '-';
                const row = `
                    <tr>
                        <td>${opp.title || '-'}</td>
                        <td>${opp.customer_name || opp.customer_id || '-'}</td> 
                        <td>${opp.value ? `$${opp.value.toLocaleString()}` : '-'}</td>
                        <td>${opp.stage || '-'}</td>
                        <td>${opp.probability ? `${(opp.probability * 100).toFixed(0)}%` : '-'}</td>
                        <td>${closeDate}</td>
                        <td>
                            <button class="btn-icon" onclick="viewOpportunity(${opp.id})"><i data-lucide="eye"></i></button>
                            <button class="btn-icon" onclick="editOpportunity(${opp.id})"><i data-lucide="edit"></i></button>
                            <button class="btn-icon btn-danger" onclick="deleteOpportunity(${opp.id})"><i data-lucide="trash-2"></i></button>
                        </td>
                    </tr>
                `;
                tableBody.append(row);
            });
            lucide.createIcons(); // Re-render icons if new ones were added
        },
        error: function(xhr) {
            console.error('Error loading opportunities:', xhr.status, xhr.responseJSON?.detail);
            $('#opportunitiesTable').empty().append('<tr><td colspan="7" class="text-center text-danger">Error loading opportunities.</td></tr>');
            if (xhr.status === 401 || xhr.status === 403) logout();
        }
    });
}

function loadCustomers() {
    const headers = getAuthHeaders();
    if (!headers) return;

    $.ajax({
        url: `${apiConfig.apiUrl}/crm/customers/list/`,
        headers: headers,
        method: 'GET',
        success: function(customers) {
            const tableBody = $('#customersTable');
            tableBody.empty();
            if (customers.length === 0) {
                tableBody.append('<tr><td colspan="6" class="text-center">No customers found.</td></tr>');
                return;
            }
            customers.forEach(cust => {
                const row = `
                    <tr>
                        <td>${cust.name || '-'}</td>
                        <td>${cust.company_name || '-'}</td>
                        <td>${cust.email || '-'}</td>
                        <td>${cust.phone_number || '-'}</td>
                        <td>${cust.status || '-'}</td>
                        <td>
                            <button class="btn-icon" onclick="viewCustomer(${cust.id})"><i data-lucide="eye"></i></button>
                            <button class="btn-icon" onclick="editCustomer(${cust.id})"><i data-lucide="edit"></i></button>
                            <button class="btn-icon btn-danger" onclick="deleteCustomer(${cust.id})"><i data-lucide="trash-2"></i></button>
                        </td>
                    </tr>
                `;
                tableBody.append(row);
            });
            lucide.createIcons();
        },
        error: function(xhr) {
            console.error('Error loading customers:', xhr.status, xhr.responseJSON?.detail);
            $('#customersTable').empty().append('<tr><td colspan="6" class="text-center text-danger">Error loading customers.</td></tr>');
            if (xhr.status === 401 || xhr.status === 403) logout();
        }
    });
}

function loadInteractions() {
    const headers = getAuthHeaders();
    if (!headers) return;

    $.ajax({
        url: `${apiConfig.apiUrl}/crm/interactions/list/`,
        headers: headers,
        method: 'GET',
        success: function(interactions) {
            const tableBody = $('#interactionsTable');
            tableBody.empty();
            if (interactions.length === 0) {
                tableBody.append('<tr><td colspan="5" class="text-center">No interactions found.</td></tr>');
                return;
            }
            interactions.forEach(intr => {
                const interactionDate = intr.interaction_date ? new Date(intr.interaction_date).toLocaleDateString() : '-';
                const row = `
                    <tr>
                        <td>${interactionDate}</td>
                        <td>${intr.customer_name || intr.customer_id || '-'}</td>
                        <td>${intr.interaction_type || '-'}</td>
                        <td>${intr.summary ? intr.summary.substring(0, 50) + (intr.summary.length > 50 ? '...' : '') : '-'}</td>
                        <td>
                            <button class="btn-icon" onclick="viewInteraction(${intr.id})"><i data-lucide="eye"></i></button>
                            <button class="btn-icon" onclick="editInteraction(${intr.id})"><i data-lucide="edit"></i></button>
                            <button class="btn-icon btn-danger" onclick="deleteInteraction(${intr.id})"><i data-lucide="trash-2"></i></button>
                        </td>
                    </tr>
                `;
                tableBody.append(row);
            });
            lucide.createIcons();
        },
        error: function(xhr) {
            console.error('Error loading interactions:', xhr.status, xhr.responseJSON?.detail);
            $('#interactionsTable').empty().append('<tr><td colspan="5" class="text-center text-danger">Error loading interactions.</td></tr>');
            if (xhr.status === 401 || xhr.status === 403) logout();
        }
    });
}

// --- Placeholder functions for CRUD operations ---
// These would typically open modals or navigate to forms
function viewOpportunity(id) { console.log(`View Opportunity ${id}`); }
function editOpportunity(id) { console.log(`Edit Opportunity ${id}`); }
function deleteOpportunity(id) { console.log(`Delete Opportunity ${id}`); /* Add confirmation */ }
function viewCustomer(id) { console.log(`View Customer ${id}`); }
function editCustomer(id) { console.log(`Edit Customer ${id}`); }
function deleteCustomer(id) { console.log(`Delete Customer ${id}`); /* Add confirmation */ }
function viewInteraction(id) { console.log(`View Interaction ${id}`); }
function editInteraction(id) { console.log(`Edit Interaction ${id}`); }
function deleteInteraction(id) { console.log(`Delete Interaction ${id}`); /* Add confirmation */ }

// --- Event Listeners for Create Buttons ---
$('#createOpportunityBtn').on('click', () => console.log('Create New Opportunity clicked'));
$('#createCustomerBtn').on('click', () => console.log('Create New Customer clicked'));
$('#createInteractionBtn').on('click', () => console.log('Create New Interaction clicked'));


document.addEventListener('DOMContentLoaded', () => {
    renderSalesOverviewChart();
    renderMonthlyOpportunitiesChart();
    renderWinLossRatioChart();
});

const defaultOptions = {
    responsive: true,
    plugins: {
        legend: {
            labels: {
                color: '#333',
                font: {
                    size: 14,
                    family: "'Segoe UI', sans-serif",
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0,0,0,0.7)',
            titleFont: { size: 14 },
            bodyFont: { size: 13 }
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            ticks: { color: '#444' },
            grid: { color: 'rgba(0,0,0,0.05)' }
        },
        x: {
            ticks: { color: '#444' },
            grid: { color: 'rgba(0,0,0,0.02)' }
        }
    }
};

function renderSalesOverviewChart() {
    const ctx = document.getElementById('salesOverviewChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            datasets: [{
                label: 'Sales (USD)',
                data: [4000, 6000, 5500, 7500, 8200],
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderRadius: 8,
                barThickness: 40
            }]
        },
        options: {
            ...defaultOptions,
            plugins: {
                ...defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Sales Overview',
                    font: { size: 18 },
                    color: '#222',
                    padding: { bottom: 10 }
                }
            }
        }
    });
}

function renderMonthlyOpportunitiesChart() {
    const ctx = document.getElementById('monthlyOpportunitiesChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            datasets: [{
                label: 'New Opportunities',
                data: [10, 14, 8, 16, 12],
                borderColor: 'rgba(255, 159, 64, 1)',
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#fff',
                pointBorderColor: 'rgba(255, 159, 64, 1)'
            }]
        },
        options: {
            ...defaultOptions,
            plugins: {
                ...defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Monthly Opportunities',
                    font: { size: 18 },
                    color: '#222',
                    padding: { bottom: 10 }
                }
            }
        }
    });
}

function renderWinLossRatioChart() {
    const ctx = document.getElementById('winLossRatioChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Won', 'Lost'],
            datasets: [{
                label: 'Ratio',
                data: [18, 7],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(255, 99, 132, 0.7)'
                ],
                borderColor: ['#4bc0c0', '#ff6384'],
                borderWidth: 2
            }]
        },
        options: {
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#444',
                        font: { size: 14 }
                    }
                },
                title: {
                    display: true,
                    text: 'Win/Loss Ratio',
                    font: { size: 18 },
                    color: '#222'
                }
            },
            responsive: true,
            cutout: '65%'
        }
    });
}


function logout() {
    console.log("Logging out..."); // Added for debugging
    // Clear local storage
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userName');

    // Redirect to login page
    window.location.href = '/auth/login.html'; // Ensure correct path to login
}

// Explicitly attach logout to the window object if it's called directly from HTML (like onclick="logout()")
window.logout = logout;
