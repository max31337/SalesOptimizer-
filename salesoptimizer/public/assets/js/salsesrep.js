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
        url: `${apiConfig.apiUrl}/summary/`, // Assuming this endpoint exists
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


function loadOpportunities() {
    const headers = getAuthHeaders();
    if (!headers) return;

    $.ajax({
        url: `${apiConfig.apiUrl}/opportunity-list/`,
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
                        <td>${opp.customer_name || opp.customer_name || '-'}</td> 
                        <td>${opp.deal_value ? `$${opp.deal_value.toLocaleString()}` : '-'}</td>
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
        url: `${apiConfig.apiUrl}/customer-list/`,
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
                        <td>${cust.company || '-'}</td>
                        <td>${cust.email || '-'}</td>
                        <td>${cust.phone || '-'}</td>
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
        url: `${apiConfig.apiUrl}/interactions/list/`,
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
                        <td>${intr.customer_name || intr.customer_name || '-'}</td>
                        <td>${intr.type || '-'}</td>
                        <td>${intr.description ? intr.description.substring(0, 50) + (intr.description.length > 50 ? '...' : '') : '-'}</td>
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

document.getElementById('createOpportunityBtn').addEventListener('click', function() {
    openOpportunityModal();
});
document.getElementById('newCustomerBtn').addEventListener('click', function() {
    openCustomerModal();
});
document.getElementById('newInteractionBtn').addEventListener('click', function() {
    openInteractionModal();
});

// Show the modal
function openOpportunityModal() {
    $('#opportunityModal').show();
    fetchCustomersForOpportunity();
}
function openCustomerModal() {
    $('#customerModal').show();
}

function openInteractionModal() {
    $('#interactionModal').show();
    fetchCustomersForInteraction();
}

function openOpportunitySuccessModal() {
    $('#opportunitySuccessModal').fadeIn();
}
function openCustomerSuccessModal() {
    $('#customerSuccessModal').fadeIn();
}
function openInteractionSuccessModal() {
    $('#interactionSuccessModal').fadeIn();
}

// Function to close the modal
function closeOpportunityModal() {
    $('#opportunityModal').hide();
    $('#opportunityForm')[0].reset();
}

function closeCustomerModal() {
    $('#customerModal').hide();

    const form = document.getElementById('customerForm');
    if (form && form.tagName === 'FORM') {
        form.reset();
    }
}

function closeInteractionModal() {
    $('#interactionModal').hide();
    $('#interactionModal')[0].reset();
}

function closeOpportunitySuccessModal() {
    $('#opportunitySuccessModal').hide();
}
function closeCustomerSuccessModal() {
    $('#customerSuccessModal').hide();
}

function closeInteractionSuccessModal() {
    $('#interactionSuccessModal').hide();
}

window.openOpportunitySuccessModal = openOpportunitySuccessModal
window.openCustomerSuccessModal = openCustomerSuccessModal 
window.openInteractionSuccessModal = openInteractionSuccessModal
window.closeOpportunityModal = closeOpportunityModal;
window.closeCustomerModal = closeCustomerModal;
window.closeInteractionModal = closeInteractionModal;
window.closeOpportunitySuccessModal = closeOpportunitySuccessModal;
window.closeCustomerSuccessModal = closeCustomerSuccessModal;
window.closeInteractionSuccessModal = closeInteractionSuccessModal;




// Event listeners for closing the modal
$(document).ready(function() {
    // Close when clicking outside the modal-content
    $('#opportunityModal').on('click', function(event) {
        if ($(event.target).is('#opportunityModal')) {
            closeOpportunityModal();
        }
    });
});
$(document).ready(function() {
    // Close when clicking outside the modal-content
    $('#customerModal').on('click', function(event) {
        if ($(event.target).is('#customerModal')) {
            closeCustomerModal();
        }
    });
});
$(document).ready(function() {
    // Close when clicking outside the modal-content
    $('#interactionModal').on('click', function(event) {
        if ($(event.target).is('#interactionModal')) {
            closeInteractionModal();
        }
    });
});

$(document).ready(function() {
    // Close when clicking outside the modal-content
    $('#opportunitySuccessModal').on('click', function(event) {
        if ($(event.target).is('#opportunitySuccessModal')) {
            closeOpportunitySuccessModal();
        }
    });
});

$(document).ready(function() {
    // Close when clicking outside the modal-content
    $('#customerSuccessModal').on('click', function(event) {
        if ($(event.target).is('#customerSuccessModal')) {
            closeCustomerSuccessModal();
        }
    });
});

$(document).ready(function() {
    // Close when clicking outside the modal-content
    $('#interactionSuccessModal').on('click', function(event) {
        if ($(event.target).is('#interactionSuccessModal')) {
            closeInteractionSuccessModal();
        }
    });
});

// Fetch customers and populate dropdown
function fetchCustomersForOpportunity() {
    const customerSelect = document.getElementById('oppCustomer');
    customerSelect.innerHTML = '<option value="">Loading...</option>';
    // Use the API config and auth headers for consistency
    const headers = getAuthHeaders();
    if (!headers) {
        customerSelect.innerHTML = '<option value="">Error loading customers</option>';
        return;
    }
    $.ajax({
        url: `${apiConfig.apiUrl}/customer-list/`,
        headers: headers,
        method: 'GET',
        success: function(data) {
            customerSelect.innerHTML = '';
            if (data && data.length > 0) {
                data.forEach(function(customer) {
                    // Check if customer.id exists, if not use customer._id
                    const customerId = customer.id || customer._id;
                    customerSelect.innerHTML += `<option value="${customerId}">${customer.name} (ID: ${customerId})</option>`;
                });
            } else {
                customerSelect.innerHTML = '<option value="">No customers found</option>';
            }
        },
        error: function() {
            customerSelect.innerHTML = '<option value="">Error loading customers</option>';
        }
    });
}
// Fetch customers and populate dropdown
function fetchCustomersForInteraction() {
    const customerSelect = document.getElementById('interactCustomer');
    customerSelect.innerHTML = '<option value="">Loading...</option>';
    // Use the API config and auth headers for consistency
    const headers = getAuthHeaders();
    if (!headers) {
        customerSelect.innerHTML = '<option value="">Error loading customers</option>';
        return;
    }
    $.ajax({
        url: `${apiConfig.apiUrl}/customer-list/`,
        headers: headers,
        method: 'GET',
        success: function(data) {
            customerSelect.innerHTML = '';
            if (data && data.length > 0) {
                data.forEach(function(customer) {
                    customerSelect.innerHTML += `<option value="${customer.id}">${customer.name} (ID: ${customer.id})</option>`;
                });
            } else {
                customerSelect.innerHTML = '<option value="">No customers found</option>';
            }
        },
        error: function() {
            customerSelect.innerHTML = '<option value="">Error loading customers</option>';
        }
    });
}

// Handle form submission
document.getElementById('opportunityForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const headers = getAuthHeaders();
    if (!headers) return;
    const formData = {
        title: document.getElementById('oppTitle').value,
        deal_value: parseFloat(document.getElementById('oppDealValue').value),
        currency: document.getElementById('oppCurrency').value,
        stage: document.getElementById('oppStage').value,
        probability: parseFloat(document.getElementById('oppProbability').value) / 100, // Convert percent to 0-1
        expected_close_date: document.getElementById('oppExpectedClose').value,
        customer_id: parseInt(document.getElementById('oppCustomer').value)
    };
    $.ajax({
        url: `${apiConfig.apiUrl}/opportunity-create/`,
        headers: headers,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function() {
            closeOpportunityModal();
            openOpportunitySuccessModal(); 
            loadOpportunities && loadOpportunities();
        },
        error: function() {
            alert('Failed to create opportunity.');
        }
    });
});

document.getElementById('customerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const headers = getAuthHeaders();
    if (!headers) return;
    const formData = {
        name: document.getElementById('cusName').value,
        company: document.getElementById('cusCompany').value,
        email: document.getElementById('cusEmail').value,
        phone: document.getElementById('cusPhone').value,
        address: document.getElementById('cusAddress').value,
        segment: document.getElementById('cusSegment').value,
        status: document.getElementById('cusStatus').value,
        industry: document.getElementById('cusIndustry').value,
        annualRevenue: parseFloat(document.getElementById('cusAnRevenue').value),
        employeeCount: parseFloat(document.getElementById('cusEmployeeCount').value),
    };
    $.ajax({
        url: `${apiConfig.apiUrl}/customer-create/`,
        headers: headers,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function() {
            closeCustomerModal();
            openCustomerSuccessModal();
            loadCustomers && loadCustomers();
        },
        error: function(xhr) {
            if (xhr.responseJSON && xhr.responseJSON.detail) {
                // Create or get error message container
                let errorContainer = document.getElementById('customerFormError');
                if (!errorContainer) {
                    errorContainer = document.createElement('div');
                    errorContainer.id = 'customerFormError';
                    errorContainer.className = 'alert alert-danger alert-dismissible fade show';
                    errorContainer.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 9999; max-width: 350px; background-color: #f8d7da; color: #721c24; padding: 1rem; border: 1px solid #f5c6cb; border-radius: 4px; box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15); text-align: center;';
                    
                    // Add close button
                    const closeButton = document.createElement('button');
                    closeButton.type = 'button';
                    closeButton.className = 'btn-close';
                    closeButton.setAttribute('data-bs-dismiss', 'alert');
                    closeButton.style.position = 'absolute';
                    closeButton.style.right = '10px';
                    closeButton.style.top = '10px';
                    closeButton.onclick = function() {
                        errorContainer.remove();
                    };
                    
                    errorContainer.appendChild(closeButton);
                    document.body.appendChild(errorContainer);
                }
                
                // Set error message with icon
                errorContainer.innerHTML = `
                    <div style="margin-bottom: 10px;">
                        <i class="fas fa-exclamation-circle" style="font-size: 24px; color: #721c24; margin-bottom: 10px;"></i>
                    </div>
                    <div style="margin-bottom: 15px;">${xhr.responseJSON.detail}</div>
                    <button type="button" class="btn-close" style="position: absolute; right: 10px; top: 10px;" onclick="this.parentElement.remove()"></button>
                `;
                
                // Auto-hide after 5 seconds
                setTimeout(() => {
                    if (errorContainer && errorContainer.parentNode) {
                        errorContainer.remove();
                    }
                }, 5000);
            } else {
                alert('Failed to create customer.');
            }
        }
    });
});



document.addEventListener('DOMContentLoaded', () => {
    loadSalesOverviewChart();
    renderMonthlyOpportunitiesChart();
    renderWinLossRatioChart();
    renderSalesPipelineChart();
});


// Function to load the sales overview chart
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

// You might also need to ensure the customer_id is set when the modal is opened
// Example: When clicking an "Add Opportunity" button for a specific customer
$(document).on('click', '.add-opportunity-btn', function() {
    const customerId = $(this).data('customer-id'); // Get customer ID from button's data attribute
    $('#opportunityCustomerId').val(customerId); // Set it in the hidden input
    // Or set it on the modal data attribute
    // $('#addOpportunityModal').data('customer-id', customerId); 
    $('#addOpportunityModal').show(); // Show the modal
});

// Attach the event listener
document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("addTaskBtn");
    if (btn) {
      btn.addEventListener("click", addTask);
    }
  });

