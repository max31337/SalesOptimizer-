from app.core.exceptions import NotFoundError, ValidationError, DatabaseError
from app.db.unit_of_work import UnitOfWork
from sqlalchemy.orm import Session
from app.crud.user_repository import UserRepository 
from app.db.database import get_db
from app.utils.security import get_password_hash
from app.models import User
from typing import Optional, Dict, List
from abc import ABC, abstractmethod
from app.schemas import UserCreate, UserUpdate

class IUserService(ABC):
    @abstractmethod
    def create_user(self, user_data: UserCreate):
        pass
    
    @abstractmethod 
    def update_user(self, user_id: int, user_data: UserUpdate):
        pass

class UserService(IUserService):
    def __init__(self, db: Session):
        self.db = db
        # Fix: Pass a lambda function that returns the db session
        self.uow = UnitOfWork(lambda: db)  # Changed from self.db to lambda: db

    def create_user(self, user_data: UserCreate) -> User:
        with self.uow.start() as session:
            repo = UserRepository(session)
            
            if repo.get_by_email(user_data.email):
                raise ValidationError("Email already registered")
            
            try:
                # Create user with hashed password
                user = User(
                    email=user_data.email,
                    name=user_data.name,
                    username=user_data.email,  # Set username to email by default
                    password=get_password_hash(user_data.password),
                    role=user_data.role,
                    is_active=False
                )
                
                session.add(user)
                session.commit()
                session.refresh(user)
                
                return user
            except Exception as e:
                raise DatabaseError(f"Failed to create user: {str(e)}")

    async def get(self, id: int) -> Optional[User]:
        with self.uow.start() as session:
            repo = UserRepository(session)
            user = repo.get(id)
            if not user:
                raise NotFoundError("User", id)
            return user

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        with self.uow.start() as session:
            repo = UserRepository(session)
            return repo.get_all(skip=skip, limit=limit)

    async def get_by_email(self, email: str) -> Optional[User]:
        with self.uow.start() as session:
            repo = UserRepository(session)
            return repo.get_by_email(email)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        with self.uow.start() as session:
            repo = UserRepository(session)
            user = repo.get(user_id)
            
            if not user:
                raise NotFoundError("User", user_id)
            
            try:
                return repo.update_with_hash(user, user_data)
            except Exception as e:
                raise DatabaseError(f"Failed to update user: {str(e)}")

    async def delete_user(self, user_id: int) -> Dict[str, str]:
        with self.uow.start() as session:
            repo = UserRepository(session)
            try:
                repo.delete(user_id)
                return {"message": "User deleted successfully"}
            except NotFoundError:
                raise
            except Exception as e:
                raise DatabaseError(f"Failed to delete user: {str(e)}")

    async def verify_user(self, user_id: int) -> User:
        with self.uow.start() as session:
            repo = UserRepository(session)
            user = repo.get(user_id)
            if not user:
                raise NotFoundError("User", user_id)
            user.is_verified = True
            user.verification_token = None
            return user