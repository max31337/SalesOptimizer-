from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models import Opportunity
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate

class OpportunityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[Opportunity]:
        return self.db.query(Opportunity).filter(Opportunity.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Opportunity]:
        return self.db.query(Opportunity).offset(skip).limit(limit).all()

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