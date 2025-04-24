from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.interaction_repository import InteractionRepository
from app.models import Interaction
from app.schemas.interaction import InteractionCreate, InteractionUpdate
from app.core.exceptions import NotFoundError, ValidationError

class InteractionService:
    def __init__(self, db: Session):
        self.repository = InteractionRepository(db)

    async def get(self, id: int) -> Interaction:
        interaction = self.repository.get(id)
        if not interaction:
            raise NotFoundError("Interaction", id)
        return interaction

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Interaction]:
        return self.repository.get_all(skip=skip, limit=limit)

    async def get_by_customer(self, customer_id: int) -> List[Interaction]:
        return self.repository.get_by_customer(customer_id)

    async def create(self, interaction_data: InteractionCreate, user_id: int) -> Interaction:
        interaction_dict = interaction_data.model_dump()
        interaction_dict['sales_rep_id'] = user_id  # Changed from created_by to sales_rep_id
        return self.repository.create(interaction_dict)

    async def update(self, id: int, interaction_data: InteractionUpdate) -> Interaction:
        interaction = self.repository.get(id)
        if not interaction:
            raise NotFoundError("Interaction", id)
        return self.repository.update(interaction, interaction_data)

    async def delete(self, id: int) -> bool:
        interaction = self.repository.get(id)
        if not interaction:
            raise NotFoundError("Interaction", id)
        return self.repository.delete(interaction)