function addTask() {
    const container = document.getElementById('taskList');
    const task = document.createElement('div');
    task.className = 'task-item';
    task.innerHTML = `
      <input type="checkbox" disabled>
      <input type="text" name="tasks[]" placeholder="Enter task" required>
    `;
    container.appendChild(task);
  }


document.getElementById('interactionForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const headers = getAuthHeaders();
    if (!headers) return;

    // Collect form data
    const taskInputs = document.querySelectorAll('#taskList input[name="tasks[]"]');
    const tasks = Array.from(taskInputs).map(input => input.value.trim()).filter(task => task !== '');

    const formData = {
        type: document.getElementById('interactType').value,
        subject: document.getElementById('interactSubject').value,
        description: document.getElementById('interactDescription').value,
        notes: document.getElementById('interactNotes').value,
        interaction_date: document.getElementById('interactDate').value,
        follow_up_date: document.getElementById('interactFollowUpDate').value,
        follow_up_status: document.getElementById('interactFollowUpStatus').value,
        customer_id: document.getElementById('interactCustomer').value,
        tasks: tasks 
    };

    $.ajax({
        url: `${apiConfig.apiUrl}/interaction-create/`,
        headers: headers,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function () {
            $('#interactionModal').hide();
            $('#interactionSuccessModal').show();
            loadInteractions && loadInteractions(); // refresh list if applicable
        },
        error: function (xhr) {
            console.error(xhr.responseText);
            alert('Failed to create interaction.');
        }
    });
});

