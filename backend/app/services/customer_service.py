from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.customer_repository import CustomerRepository
from app.models import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.core.exceptions import NotFoundError, ValidationError

class CustomerService:
    def __init__(self, db: Session):
        self.repository = CustomerRepository(db)

    async def get(self, id: int) -> Customer:
        customer = self.repository.get(id)
        if not customer:
            raise NotFoundError("Customer", id)
        return customer

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        return self.repository.get_all(skip=skip, limit=limit)

    async def search(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Customer]:
        return self.repository.search(search_term, skip=skip, limit=limit)

    async def update(self, id: int, customer_data: CustomerUpdate) -> Customer:
        customer = self.repository.get(id)
        if not customer:
            raise NotFoundError("Customer", id)
        
        # Check email uniqueness if email is being updated
        if customer_data.email and customer_data.email != customer.email:
            existing_customer = self.repository.get_by_email(customer_data.email)
            if existing_customer:
                raise ValidationError("Email already registered")
        
        return self.repository.update(customer, customer_data)

    async def delete(self, id: int) -> bool:
        customer = self.repository.get(id)
        if not customer:
            raise NotFoundError("Customer", id)
        
        return self.repository.delete(customer)

    async def get_by_company(self, company: str) -> List[Customer]:
        return self.repository.get_by_company(company)