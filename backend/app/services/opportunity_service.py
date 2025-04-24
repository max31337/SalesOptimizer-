from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.opportunity_repository import OpportunityRepository
from app.models import Opportunity
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

    async def get_all(self, skip: int = 0, limit: int = 100, 
                     customer_id: Optional[int] = None) -> List[Opportunity]:
        if customer_id:
            return self.repository.get_by_customer(customer_id)
        return self.repository.get_all(skip=skip, limit=limit)

    async def create(self, opportunity_data: OpportunityCreate, user_id: int) -> Opportunity:
        # Convert to dict and add sales rep id
        opportunity_dict = opportunity_data.model_dump()  # Convert Pydantic model to dict first
        opportunity_dict['sales_rep_id'] = user_id
        return self.repository.create(opportunity_dict)  # Pass the dict directly

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

    async def get_all_for_sales_rep(self, sales_rep_id: int, skip: int = 0, limit: int = 100) -> List[Opportunity]:
        """Gets all opportunities for a specific sales representative."""
        # Note: The repository method is synchronous, but we keep the service async for consistency
        return self.repository.get_all_for_sales_rep(sales_rep_id=sales_rep_id, skip=skip, limit=limit)

    async def get_summary_for_sales_rep(self, sales_rep_id: int) -> OpportunitySummary:
        """Gets the opportunity summary metrics for a specific sales representative."""
        summary_data = self.repository.get_summary_for_sales_rep(sales_rep_id=sales_rep_id)
        # Wrap the dictionary result in the Pydantic model
        return OpportunitySummary(**summary_data)

    async def get_performance_data_for_sales_rep(self, sales_rep_id: int, months: int = 6) -> SalesPerformanceData:
        """Gets the sales performance data for the chart for a specific sales representative."""
        performance_data = self.repository.get_performance_data_for_sales_rep(sales_rep_id=sales_rep_id, months=months)
        # Wrap the dictionary result in the Pydantic model
        return SalesPerformanceData(**performance_data)
