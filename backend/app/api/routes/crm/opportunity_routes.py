from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models import User, Opportunity
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate, OpportunitySummary, Opportunity as OpportunitySchema
from app.api.routes.auth.user_check_routes import get_sales_rep
from app.services.opportunity_service import OpportunityService

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.get("/details/{opportunity_id}", response_model=OpportunitySchema)
async def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """Get opportunity details"""
    opportunity_service = OpportunityService(db)
    return await opportunity_service.get(opportunity_id)

@router.put("/update/{opportunity_id}", response_model=OpportunitySchema)
async def update_opportunity(
    opportunity_id: int,
    opportunity_update: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """Update opportunity details"""
    opportunity_service = OpportunityService(db)
    return await opportunity_service.update(opportunity_id, opportunity_update)

@router.delete("/delete/{opportunity_id}")
async def delete_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """Delete an opportunity"""
    opportunity_service = OpportunityService(db)
    return await opportunity_service.delete(opportunity_id)