// charts for overview

function loadSalesOverviewChart() {
    const headers = getAuthHeaders();
    if (!headers) return;

    $.ajax({
        url: `${apiConfig.apiUrl}/monthly-summary/`,
        headers: headers,
        method: 'GET',
        success: function(summary) {
            if (salesChartInstance) {
                salesChartInstance.destroy();
            }

            const ctx = document.getElementById('salesOverviewChart').getContext('2d');
            
            // Shadcn UI inspired colors and styling
            const chartColors = {
                primary: 'hsl(221.2 83.2% 53.3%)',
                secondary: 'hsl(346.8 77.2% 49.8%)',
                muted: 'hsl(215.4 16.3% 46.9%)',
                background: 'hsl(0 0% 100%)',
                border: 'hsl(214.3 31.8% 91.4%)'
            };

            salesChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Monthly Performance'],
                    datasets: [
                        {
                            label: 'Total Value ($)',
                            data: [summary.monthly_value],
                            backgroundColor: `${chartColors.primary}`, // Adding transparency
                            borderColor: chartColors.primary,
                            borderWidth: 2,
                            borderRadius: 6,
                            barThickness: 70
                            
                        },
                        {
                            label: 'Average Deal Size ($)',
                            data: [summary.average_deal_size],
                            backgroundColor: `${chartColors.secondary}`, // Adding transparency
                            borderColor: chartColors.secondary,
                            borderWidth: 2,
                            borderRadius: 6,
                            barThickness: 70
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Monthly Sales Performance',
                            color: chartColors.muted,
                            font: {
                                size: 16,
                                weight: '500',
                                family: "'Inter', sans-serif"
                            },
                            padding: {
                                top: 20,
                                bottom: 20
                            }
                        },
                        legend: {
                            position: 'bottom',
                            labels: {
                                usePointStyle: true,
                                pointStyle: 'circle',
                                padding: 20,
                                color: chartColors.muted,
                                font: {
                                    family: "'Inter', sans-serif",
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            backgroundColor: chartColors.background,
                            titleColor: chartColors.muted,
                            titleFont: {
                                family: "'Inter', sans-serif",
                                size: 13,
                                weight: '500'
                            },
                            bodyColor: chartColors.muted,
                            bodyFont: {
                                family: "'Inter', sans-serif",
                                size: 12
                            },
                            borderColor: chartColors.border,
                            borderWidth: 1,
                            padding: 12,
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) {
                                        label += ': ';
                                    }
                                    label += new Intl.NumberFormat('en-US', {
                                        style: 'currency',
                                        currency: 'USD'
                                    }).format(context.raw);
                                    return label;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            border: {
                                display: false
                            },
                            grid: {
                                color: chartColors.border,
                                drawBorder: false
                            },
                            ticks: {
                                color: chartColors.muted,
                                font: {
                                    family: "'Inter', sans-serif",
                                    size: 12
                                },
                                padding: 10,
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        },
                        x: {
                            border: {
                                display: false
                            },
                            grid: {
                                display: false
                            },
                            ticks: {
                                color: chartColors.muted,
                                font: {
                                    family: "'Inter', sans-serif",
                                    size: 12
                                },
                                padding: 10
                            }
                        }
                    }
                }
            });

            $('#monthlyDeals').text(summary.monthly_deals);
        },
        error: function(xhr) {
            console.error('Error loading sales overview chart:', xhr.status, xhr.responseJSON?.detail);
            if (xhr.status === 401 || xhr.status === 403) logout();
        }
    });
}

