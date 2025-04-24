from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models import Opportunity, OpportunityStage # Import OpportunityStage
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate

class OpportunityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[Opportunity]:
        return self.db.query(Opportunity).filter(Opportunity.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Opportunity]:
        # This fetches all opportunities, might be needed for admin roles
        return self.db.query(Opportunity).offset(skip).limit(limit).all()

    def get_all_for_sales_rep(self, sales_rep_id: int, skip: int = 0, limit: int = 100) -> List[Opportunity]:
        """Fetches all opportunities assigned to a specific sales representative."""
        return self.db.query(Opportunity)\
            .filter(Opportunity.sales_rep_id == sales_rep_id)\
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

    def get_summary_for_sales_rep(self, sales_rep_id: int) -> Dict[str, Any]:
        """Calculates summary metrics for a specific sales representative."""
        active_stages = [
            OpportunityStage.PROSPECTING,
            OpportunityStage.QUALIFICATION,
            OpportunityStage.PROPOSAL,
            OpportunityStage.NEGOTIATION,
            OpportunityStage.CLOSED_WON, # Include won for win rate calculation
            OpportunityStage.CLOSED_LOST # Include lost for win rate calculation
        ]

        # Query for counts and sums based on stage
        summary_query = self.db.query(
            func.count(Opportunity.id).label("total_count"),
            func.sum(case((Opportunity.stage.in_([OpportunityStage.PROSPECTING, OpportunityStage.QUALIFICATION, OpportunityStage.PROPOSAL, OpportunityStage.NEGOTIATION]), Opportunity.deal_value), else_=0)).label("active_pipeline_value"),
            func.count(case((Opportunity.stage.in_([OpportunityStage.PROSPECTING, OpportunityStage.QUALIFICATION, OpportunityStage.PROPOSAL, OpportunityStage.NEGOTIATION]), Opportunity.id), else_=None)).label("active_count"),
            func.count(case((Opportunity.stage == OpportunityStage.CLOSED_WON, Opportunity.id), else_=None)).label("won_count"),
            func.count(case((Opportunity.stage == OpportunityStage.CLOSED_LOST, Opportunity.id), else_=None)).label("lost_count")
        ).filter(
            Opportunity.sales_rep_id == sales_rep_id,
            Opportunity.stage.in_(active_stages) # Consider only relevant stages
        ).first()

        if not summary_query:
            return {"active_count": 0, "total_value": 0.0, "win_rate": 0.0}

        active_count = summary_query.active_count or 0
        total_value = summary_query.active_pipeline_value or 0.0
        won_count = summary_query.won_count or 0
        lost_count = summary_query.lost_count or 0
        total_closed = won_count + lost_count

        win_rate = (won_count / total_closed) if total_closed > 0 else 0.0

        return {
            "active_count": active_count,
            "total_value": float(total_value), # Ensure float
            "win_rate": win_rate
        }

    def get_performance_data_for_sales_rep(self, sales_rep_id: int, months: int = 6) -> Dict[str, list]:
        """
        Fetches monthly sales performance data (value and count of won opportunities)
        for the specified sales representative over the last 'months'.
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30) # Approximate months

        # Query won opportunities grouped by month
        performance_query = self.db.query(
            extract('year', Opportunity.expected_close_date).label('year'),
            extract('month', Opportunity.expected_close_date).label('month'),
            func.sum(Opportunity.deal_value).label('monthly_value'),
            func.count(Opportunity.id).label('monthly_won_count')
        ).filter(
            Opportunity.sales_rep_id == sales_rep_id,
            Opportunity.stage == OpportunityStage.CLOSED_WON,
            Opportunity.expected_close_date >= start_date,
            Opportunity.expected_close_date <= end_date
        ).group_by(
            extract('year', Opportunity.expected_close_date),
            extract('month', Opportunity.expected_close_date)
        ).order_by(
            extract('year', Opportunity.expected_close_date),
            extract('month', Opportunity.expected_close_date)
        ).all()

        # Prepare data structure for the last 'months'
        performance_data = {}
        current_date = start_date
        while current_date <= end_date:
            month_label = current_date.strftime("%b %Y") # e.g., "Apr 2025"
            performance_data[month_label] = {"sales_value": 0.0, "opportunities_won": 0}
            # Move to the next month (approximation)
            next_month_day_one = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
            current_date = next_month_day_one


        # Populate with actual data
        for record in performance_query:
            # Construct the label based on year and month from the query result
            record_date = datetime(int(record.year), int(record.month), 1)
            month_label = record_date.strftime("%b %Y")
            if month_label in performance_data:
                performance_data[month_label]["sales_value"] = float(record.monthly_value or 0.0)
                performance_data[month_label]["opportunities_won"] = record.monthly_won_count or 0

        # Format for the final response schema
        labels = list(performance_data.keys())
        sales_values = [data["sales_value"] for data in performance_data.values()]
        opportunities_won = [data["opportunities_won"] for data in performance_data.values()]

        # Ensure the lists cover the requested number of months, even if no data exists
        # (The loop above already initializes all months in the range)

        return {
            "labels": labels,
            "salesValue": sales_values,
            "opportunitiesWon": opportunities_won
        }
