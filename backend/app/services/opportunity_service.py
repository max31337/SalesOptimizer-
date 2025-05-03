from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.opportunity_repository import OpportunityRepository
from app.models import Opportunity
from app.models import User
# Import the new schemas
from app.schemas.opportunity import (
    OpportunityCreate, OpportunityUpdate, OpportunitySummary, SalesPerformanceData
)
from app.core.exceptions import NotFoundError, ValidationError

class OpportunityService:
    def __init__(self, db: Session):
        self.repository = OpportunityRepository(db)

    async def get(self, id: int) -> Opportunity:
        opportunity = self.repository.get(id)
        if not opportunity:
            raise NotFoundError("Opportunity", id)
        return opportunity


    async def update(self, id: int, opportunity_data: OpportunityUpdate) -> Opportunity:
        opportunity = self.repository.get(id)
        if not opportunity:
            raise NotFoundError("Opportunity", id)
        return self.repository.update(opportunity, opportunity_data)

    async def delete(self, id: int) -> bool:
        opportunity = self.repository.get(id)
        if not opportunity:
            raise NotFoundError("Opportunity", id)
        return self.repository.delete(opportunity)

    async def get_by_stage(self, stage: str) -> List[Opportunity]:
        return self.repository.get_by_stage(stage)

    async def update_stage(self, id: int, stage: str) -> Opportunity:
        opportunity = self.repository.get(id)
        if not opportunity:
            raise NotFoundError("Opportunity", id)
        return self.repository.update_stage(opportunity, stage)

    async def create(self, opportunity_data: OpportunityCreate) -> Opportunity:
        opportunity = self.repository.create(opportunity_data)
        return self.repository.update(opportunity, update_data)
