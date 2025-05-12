# application/services/work_order_app_service.py
import uuid
from typing import List, Optional
from datetime import datetime

from domain.entities.work_order import WorkOrder
from domain.repositories.work_order_repository import AbstractWorkOrderRepository
from domain.value_objects.order_status import OrderStatus
from api.schemas import work_order_schemas # 使用相对导入可能更好，或者配置PYTHONPATH

class WorkOrderApplicationService:
    def __init__(self, work_order_repo: AbstractWorkOrderRepository):
        self.work_order_repo = work_order_repo

    async def create_work_order(self, wo_create_data: work_order_schemas.WorkOrderCreateRequest) -> WorkOrder:
        # 检查工单号是否已存在 (业务规则可以在应用层或领域服务中)
        existing_wo = await self.work_order_repo.get_by_order_number(wo_create_data.order_number)
        if existing_wo:
            raise ValueError(f"Work order with number '{wo_create_data.order_number}' already exists.")

        work_order = WorkOrder(
            order_number=wo_create_data.order_number,
            product_name=wo_create_data.product_name,
            quantity=wo_create_data.quantity,
            due_date=wo_create_data.due_date,
            notes=wo_create_data.notes,
            status=wo_create_data.status if wo_create_data.status else OrderStatus.PENDING
        )
        return await self.work_order_repo.add(work_order)

    async def get_work_order_by_id(self, wo_id: uuid.UUID) -> Optional[WorkOrder]:
        return await self.work_order_repo.get_by_id(wo_id)

    async def get_all_work_orders(self, skip: int = 0, limit: int = 100) -> List[WorkOrder]:
        return await self.work_order_repo.list_all(skip=skip, limit=limit)

    async def update_work_order(
        self,
        wo_id: uuid.UUID,
        wo_update_data: work_order_schemas.WorkOrderUpdateRequest
    ) -> Optional[WorkOrder]:
        work_order = await self.work_order_repo.get_by_id(wo_id)
        if not work_order:
            return None

        update_data = wo_update_data.model_dump(exclude_unset=True) # Pydantic v2

        if "order_number" in update_data and update_data["order_number"] != work_order.order_number:
             # 如果允许修改工单号，需要检查新工单号是否唯一
            existing_wo = await self.work_order_repo.get_by_order_number(update_data["order_number"])
            if existing_wo and existing_wo.id != wo_id:
                raise ValueError(f"Work order with number '{update_data['order_number']}' already exists.")
            work_order.order_number = update_data["order_number"]

        # 使用实体的方法来更新，以封装领域逻辑
        work_order.update_details(
            product_name=update_data.get("product_name"),
            quantity=update_data.get("quantity"),
            due_date=update_data.get("due_date"),
            notes=update_data.get("notes")
        )

        if "status" in update_data:
            work_order.update_status(OrderStatus(update_data["status"]))

        work_order.updated_at = datetime.utcnow()
        return await self.work_order_repo.update(work_order)

    async def delete_work_order(self, wo_id: uuid.UUID) -> bool:
        # 可在此处添加业务规则，例如不允许删除正在进行的工单
        wo = await self.work_order_repo.get_by_id(wo_id)
        if wo and wo.status == OrderStatus.IN_PROGRESS:
            raise ValueError("Cannot delete a work order that is in progress.")
        return await self.work_order_repo.delete(wo_id)

    async def count_work_orders(self) -> int:
        # 实际场景中，仓储接口可能需要一个 count() 方法
        items = await self.work_order_repo.list_all(limit=0) # 临时方案获取数量
        return len(await self.work_order_repo.list_all(limit=1000000)) # 不推荐，应有专用count方法