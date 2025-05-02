from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.salesrep_repository import SalesRepRepository
from app.models import User, Opportunity, Customer, Interaction
from app.schemas import OpportunityCreate, OpportunityUpdate, CustomerCreate, CustomerUpdate, InteractionCreate, InteractionUpdate

class SalesRepService:
    def __init__(self, db: Session):
        self.repository = SalesRepRepository(db)
            
    def get_summary_for_sales_rep(self, current_user: User) -> Dict[str, Any]:
        """Gets the summary (active count, total value, win rate) for a specific sales representative."""
        return self.repository.get_summary_for_user(current_user.id)

    def get_monthly_summary_for_sales_rep(self, current_user: User) -> Dict[str, Any]:
        """Gets the monthly sales summary for a specific sales representative."""
        return self.repository.get_monthly_summary(current_user.id)

    def get_monthly_opportunities_for_sales_rep(self, current_user: User) -> List[Opportunity]:
        """Gets all opportunities for the current month for a specific sales representative."""
        return self.repository.get_monthly_opportunities(current_user.id)

    def get_pipeline_stages_distribution(self, current_user: User) -> Dict[str, Any]:
        """Gets the distribution of opportunities across pipeline stages with counts and values."""
        return self.repository.get_pipeline_stages_distribution(current_user.id)

    def get_win_loss_summary_for_sales_rep(self, current_user: User) -> Dict[str, int]:
        """Get win/loss count for doughnut chart."""
        return self.repository.get_win_loss_summary(current_user.id)

#Opportunities
    def get_all_opportunities(self, current_user: User, skip: int = 0, limit: int = 100) -> List[Opportunity]:
        """Gets all opportunities for a specific sales representative."""
        return self.repository.get_all_opportunities(current_user.id, skip=skip, limit=limit)

    def get_all_customers(self, current_user: User, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Gets all customers assigned to the current sales representative."""
        return self.repository.get_all_customers(current_user.id, skip=skip, limit=limit)

    def get_all_interactions(self, current_user: User, skip: int = 0, limit: int = 100) -> List[Interaction]:
        """Gets all interactions for a specific sales representative."""
        return self.repository.get_all_interactions(current_user.id, skip=skip, limit=limit)

    async def create_opportunity(self, opportunity_data: OpportunityCreate, user_id: int) -> Opportunity:
        # Convert to dict and add sales rep id
        opportunity_dict = opportunity_data.model_dump()  # Convert Pydantic model to dict first
        opportunity_dict['sales_rep_id'] = user_id
        return self.repository.create_opportunity(opportunity_dict)
        
    async def create_customer(self, customer_data: CustomerCreate, assigned_to: int) -> Customer:
        # Convert to dict and add assigned_to
        customer_dict = customer_data.model_dump()
        customer_dict['assigned_to'] = assigned_to
        return self.repository.create_customer(customer_data, assigned_to)

    async def create_interaction(self, interaction_data: InteractionCreate, user_id: int) -> Interaction:
        interaction_dict = interaction_data.model_dump(exclude={'customer_name'})  # Exclude customer_name
        interaction_dict['sales_rep_id'] = user_id  

        if 'follow_up_tasks' in interaction_dict:
            interaction_dict['follow_up_task'] = json.dumps(interaction_dict.pop('follow_up_tasks'))
        return self.repository.create_interaction(interaction_dict)