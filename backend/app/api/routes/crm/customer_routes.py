from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models import User, Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerSchema
from app.api.routes.auth.user_check_routes import get_sales_rep  # Updated import
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])

# Update all other route dependencies similarly 
@router.get("/list/", response_model=List[CustomerSchema])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    segment: Optional[str] = None,
    industry: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)  # Updated dependency
):
    """List customers with search and filters"""
    customer_service = CustomerService(db)
    return await customer_service.get_all(skip=skip, limit=limit)

@router.get("/details/{customer_id}", response_model=CustomerSchema)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """Get customer details"""
    customer_service = CustomerService(db)
    return await customer_service.get(customer_id)

@router.put("/update/{customer_id}", response_model=CustomerSchema)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """Update customer details"""
    customer_service = CustomerService(db)
    return await customer_service.update(customer_id, customer_update)

@router.delete("/delete/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """Delete a customer"""
    customer_service = CustomerService(db)
    return await customer_service.delete(customer_id)