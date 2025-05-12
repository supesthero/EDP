# core/dependencies.py
from sqlmodel import Session # Import Session from sqlmodel
from fastapi import Depends

from domain.repositories.work_order_repository import AbstractWorkOrderRepository
from infrastructure.repositories.sqlmodel_work_order_repository import SQLModelWorkOrderRepository # Import new repo
from infrastructure.database.connection import get_session # Import get_session
from application.services.work_order_app_service import WorkOrderApplicationService

def get_work_order_repository(session: Session = Depends(get_session)) -> AbstractWorkOrderRepository:
    """
    Dependency to get the SQLModel-based work order repository instance.
    It requires a database session, which is also injected by FastAPI.
    """
    return SQLModelWorkOrderRepository(session=session)

def get_work_order_application_service(
    repo: AbstractWorkOrderRepository = Depends(get_work_order_repository)
) -> WorkOrderApplicationService:
    """
    Gets the WorkOrderApplicationService with its dependencies injected.
    """
    return WorkOrderApplicationService(work_order_repo=repo)
