document.getElementById('inviteForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('inviteEmail').value;
    const role = document.getElementById('inviteRole').value;
    
    try {
        const response = await fetch('/api/admin/invite/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ email, role })
        });
        
        if (!response.ok) throw new Error('Failed to send invitation');
        
        alert('Invitation sent successfully!');
        loadUsers();
    } catch (error) {
        alert('Error sending invitation: ' + error.message);
    }
});

async function loadUsers() {
    try {
        const response = await fetch('/api/admin/users/', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load users');
        
        const users = await response.json();
        const tbody = document.querySelector('#userTable tbody');
        tbody.innerHTML = users.map(user => `
            <tr>
                <td>${user.email}</td>
                <td>${user.role}</td>
                <td>${user.is_verified ? 'Verified' : 'Pending'}</td>
                <td>
                    <button onclick="toggleUserStatus('${user.id}')">
                        ${user.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        alert('Error loading users: ' + error.message);
    }
}

// Load users when page loads
document.addEventListener('DOMContentLoaded', loadUsers);