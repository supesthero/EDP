# core/dependencies.py
from functools import lru_cache
from domain.repositories.work_order_repository import AbstractWorkOrderRepository
from infrastructure.repositories.in_memory_work_order_repository import InMemoryWorkOrderRepository
from application.services.work_order_app_service import WorkOrderApplicationService

# 使用 lru_cache 来实现单例效果 (对于无状态的、可共享的依赖)
@lru_cache()
def get_work_order_repository() -> AbstractWorkOrderRepository:
    """
    获取工单仓储的实例。
    在实际应用中，这里可能会从配置中读取数据库类型，并返回相应的仓储实现。
    """
    return InMemoryWorkOrderRepository()

def get_work_order_application_service() -> WorkOrderApplicationService:
    """
    获取工单应用服务的实例，并注入其依赖。
    """
    repo = get_work_order_repository()
    return WorkOrderApplicationService(work_order_repo=repo)