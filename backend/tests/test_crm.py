import pytest
from datetime import datetime

def test_create_customer(client, test_sales_rep):
    # Login first
    login_response = client.post("/api/auth/login/", json={
        "email": "sales@test.com",
        "password": "sales123"
    })
    token = login_response.json()["access_token"]
    
    # Create customer
    response = client.post(
        "/api/crm/customers/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Customer",
            "email": "customer@test.com",
            "phone": "1234567890",
            "company": "Test Company",
            "status": "active"
        }
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Customer"

def test_create_interaction(client, test_sales_rep):
    # Login and create customer first
    login_response = client.post("/api/auth/login/", json={
        "email": "sales@test.com",
        "password": "sales123"
    })
    token = login_response.json()["access_token"]
    
    # Create customer
    customer_response = client.post(
        "/api/crm/customers/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Customer",
            "email": "customer@test.com",
            "phone": "1234567890",
            "company": "Test Company",
            "status": "active"
        }
    )
    customer_id = customer_response.json()["id"]
    
    # Create interaction
    response = client.post(
        "/api/crm/interactions/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "type": "call",
            "notes": "Test call",
            "interaction_date": datetime.utcnow().isoformat(),
            "customer_id": customer_id,
            "sales_rep_id": test_sales_rep.id
        }
    )
    assert response.status_code == 200
    assert response.json()["type"] == "call"