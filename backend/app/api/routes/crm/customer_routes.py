from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from sqlalchemy import or_

from app.db.database import get_db
from app.models import User, Customer, Interaction  # Updated import
from app.schemas.customer import CustomerCreate, CustomerUpdate, Customer as CustomerSchema
from app.api.routes.auth import get_current_user

router = APIRouter()

# CRUD Operations
@router.post("/customers/", response_model=CustomerSchema)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new customer"""
    db_customer = Customer(**customer.dict())
    db_customer.assigned_to = current_user.id
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/customers/", response_model=List[CustomerSchema])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    segment: Optional[str] = None,
    industry: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List customers with search and filters"""
    query = db.query(Customer)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Customer.name.ilike(f"%{search}%"),
                Customer.company.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%")
            )
        )
    if segment:
        query = query.filter(Customer.segment == segment)
    if industry:
        query = query.filter(Customer.industry == industry)
    if status:
        query = query.filter(Customer.status == status)
    
    # Filter by assigned sales rep if not admin
    if current_user.role != "admin":
        query = query.filter(Customer.assigned_to == current_user.id)
    
    total = query.count()
    customers = query.offset(skip).limit(limit).all()
    
    return customers

@router.get("/customers/{customer_id}", response_model=CustomerSchema)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer details"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if current_user.role != "admin" and customer.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this customer")
    
    return customer

@router.put("/customers/{customer_id}", response_model=CustomerSchema)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update customer details"""
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if current_user.role != "admin" and db_customer.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this customer")
    
    for field, value in customer_update.dict(exclude_unset=True).items():
        setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a customer"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete customers")
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}

# Customer History
@router.get("/customers/{customer_id}/history")
async def get_customer_history(
    customer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer interaction history"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if current_user.role != "admin" and customer.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this customer's history")
    
    history = []
    
    # Get interactions
    interactions = (
        db.query(customer.interactions)
        .order_by(customer.interactions.interaction_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Get opportunities
    opportunities = (
        db.query(customer.opportunities)
        .order_by(customer.opportunities.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Combine and sort history
    for item in interactions + opportunities:
        history_item = {
            "type": "interaction" if hasattr(item, "interaction_date") else "opportunity",
            "date": item.interaction_date if hasattr(item, "interaction_date") else item.created_at,
            "details": item
        }
        history.append(history_item)
    
    # Sort combined history by date
    history.sort(key=lambda x: x["date"], reverse=True)
    
    return history