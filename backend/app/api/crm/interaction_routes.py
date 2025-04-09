from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.db.database import get_db
from app.models import Interaction, Customer, User
from app.schemas.interaction import InteractionCreate, InteractionUpdate, Interaction as InteractionSchema
from app.api.auth.auth import get_current_user

router = APIRouter()

@router.post("/interactions/", response_model=InteractionSchema)
async def create_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new interaction"""
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == interaction.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check authorization
    if current_user.role != "admin" and customer.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to create interaction for this customer")
    
    db_interaction = Interaction(**interaction.dict())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

@router.put("/interactions/{interaction_id}", response_model=InteractionSchema)
async def update_interaction(
    interaction_id: int,
    interaction_update: InteractionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an interaction"""
    db_interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    # Check authorization
    if current_user.role != "admin" and db_interaction.sales_rep_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this interaction")
    
    for field, value in interaction_update.dict(exclude_unset=True).items():
        setattr(db_interaction, field, value)
    
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

@router.delete("/interactions/{interaction_id}")
async def delete_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an interaction"""
    db_interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    # Check authorization
    if current_user.role != "admin" and db_interaction.sales_rep_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this interaction")
    
    db.delete(db_interaction)
    db.commit()
    return {"message": "Interaction deleted successfully"}

@router.get("/interactions/", response_model=List[InteractionSchema])
async def get_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    customer_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get interaction history"""
    query = db.query(Interaction)
    
    if customer_id:
        # If customer_id is provided, check authorization
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        if current_user.role != "admin" and customer.assigned_to != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this customer's interactions")
        
        query = query.filter(Interaction.customer_id == customer_id)
    elif current_user.role != "admin":
        # If not admin, only show interactions where user is the sales rep
        query = query.filter(Interaction.sales_rep_id == current_user.id)
    
    return query.order_by(Interaction.interaction_date.desc()).offset(skip).limit(limit).all()