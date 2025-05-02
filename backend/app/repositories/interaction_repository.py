from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional 
from datetime import datetime
from app.models import Interaction
from app.schemas.interaction import InteractionCreate, InteractionUpdate


class InteractionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[Interaction]:
        return self.db.query(Interaction).filter(Interaction.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Interaction]:
        return self.db.query(Interaction).offset(skip).limit(limit).all()

    def get_by_customer(self, customer_id: int) -> List[Interaction]:
        return self.db.query(Interaction).filter(Interaction.customer_id == customer_id).all()

    def update(self, interaction: Interaction, interaction_data: InteractionUpdate) -> Interaction:
        for key, value in interaction_data.model_dump(exclude_unset=True).items():
            setattr(interaction, key, value)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def delete(self, interaction: Interaction) -> bool:
        self.db.delete(interaction)
        self.db.commit()
        return True

    def get_by_type(self, interaction_type: str) -> List[Interaction]:
        return self.db.query(Interaction).filter(Interaction.type == interaction_type).all()

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Interaction]:
        return self.db.query(Interaction).filter(
            Interaction.created_at.between(start_date, end_date)
        ).all()