# infrastructure/repositories/in_memory_work_order_repository.py
import uuid
from typing import List, Optional, Dict
from domain.entities.work_order import WorkOrder
from domain.repositories.work_order_repository import AbstractWorkOrderRepository

class InMemoryWorkOrderRepository(AbstractWorkOrderRepository):
    """
    工单仓储的内存实现 (用于测试和简单场景)
    """
    _work_orders: Dict[uuid.UUID, WorkOrder]

    def __init__(self):
        self._work_orders = {}

    async def get_by_id(self, id: uuid.UUID) -> Optional[WorkOrder]:
        return self._work_orders.get(id)

    async def add(self, work_order: WorkOrder) -> WorkOrder:
        if work_order.id in self._work_orders:
            raise ValueError(f"WorkOrder with id {work_order.id} already exists.")
        # 模拟数据库行为，返回的是对象的副本或新对象
        new_order = work_order.model_copy(deep=True)
        self._work_orders[new_order.id] = new_order
        return new_order

    async def update(self, work_order: WorkOrder) -> Optional[WorkOrder]:
        if work_order.id not in self._work_orders:
            return None
        # 模拟数据库行为
        updated_order = work_order.model_copy(deep=True)
        self._work_orders[updated_order.id] = updated_order
        return updated_order

    async def delete(self, id: uuid.UUID) -> bool:
        if id in self._work_orders:
            del self._work_orders[id]
            return True
        return False

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[WorkOrder]:
        all_orders = list(self._work_orders.values())
        return [order.model_copy(deep=True) for order in all_orders[skip : skip + limit]]

    async def get_by_order_number(self, order_number: str) -> Optional[WorkOrder]:
        for wo in self._work_orders.values():
            if wo.order_number == order_number:
                return wo.model_copy(deep=True)
        return None

    # 用于测试或清理
    def clear(self):
        self._work_orders.clear()

# 单例模式，确保在整个应用中只有一个内存仓储实例 (在简单示例中可以这样，大型应用需更复杂管理)
# 或者通过依赖注入来管理生命周期
# _in_memory_repo_instance = None

# def get_in_memory_work_order_repository():
#     global _in_memory_repo_instance
#     if _in_memory_repo_instance is None:
#         _in_memory_repo_instance = InMemoryWorkOrderRepository()
#     return _in_memory_repo_instance