function renderMonthlyOpportunitiesChart() {
    const headers = getAuthHeaders();
    if (!headers) return;

    $.ajax({
        url: `${apiConfig.apiUrl}/monthly-opportunities/`,
        headers: headers,
        method: 'GET',
        success: function(opportunities) {
            // Process data for the chart
            const dates = opportunities.map(opp => new Date(opp.created_at).toLocaleDateString());
            const values = opportunities.map(opp => opp.deal_value);

            // Shadcn UI inspired colors
            const colors = {
                primary: 'hsl(252 83.3% 14.1%)',
                background: 'hsl(0 0% 100%)',
                foreground: 'hsl(224 71.4% 4.1%)',
                muted: 'hsl(215.4 16.3% 46.9%)',
                border: 'hsl(214.3 31.8% 78.4%)',
                accent: 'hsl(210 40% 96.1%)'
            };

            // Get the chart context
            const ctx = document.getElementById('monthlyOpportunitiesChart').getContext('2d');
            
            // Create the line chart with shadcn styling
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Opportunity Value',
                        data: values,
                        borderColor: colors.primary,
                        backgroundColor: `${colors.primary}`,
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: colors.primary,
                        pointBorderColor: colors.primary,
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Monthly Opportunities Timeline',
                            color: colors.foreground,
                            font: {
                                size: 16,
                                weight: '500',
                                family: "'Inter', system-ui, sans-serif"
                            },
                            padding: {
                                top: 20,
                                bottom: 20
                            }
                        },
                        legend: {
                            position: 'top',
                            align: 'start',
                            labels: {
                                usePointStyle: true,
                                pointStyle: 'circle',
                                padding: 20,
                                color: colors.muted,
                                font: {
                                    family: "'Inter', system-ui, sans-serif",
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            backgroundColor: colors.background,
                            titleColor: colors.foreground,
                            bodyColor: colors.muted,
                            borderColor: colors.border,
                            borderWidth: 1,
                            padding: 12,
                            bodyFont: {
                                family: "'Inter', system-ui, sans-serif"
                            },
                            titleFont: {
                                family: "'Inter', system-ui, sans-serif",
                                weight: '500'
                            },
                            callbacks: {
                                label: function(context) {
                                    return new Intl.NumberFormat('en-US', {
                                        style: 'currency',
                                        currency: 'USD'
                                    }).format(context.raw);
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                color: colors.border,
                                drawBorder: false
                            },
                            ticks: {
                                color: colors.muted,
                                font: {
                                    family: "'Inter', system-ui, sans-serif",
                                    size: 12
                                }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            border: {
                                display: false
                            },
                            grid: {
                                color: colors.border,
                                drawBorder: false
                            },
                            ticks: {
                                color: colors.muted,
                                font: {
                                    family: "'Inter', system-ui, sans-serif",
                                    size: 12
                                },
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
        },
        error: function(xhr) {
            console.error('Error loading monthly opportunities:', xhr.status, xhr.responseJSON?.detail);
            if (xhr.status === 401 || xhr.status === 403) logout();
        }
    });
}

function renderWinLossRatioChart() {
    const headers = getAuthHeaders();
    if (!headers) return;

    $.ajax({
        url: `${apiConfig.apiUrl}/win-loss/`,
        headers: headers,
        method: 'GET',
        success: function(summary) {
            const ctx = document.getElementById('winLossRatioChart').getContext('2d');
            
            // Shadcn UI inspired colors
            const colors = {
                primary: 'hsl(142.1 76.2% 36.3%)',     // Success green
                danger: 'hsl(346.8 77.2% 49.8%)',      // Danger red
                muted: 'hsl(215.4 16.3% 46.9%)',
                border: 'hsl(214.3 31.8% 91.4%)',
                background: 'hsl(0 0% 100%)'
            };

            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Won', 'Lost'],
                    datasets: [{
                        data: [
                            summary.won_opportunities || 0,
                            summary.lost_opportunities || 0
                        ],
                        backgroundColor: [
                            colors.primary,
                            colors.danger
                        ],
                        borderColor: colors.border,
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '75%',
                    plugins: {
                        title: {
                            display: true,
                            text: 'Win/Loss Ratio',
                            color: colors.muted,
                            font: {
                                size: 16,
                                weight: '500',
                                family: "'Inter', sans-serif"
                            },
                            padding: {
                                top: 20,
                                bottom: 20
                            }
                        },
                        legend: {
                            position: 'bottom',
                            labels: {
                                usePointStyle: true,
                                pointStyle: 'circle',
                                padding: 20,
                                color: colors.muted,
                                font: {
                                    family: "'Inter', sans-serif",
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            backgroundColor: colors.background,
                            titleColor: colors.muted,
                            bodyColor: colors.muted,
                            borderColor: colors.border,
                            borderWidth: 1,
                            padding: 12,
                            bodyFont: {
                                family: "'Inter', sans-serif"
                            },
                            titleFont: {
                                family: "'Inter', sans-serif",
                                weight: '500'
                            }
                        }
                    }
                }
            });
        },
        error: function(xhr) {
            console.error('Error loading win/loss ratio:', xhr.status, xhr.responseJSON?.detail);
            if (xhr.status === 401 || xhr.status === 403) logout();
        }
    });
}

function renderSalesPipelineChart() {
    const headers = getAuthHeaders();
    if (!headers) return;

    $.ajax({
        url: `${apiConfig.apiUrl}/pipeline-stages/`,
        headers: headers,
        method: 'GET',
        success: function(pipelineData) {
            const ctx = document.getElementById('salesPipelineChart').getContext('2d');
            
            // Shadcn UI inspired colors
            const colors = {
                primary: 'hsl(221.2 83.2% 53.3%)',     // Blue for count
                secondary: 'hsl(346.8 77.2% 49.8%)',   // Pink for value
                muted: 'hsl(215.4 16.3% 46.9%)',
                border: 'hsl(214.3 31.8% 91.4%)',
                background: 'hsl(0 0% 100%)'
            };

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Lead', 'Prospect', 'Negotiation', 'Closed Won', 'Closed Lost'],
                    datasets: [
                        {
                            label: 'Number of Opportunities',
                            data: [
                                pipelineData.lead_count || 0,
                                pipelineData.prospect_count || 0,
                                pipelineData.negotiation_count || 0,
                                pipelineData.won_count || 0,
                                pipelineData.lost_count || 0
                            ],
                            borderColor: colors.primary,
                            backgroundColor: `${colors.primary}10`,
                            borderWidth: 2,
                            tension: 0.4,
                            pointBackgroundColor: colors.background,
                            pointBorderColor: colors.primary,
                            pointBorderWidth: 2,
                            pointRadius: 4,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Total Value ($)',
                            data: [
                                pipelineData.lead_value || 0,
                                pipelineData.prospect_value || 0,
                                pipelineData.negotiation_value || 0,
                                pipelineData.won_value || 0,
                                pipelineData.lost_value || 0
                            ],
                            borderColor: colors.secondary,
                            backgroundColor: `${colors.secondary}10`,
                            borderWidth: 2,
                            tension: 0.4,
                            pointBackgroundColor: colors.background,
                            pointBorderColor: colors.secondary,
                            pointBorderWidth: 2,
                            pointRadius: 4,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Sales Pipeline Distribution',
                            color: colors.muted,
                            font: {
                                size: 16,
                                weight: '500',
                                family: "'Inter', sans-serif"
                            },
                            padding: {
                                top: 20,
                                bottom: 20
                            }
                        },
                        legend: {
                            position: 'top',
                            align: 'start',
                            labels: {
                                usePointStyle: true,
                                pointStyle: 'circle',
                                padding: 20,
                                color: colors.muted,
                                font: {
                                    family: "'Inter', sans-serif",
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            backgroundColor: colors.background,
                            titleColor: colors.muted,
                            bodyColor: colors.muted,
                            borderColor: colors.border,
                            borderWidth: 1,
                            padding: 12,
                            callbacks: {
                                label: function(context) {
                                    if (context.datasetIndex === 0) {
                                        return `Count: ${context.raw}`;
                                    }
                                    return `Value: $${context.raw.toLocaleString()}`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                color: colors.border,
                                drawBorder: false
                            },
                            ticks: {
                                color: colors.muted,
                                font: {
                                    family: "'Inter', sans-serif",
                                    size: 12
                                }
                            }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Number of Opportunities',
                                color: colors.primary
                            },
                            grid: {
                                color: colors.border,
                                drawBorder: false
                            },
                            ticks: {
                                color: colors.muted,
                                font: {
                                    family: "'Inter', sans-serif",
                                    size: 12
                                }
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Total Value ($)',
                                color: colors.secondary
                            },
                            grid: {
                                drawOnChartArea: false
                            },
                            ticks: {
                                color: colors.muted,
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                },
                                font: {
                                    family: "'Inter', sans-serif",
                                    size: 12
                                }
                            }
                        }
                    }
                }
            });
        },
        error: function(xhr) {
            console.error('Error loading pipeline data:', xhr.status, xhr.responseJSON?.detail);
            if (xhr.status === 401 || xhr.status === 403) logout();
        }
    });
}