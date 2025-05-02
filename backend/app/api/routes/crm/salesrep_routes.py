from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models import User, Opportunity, Customer
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate, OpportunitySummary, Opportunity as OpportunitySchema
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerSchema
from app.schemas.interaction import InteractionBase, InteractionCreate, InteractionType, InteractionUpdate, InteractionResponse as InteractionSchema
from app.api.routes.auth.user_check_routes import get_sales_rep
from app.services.salesrep_service import SalesRepService


router = APIRouter(tags=["Sales Representative"])

#For Overview Section
@router.get("/summary/", response_model=OpportunitySummary)
async def get_opportunity_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    service = SalesRepService(db)
    summary = service.get_summary_for_sales_rep(current_user)
    return OpportunitySummary(**summary)

@router.get("/monthly-summary/")
async def get_monthly_sales_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """Get monthly sales summary for the current sales representative"""
    service = SalesRepService(db)
    return service.get_monthly_summary_for_sales_rep(current_user)

@router.get("/monthly-opportunities/", response_model=List[OpportunitySchema])
async def get_monthly_opportunities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """Get all opportunities for the current month for the current sales representative"""
    service = SalesRepService(db)
    return service.get_monthly_opportunities_for_sales_rep(current_user)

@router.get("/pipeline-stages/")
async def get_pipeline_stages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """Get pipeline stages distribution with counts and values"""
    service = SalesRepService(db)
    return service.get_pipeline_stages_distribution(current_user)

@router.get("/win-loss/")
async def get_win_loss_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """Returns count of won and lost opportunities for win/loss chart."""
    service = SalesRepService(db)
    return service.get_win_loss_summary_for_sales_rep(current_user)


#Opportunities Section
@router.get("/opportunity-list/", response_model=List[OpportunitySchema])
async def list_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """List all opportunities for the current sales representative"""
    service = SalesRepService(db)
    return service.get_all_opportunities(current_user, skip=skip, limit=limit)

@router.get("/customer-list/", response_model=List[CustomerSchema])  # Make sure this route uses CustomerSchema
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """List all customers assigned to the current sales representative"""
    service = SalesRepService(db)
    return service.get_all_customers(current_user, skip=skip, limit=limit)

@router.get("/interaction-list/", response_model=List[InteractionSchema])
async def list_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """List all interactions for the current sales representative"""
    service = SalesRepService(db)
    return service.get_all_interactions(current_user, skip=skip, limit=limit)


@router.post("/opportunity-create/", response_model=OpportunitySchema)
async def create_opportunity(
    opportunity: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """Create a new opportunity"""
    service = SalesRepService(db)  
    return await service.create_opportunity(opportunity, current_user.id)
    
@router.post("/customer-create/", response_model=CustomerSchema)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """Create a new customer"""
    service = SalesRepService(db)
    return await service.create_customer(customer, assigned_to=current_user.id)
    
@router.post("/interaction-create/", response_model=InteractionSchema)
async def create_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sales_rep)
):
    """Create a new interaction"""
    service = SalesRepService(db)
    return await service.create_interaction(interaction, current_user.id)
