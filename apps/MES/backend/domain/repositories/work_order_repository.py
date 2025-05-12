# domain/repositories/work_order_repository.py
import abc
import uuid
from typing import List, Optional
from domain.entities.work_order import WorkOrder

class AbstractWorkOrderRepository(abc.ABC):
    """
    工单仓储抽象基类 (接口)
    """

    @abc.abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[WorkOrder]:
        raise NotImplementedError

    @abc.abstractmethod
    async def add(self, work_order: WorkOrder) -> WorkOrder:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, work_order: WorkOrder) -> Optional[WorkOrder]:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[WorkOrder]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_order_number(self, order_number: str) -> Optional[WorkOrder]:
        raise NotImplementedError