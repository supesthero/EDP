# api/endpoints/work_orders_router.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from api.schemas import work_order_schemas
from application.services.work_order_app_service import WorkOrderApplicationService
from core.dependencies import get_work_order_application_service # 修改了导入

router = APIRouter(
    prefix="/work-orders",
    tags=["Work Orders - 工单管理"],
)

# FastAPI 会自动处理从 service 返回的领域实体 WorkOrder 到 WorkOrderResponse 的转换
# (因为 WorkOrderResponse.Config.from_attributes = True)

@router.post(
    "/",
    response_model=work_order_schemas.WorkOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建新工单"
)
async def create_work_order(
    wo_create: work_order_schemas.WorkOrderCreateRequest,
    service: WorkOrderApplicationService = Depends(get_work_order_application_service)
):
    """
    创建一张新的工单。
    - **order_number**: 工单号 (必填, 唯一)
    - **product_name**: 产品名称 (必填)
    - **quantity**: 计划数量 (必填, >0)
    - **status**: 初始状态 (可选, 默认为 PENDING)
    - **due_date**: 计划完成日期 (可选)
    - **notes**: 备注 (可选)
    """
    try:
        created_wo = await service.create_work_order(wo_create)
        return created_wo
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/{wo_id}",
    response_model=work_order_schemas.WorkOrderResponse,
    summary="根据ID获取工单详情"
)
async def get_work_order_by_id(
    wo_id: uuid.UUID,
    service: WorkOrderApplicationService = Depends(get_work_order_application_service)
):
    """
    通过工单的唯一ID获取其详细信息。
    """
    work_order = await service.get_work_order_by_id(wo_id)
    if not work_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work Order not found")
    return work_order


@router.get(
    "/",
    response_model=work_order_schemas.WorkOrderListResponse,
    summary="获取工单列表 (分页)"
)
async def list_work_orders(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页的记录数"),
    service: WorkOrderApplicationService = Depends(get_work_order_application_service)
):
    """
    获取工单列表，支持分页。
    """
    items = await service.get_all_work_orders(skip=skip, limit=limit)
    total_count = await service.count_work_orders() # 获取总数
    return work_order_schemas.WorkOrderListResponse(
        items=items,
        total=total_count,
        skip=skip,
        limit=limit
    )


@router.put(
    "/{wo_id}",
    response_model=work_order_schemas.WorkOrderResponse,
    summary="更新工单信息"
)
async def update_work_order(
    wo_id: uuid.UUID,
    wo_update: work_order_schemas.WorkOrderUpdateRequest,
    service: WorkOrderApplicationService = Depends(get_work_order_application_service)
):
    """
    更新指定ID的工单信息。
    只有提供的字段才会被更新。
    """
    try:
        updated_wo = await service.update_work_order(wo_id, wo_update)
        if not updated_wo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work Order not found")
        return updated_wo
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete(
    "/{wo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除工单"
)
async def delete_work_order(
    wo_id: uuid.UUID,
    service: WorkOrderApplicationService = Depends(get_work_order_application_service)
):
    """
    根据ID删除工单。
    """
    try:
        deleted = await service.delete_work_order(wo_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work Order not found or could not be deleted")
    except ValueError as e: # 例如，试图删除进行中的工单
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return None # HTTP 204 No Content