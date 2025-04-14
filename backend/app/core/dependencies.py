from fastapi import Depends
from typing import Callable, Iterator
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.interfaces.user_service import IUserService
from app.services.user_service import UserService

def get_user_service(db: Session = Depends(get_db)) -> IUserService:
    return UserService(db)

class ServiceProvider:
    def __init__(self):
        self._user_service: Callable[[], IUserService] = get_user_service

    def override_user_service(self, service: Callable[[], IUserService]):
        self._user_service = service

    def get_user_service(self) -> Callable[[], IUserService]:
        return self._user_service

service_provider = ServiceProvider()