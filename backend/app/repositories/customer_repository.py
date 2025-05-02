from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        return self.db.query(Customer).offset(skip).limit(limit).all()

    def search(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Customer]:
        return self.db.query(Customer).filter(
            or_(
                Customer.name.ilike(f"%{search_term}%"),
                Customer.company.ilike(f"%{search_term}%"),
                Customer.email.ilike(f"%{search_term}%")
            )
        ).offset(skip).limit(limit).all()

    def create(self, customer_data: CustomerCreate, assigned_to: int) -> Customer:
        customer_dict = customer_data.dict()
        customer_dict['assigned_to'] = assigned_to
        customer = Customer(**customer_dict)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update(self, customer: Customer, customer_data: CustomerUpdate) -> Customer:
        for key, value in customer_data.dict(exclude_unset=True).items():
            setattr(customer, key, value)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete(self, customer: Customer) -> bool:
        self.db.delete(customer)
        self.db.commit()
        return True

    def get_by_email(self, email: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.email == email).first()

    def get_by_company(self, company: str) -> List[Customer]:
        return self.db.query(Customer).filter(Customer.company == company).all()