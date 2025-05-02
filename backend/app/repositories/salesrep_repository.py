from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models import Opportunity, User, Interaction, Customer
from app.models.enums import OpportunityStageGroup, OpportunityStage
from app.schemas.interaction import InteractionBase, InteractionCreate, InteractionUpdate, InteractionType, InteractionResponse
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate
from app.schemas.customer import CustomerCreate, CustomerUpdate
from fastapi import HTTPException

class SalesRepRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == id).first()
        
    def get_summary_for_user(self, user_id: int) -> Dict[str, Any]:
        """
        Returns a summary of opportunities for a given user:
        - Total value and count of active opportunities
        - Win rate: closed_won / (closed_won + closed_lost)
        """

        # Get active opportunities (lead, prospect, negotiation)
        active_query = self.db.query(Opportunity).filter(
            Opportunity.sales_rep_id == user_id,
            Opportunity.stage.in_(OpportunityStageGroup.ACTIVE)
        )

        active_opportunities = active_query.all()
        total_active_value = sum(opp.deal_value for opp in active_opportunities)
        active_count = len(active_opportunities)

        # Get count of closed opportunities
        closed_query = self.db.query(Opportunity.stage).filter(
            Opportunity.sales_rep_id == user_id,
            Opportunity.stage.in_([stage.value for stage in OpportunityStageGroup.CLOSED])
        )

        total_closed = closed_query.count()

        # Get count of closed_won only
        total_won = self.db.query(Opportunity).filter(
            Opportunity.sales_rep_id == user_id,
            Opportunity.stage == OpportunityStage.CLOSED_WON.value
        ).count()

        win_rate = total_won / total_closed if total_closed > 0 else 0.0

        return {
            "active_count": active_count,
            "total_value": total_active_value,
            "win_rate": win_rate
        }

    def get_monthly_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Returns a monthly summary of sales for a given user:
        - Total sales value for the month
        - Number of deals closed
        - Average deal size
        """
        current_date = datetime.now()
        first_day = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Get monthly closed won opportunities
        monthly_sales = self.db.query(
            func.count(Opportunity.id).label('deal_count'),
            func.sum(Opportunity.deal_value).label('total_value')
        ).filter(
            Opportunity.sales_rep_id == user_id,
            Opportunity.stage == OpportunityStage.CLOSED_WON.value,
            Opportunity.closed_date >= first_day
        ).first()

        deal_count = monthly_sales.deal_count or 0
        total_value = monthly_sales.total_value or 0
        avg_deal_size = total_value / deal_count if deal_count > 0 else 0

        return {
            "monthly_deals": deal_count,
            "monthly_value": total_value,
            "average_deal_size": avg_deal_size
        }

    def get_monthly_opportunities(self, user_id: int) -> List[Opportunity]:
        """
        Returns all opportunities for the current month for a given user
        """
        current_date = datetime.now()
        first_day = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Get all opportunities for the current month
        monthly_opportunities = self.db.query(Opportunity).filter(
            Opportunity.sales_rep_id == user_id,
            Opportunity.created_at >= first_day
        ).all()

        return monthly_opportunities

    def get_pipeline_stages_distribution(self, user_id: int) -> Dict[str, Any]:
        """
        Returns the distribution of opportunities across pipeline stages:
        - Count and total value for each stage
        """
        # Query opportunities for each stage
        lead_opps = self.db.query(Opportunity).filter(
            Opportunity.sales_rep_id == user_id,
            Opportunity.stage == OpportunityStage.LEAD.value
        ).all()
        
        prospect_opps = self.db.query(Opportunity).filter(
            Opportunity.sales_rep_id == user_id,
            Opportunity.stage == OpportunityStage.PROSPECT.value
        ).all()
        
        negotiation_opps = self.db.query(Opportunity).filter(
            Opportunity.sales_rep_id == user_id,
            Opportunity.stage == OpportunityStage.NEGOTIATION.value
        ).all()
        
        won_opps = self.db.query(Opportunity).filter(
            Opportunity.sales_rep_id == user_id,
            Opportunity.stage == OpportunityStage.CLOSED_WON.value
        ).all()
        
        lost_opps = self.db.query(Opportunity).filter(
            Opportunity.sales_rep_id == user_id,
            Opportunity.stage == OpportunityStage.CLOSED_LOST.value
        ).all()

        return {
            "lead_count": len(lead_opps),
            "lead_value": sum(opp.deal_value for opp in lead_opps),
            "prospect_count": len(prospect_opps),
            "prospect_value": sum(opp.deal_value for opp in prospect_opps),
            "negotiation_count": len(negotiation_opps),
            "negotiation_value": sum(opp.deal_value for opp in negotiation_opps),
            "won_count": len(won_opps),
            "won_value": sum(opp.deal_value for opp in won_opps),
            "lost_count": len(lost_opps),
            "lost_value": sum(opp.deal_value for opp in lost_opps)
        }

    def get_win_loss_summary(self, user_id: int) -> Dict[str, int]:
        won_count = self.db.query(Opportunity).filter(
        Opportunity.sales_rep_id == user_id,
        Opportunity.stage == OpportunityStage.CLOSED_WON.value
        ).count()

        lost_count = self.db.query(Opportunity).filter(
        Opportunity.sales_rep_id == user_id,
        Opportunity.stage == OpportunityStage.CLOSED_LOST.value
        ).count()

        return {
        "won_opportunities": won_count,
        "lost_opportunities": lost_count
        }


    def get_all_opportunities(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Opportunity]:
        """Get all opportunities for a specific sales representative with customer names"""
        opportunities = self.db.query(Opportunity).join(
            Customer,
            Opportunity.customer_id == Customer.id
        ).add_columns(
            Customer.name.label('customer_name')
        ).filter(
            Opportunity.sales_rep_id == user_id
        ).offset(skip).limit(limit).all()
        
        # Attach customer name to opportunity object using the new setter
        result = []
        for opp, customer_name in opportunities:
            opp.customer_name = customer_name
            result.append(opp)
        
        return result

    def get_all_customers(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Get all customers assigned to the current sales representative"""
        return self.db.query(Customer).filter(
            Customer.assigned_to == user_id
        ).offset(skip).limit(limit).all()

    def get_all_interactions(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Interaction]:
        """Get all interactions for a specific sales representative with customer names"""
        interactions = self.db.query(Interaction).join(
            Customer,
            Interaction.customer_id == Customer.id
        ).add_columns(
            Customer.name.label('customer_name')
        ).filter(
            Interaction.sales_rep_id == user_id
        ).offset(skip).limit(limit).all()
        
        # Attach customer name to interaction object
        result = []
        for interaction, customer_name in interactions:
            interaction.customer_name = customer_name
            result.append(interaction)
        
        return result


    def create_opportunity(self, opportunity_data: dict) -> Opportunity:
        opportunity = Opportunity(**opportunity_data) 
        self.db.add(opportunity)
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity

    def get_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email"""
        return self.db.query(Customer).filter(Customer.email == email).first()

    def create_customer(self, customer_data: CustomerCreate, assigned_to: int) -> Customer:
        # First check if email already exists
        existing_customer = self.get_by_email(customer_data.email)
        if existing_customer:
            raise HTTPException(status_code=400, detail="Email already in use")
            
        customer_dict = customer_data.model_dump()
        customer_dict['assigned_to'] = assigned_to
        customer = Customer(**customer_dict)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def create_interaction(self, interaction_data: dict) -> Interaction:
        interaction = Interaction(**interaction_data)
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction
