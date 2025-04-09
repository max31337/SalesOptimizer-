def test_list_users(client, test_admin):
    # Login as admin
    login_response = client.post("/api/auth/login/", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/api/admin/users/",  # Correct endpoint from user_management.py
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "users" in response.json()
    assert "total" in response.json()

def test_get_analytics(client, test_admin):
    login_response = client.post("/api/auth/login/", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]
    
    # Updated analytics endpoints to match the actual routes
    endpoints = [
        "/api/analytics/registration-trends",
        "/api/analytics/active-users",
        "/api/analytics/role-distribution",
        "/api/analytics/login-activity"
    ]
    
    for endpoint in endpoints:
        response = client.get(
            endpoint,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

def test_audit_logs(client, test_admin):
    login_response = client.post("/api/auth/login/", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/api/admin/audit-logs",  # Updated audit logs endpoint
        headers={"Authorization": f"Bearer {token}"},
        params={
            "skip": 0,
            "limit": 10
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_user(client, test_admin):
    # Login as admin
    login_response = client.post("/api/auth/login/", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]
    
    # Create new user
    response = client.post(
        "/api/admin/users/",  # Added trailing slash
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "newuser@test.com",
            "name": "New User",
            "username": "newuser",
            "password": "password123",  # Added password field
            "role": "sales"
        }
    )
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["email"] == "newuser@test.com"

def test_update_user(client, test_admin):
    # Login as admin
    login_response = client.post("/api/auth/login/", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]
    
    # Create user first
    create_response = client.post(
        "/api/admin/users/",  # Added trailing slash
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "updatetest@test.com",
            "name": "Update Test",
            "username": "updatetest",
            "password": "password123",
            "role": "sales-rep"  # Updated role to match enum
        }
    )
    user_id = create_response.json()["id"]
    
    # Update user
    response = client.put(
        f"/api/admin/users/{user_id}/",  # Added trailing slash
        headers={"Authorization": f"Bearer {token}"},
        json={
            "role": "sales-rep",  # Updated role to match enum
            "is_active": True
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User updated successfully"

def test_audit_logs(client, test_admin):
    # Login as admin
    login_response = client.post("/api/auth/login/", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]
    
    # Get audit logs
    response = client.get(
        "/api/audit-logs",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "skip": 0,
            "limit": 10
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Now expecting a list directly

def test_unauthorized_access(client, test_sales_rep):
    # Login as sales rep
    login_response = client.post("/api/auth/login/", json={
        "email": "sales@test.com",
        "password": "sales123"
    })
    token = login_response.json()["access_token"]
    
    # Try to access admin endpoints
    admin_endpoints = [
        "/api/admin/users/",  # Added trailing slash
        "/api/analytics/registration-trends",  # Updated path
        "/api/admin/audit-logs"  # Updated path
    ]
    
    for endpoint in admin_endpoints:
        response = client.get(
            endpoint,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403