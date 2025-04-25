from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models import Opportunity, User
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate
from app.models.enums import OpportunityStageGroup, OpportunityStage

class OpportunityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[Opportunity]:
        return self.db.query(Opportunity).filter(Opportunity.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Opportunity]:
        # This fetches all opportunities, might be needed for admin roles
        return self.db.query(Opportunity).offset(skip).limit(limit).all()

    def get_all_for_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Opportunity]:
        """Fetches all opportunities assigned to a specific user (could be sales rep, or any user)."""
        return self.db.query(Opportunity)\
            .filter(Opportunity.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_by_customer(self, customer_id: int) -> List[Opportunity]:
        return self.db.query(Opportunity).filter(Opportunity.customer_id == customer_id).all()

    def get_by_stage(self, stage: str) -> List[Opportunity]:
        return self.db.query(Opportunity).filter(Opportunity.stage == stage).all()

    def create(self, opportunity_data: dict) -> Opportunity:
        opportunity = Opportunity(**opportunity_data)  # Use dict directly
        self.db.add(opportunity)
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity

    def update(self, opportunity: Opportunity, opportunity_data: OpportunityUpdate) -> Opportunity:
        for key, value in opportunity_data.model_dump(exclude_unset=True).items():
            setattr(opportunity, key, value)
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity

    def update_stage(self, opportunity: Opportunity, stage: str) -> Opportunity:
        opportunity.stage = stage
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity

    def delete(self, opportunity: Opportunity) -> bool:
        self.db.delete(opportunity)
        self.db.commit()
        return True

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