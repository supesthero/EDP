# application/services/work_order_app_service.py
import uuid
from typing import List, Optional
from datetime import datetime

from domain.repositories.work_order_repository import AbstractWorkOrderRepository
from domain.value_objects.order_status import OrderStatus
# Import SQLModel classes; these will be the primary data carriers now
from infrastructure.sqlmodels.work_order import WorkOrder, WorkOrderCreate, WorkOrderUpdate


class WorkOrderApplicationService:
    def __init__(self, work_order_repo: AbstractWorkOrderRepository):
        self.work_order_repo = work_order_repo

    async def create_work_order_sqlmodel(self, wo_create_data: WorkOrderCreate) -> WorkOrder:
        """
        Creates a new work order using SQLModel.
        wo_create_data is an instance of WorkOrderCreate.
        Returns the persisted WorkOrder table model.
        """
        existing_wo = await self.work_order_repo.get_by_order_number(wo_create_data.order_number)
        if existing_wo:
            raise ValueError(f"Work order with number '{wo_create_data.order_number}' already exists.")

        # Convert WorkOrderCreate to WorkOrder (table model)
        # SQLModel makes this easy if WorkOrderCreate contains all necessary fields
        # or if WorkOrder has appropriate defaults (like id, created_at, updated_at).
        
        # The WorkOrder model has default_factory for id, and DB defaults for created_at/updated_at.
        # So, we can directly create a WorkOrder instance from WorkOrderCreate.
        # SQLModel's .model_validate should work if WorkOrderCreate is a compatible subset.
        # Or, more explicitly:
        new_work_order_table_instance = WorkOrder.model_validate(wo_create_data)
        # new_work_order_table_instance.id = uuid.uuid4() # If not using default_factory in model
        # created_at and updated_at will be handled by the database as per Alembic migration.

        return await self.work_order_repo.add(new_work_order_table_instance)

    async def get_work_order_by_id(self, wo_id: uuid.UUID) -> Optional[WorkOrder]:
        """Returns a WorkOrder table model instance."""
        return await self.work_order_repo.get_by_id(wo_id)

    async def get_all_work_orders(self, skip: int = 0, limit: int = 100) -> List[WorkOrder]:
        """Returns a list of WorkOrder table model instances."""
        return await self.work_order_repo.list_all(skip=skip, limit=limit)

    async def update_work_order_sqlmodel(
        self,
        wo_id: uuid.UUID,
        wo_update_data: WorkOrderUpdate
    ) -> Optional[WorkOrder]:
        """
        Updates a work order using SQLModel.
        wo_update_data is an instance of WorkOrderUpdate.
        Returns the updated WorkOrder table model instance.
        """
        # The repository's update method now handles applying WorkOrderUpdate to the fetched WorkOrder
        
        # Business logic before update (e.g., status change validation) can be here:
        current_wo = await self.work_order_repo.get_by_id(wo_id)
        if not current_wo:
            return None # Or raise not found

        if wo_update_data.status is not None:
            # Example of domain logic:
            if current_wo.status == OrderStatus.COMPLETED and wo_update_data.status != OrderStatus.COMPLETED:
                raise ValueError("Cannot change status of a completed order via this generic update. Use a specific operation.")
            if current_wo.status == OrderStatus.CANCELLED and wo_update_data.status != OrderStatus.CANCELLED:
                raise ValueError("Cannot change status of a cancelled order.")
        
        if wo_update_data.order_number and wo_update_data.order_number != current_wo.order_number:
            existing_wo_with_new_number = await self.work_order_repo.get_by_order_number(wo_update_data.order_number)
            if existing_wo_with_new_number and existing_wo_with_new_number.id != wo_id:
                 raise ValueError(f"Work order with number '{wo_update_data.order_number}' already exists.")


        # The repository update method now takes wo_id and WorkOrderUpdate
        return await self.work_order_repo.update(wo_id, wo_update_data)


    async def delete_work_order(self, wo_id: uuid.UUID) -> bool:
        """Deletes a work order. Returns True if successful."""
        # Add business logic if needed, e.g., check status before deletion
        work_order_to_delete = await self.work_order_repo.get_by_id(wo_id)
        if work_order_to_delete and work_order_to_delete.status == OrderStatus.IN_PROGRESS:
            raise ValueError("Cannot delete a work order that is currently in progress.")
        
        return await self.work_order_repo.delete(wo_id)

    async def count_work_orders(self) -> int:
        """Counts all work orders."""
        return await self.work_order_repo.count_all()

