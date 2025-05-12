# api/endpoints/work_orders_router.py
import uuid
from sqlmodel import SQLModel
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query

# Import SQLModel schemas directly
from infrastructure.sqlmodels.work_order import (
    WorkOrder, # The table model, can be used for responses if it matches WorkOrderReadFull
    WorkOrderCreate,
    WorkOrderRead,
    WorkOrderUpdate,
    WorkOrderReadFull
)
from application.services.work_order_app_service import WorkOrderApplicationService
from core.dependencies import get_work_order_application_service

router = APIRouter(
    prefix="/work-orders",
    tags=["Work Orders - 工单管理 (SQLModel)"], # Updated tag
)

@router.post(
    "/",
    response_model=WorkOrderRead, # Or WorkOrderReadFull if you want all fields from table model
    status_code=status.HTTP_201_CREATED,
    summary="创建新工单 (SQLModel)"
)
async def create_work_order(
    wo_create: WorkOrderCreate, # Use SQLModel schema for request body
    service: WorkOrderApplicationService = Depends(get_work_order_application_service)
) -> Any: # Return type can be WorkOrderRead or WorkOrder (SQLModel table model)
    """
    创建一张新的工单。SQLModel 版本。
    - **order_number**: 工单号 (必填, 唯一)
    - **product_name**: 产品名称 (必填)
    - **quantity**: 计划数量 (必填, >0)
    - **status**: 初始状态 (可选, 默认为 PENDING)
    - **due_date**: 计划完成日期 (可选)
    - **notes**: 备注 (可选)
    """
    try:
        # The service method will need to be adapted to accept WorkOrderCreate
        # and return a WorkOrder (table model) or compatible type.
        created_wo = await service.create_work_order_sqlmodel(wo_create_data=wo_create)
        return created_wo
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log the exception e
        print(f"Error in create_work_order: {e}") # Basic logging
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error creating work order")


@router.get(
    "/{wo_id}",
    response_model=WorkOrderReadFull, # Use WorkOrderRead or WorkOrderReadFull
    summary="根据ID获取工单详情 (SQLModel)"
)
async def get_work_order_by_id(
    wo_id: uuid.UUID,
    service: WorkOrderApplicationService = Depends(get_work_order_application_service)
) -> Any:
    work_order = await service.get_work_order_by_id(wo_id) # Service returns SQLModel WorkOrder
    if not work_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work Order not found")
    return work_order


class WorkOrderListResponse(SQLModel): # Define a Pydantic/SQLModel for list response
    items: List[WorkOrderRead] # List of read models
    total: int
    skip: int
    limit: int

@router.get(
    "/",
    response_model=WorkOrderListResponse, # Use the new list response model
    summary="获取工单列表 (分页, SQLModel)"
)
async def list_work_orders(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页的记录数"),
    service: WorkOrderApplicationService = Depends(get_work_order_application_service)
) -> WorkOrderListResponse:
    items = await service.get_all_work_orders(skip=skip, limit=limit) # Service returns List[WorkOrder]
    total_count = await service.count_work_orders()
    # Convert items to WorkOrderRead if necessary, though direct SQLModel WorkOrder might be fine
    # if WorkOrderReadFull is the target and WorkOrder is compatible.
    # For explicit schema, map here:
    # read_items = [WorkOrderRead.model_validate(item) for item in items]
    return WorkOrderListResponse(
        items=items, # Assuming service returns List[WorkOrder] which is compatible with List[WorkOrderRead] structure
        total=total_count,
        skip=skip,
        limit=limit
    )


@router.put(
    "/{wo_id}",
    response_model=WorkOrderRead, # Or WorkOrderReadFull
    summary="更新工单信息 (SQLModel)"
)
async def update_work_order(
    wo_id: uuid.UUID,
    wo_update: WorkOrderUpdate, # Use SQLModel schema for request body
    service: WorkOrderApplicationService = Depends(get_work_order_application_service)
) -> Any:
    try:
        # Service method needs to accept WorkOrderUpdate
        updated_wo = await service.update_work_order_sqlmodel(wo_id=wo_id, wo_update_data=wo_update)
        if not updated_wo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work Order not found for update")
        return updated_wo
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Error in update_work_order: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error updating work order")


@router.delete(
    "/{wo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除工单 (SQLModel)"
)
async def delete_work_order(
    wo_id: uuid.UUID,
    service: WorkOrderApplicationService = Depends(get_work_order_application_service)
):
    try:
        deleted = await service.delete_work_order(wo_id) # Service method is fine
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work Order not found or could not be deleted")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return None
