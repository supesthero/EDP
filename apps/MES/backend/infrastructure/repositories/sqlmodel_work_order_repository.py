# infrastructure/repositories/sqlmodel_work_order_repository.py
import uuid
from typing import List, Optional
from sqlmodel import Session, select, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from domain.repositories.work_order_repository import AbstractWorkOrderRepository
# We will use SQLModel's WorkOrder directly for persistence and as a data carrier.
# The domain.entities.work_order.WorkOrder (Pydantic model) might become redundant or serve a different purpose
# if we fully embrace SQLModel for data representation in the app service.
# For now, let's assume the application service will work with SQLModel's WorkOrder.
from infrastructure.sqlmodels.work_order import WorkOrder, WorkOrderCreate, WorkOrderUpdate
from domain.value_objects.order_status import OrderStatus # Still needed for status logic
from datetime import datetime


class SQLModelWorkOrderRepository(AbstractWorkOrderRepository):
    """
    SQLModel implementation of the Work Order Repository.
    """
    def __init__(self, session: Session):
        self.session = session

    async def get_by_id(self, id: uuid.UUID) -> Optional[WorkOrder]:
        try:
            # SQLModel's select syntax
            statement = select(WorkOrder).where(WorkOrder.id == id)
            work_order = self.session.exec(statement).first()
            return work_order
        except SQLAlchemyError as e:
            print(f"Database error in get_by_id: {e}") # Replace with proper logging
            raise

    async def add(self, work_order_data: WorkOrder) -> WorkOrder:
        """
        Adds a new work order to the database.
        Expects a WorkOrder table model instance.
        """
        # The work_order_data should already be an instance of the SQLModel table class (WorkOrder)
        # with id, created_at, updated_at potentially being None or set by default_factory/DB.
        db_work_order = work_order_data # Assuming work_order_data is already a WorkOrder table instance
        try:
            self.session.add(db_work_order)
            self.session.commit()
            self.session.refresh(db_work_order) # To get DB-generated values
            return db_work_order
        except IntegrityError as e:
            self.session.rollback()
            print(f"Integrity error in add: {e.orig}")
            # Consider raising a more specific business exception
            raise ValueError(f"Could not add work order. Integrity constraint violated (e.g. duplicate order_number): {e.orig}")
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Database error in add: {e}")
            raise

    async def update(self, work_order_id: uuid.UUID, work_order_update_data: WorkOrderUpdate) -> Optional[WorkOrder]:
        """
        Updates an existing work order.
        work_order_update_data contains the fields to update.
        """
        try:
            db_work_order = self.session.get(WorkOrder, work_order_id) # SQLModel's get by PK
            if not db_work_order:
                return None

            update_data = work_order_update_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_work_order, key, value)
            
            # DB trigger should handle updated_at, no need to set it manually here
            # if it was set by the application service, it will be persisted.

            self.session.add(db_work_order) # Add to session to mark as dirty
            self.session.commit()
            self.session.refresh(db_work_order)
            return db_work_order
        except IntegrityError as e: # e.g. unique constraint violation for order_number if changed
            self.session.rollback()
            print(f"Integrity error in update: {e.orig}")
            raise ValueError(f"Could not update work order. Integrity constraint violated: {e.orig}")
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Database error in update: {e}")
            raise

    async def delete(self, id: uuid.UUID) -> bool:
        try:
            work_order = self.session.get(WorkOrder, id)
            if work_order:
                self.session.delete(work_order)
                self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Database error in delete: {e}")
            raise

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[WorkOrder]:
        try:
            statement = select(WorkOrder).offset(skip).limit(limit)
            work_orders = self.session.exec(statement).all()
            return work_orders
        except SQLAlchemyError as e:
            print(f"Database error in list_all: {e}")
            raise

    async def get_by_order_number(self, order_number: str) -> Optional[WorkOrder]:
        try:
            statement = select(WorkOrder).where(WorkOrder.order_number == order_number)
            work_order = self.session.exec(statement).first()
            return work_order
        except SQLAlchemyError as e:
            print(f"Database error in get_by_order_number: {e}")
            raise

    async def count_all(self) -> int:
        try:
            # Using func.count with SQLModel
            # The argument to func.count should be a column. WorkOrder.id is a good choice.
            statement = select(func.count(WorkOrder.id))
            count = self.session.exec(statement).one() # .one() because count always returns one row
            return count
        except SQLAlchemyError as e:
            print(f"Database error in count_all: {e}")
            raise
