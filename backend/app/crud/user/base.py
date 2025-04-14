from sqlalchemy.orm import Session
from app.models import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def commit_and_refresh(self, instance):
        self.db.commit()
        self.db.refresh(instance)
        return instance