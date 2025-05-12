# api/schemas/work_order_schemas.py
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from domain.value_objects.order_status import OrderStatus

# --- 基本模型 ---
class WorkOrderBase(BaseModel):
    order_number: str = Field(..., min_length=1, max_length=50, description="工单号", examples=["WO-2025-001"])
    product_name: str = Field(..., min_length=1, max_length=100, description="产品名称", examples=["高端齿轮"])
    quantity: int = Field(..., gt=0, description="计划数量", examples=[100])
    due_date: Optional[datetime] = Field(default=None, description="计划完成日期", examples=["2025-12-31T23:59:59Z"])
    notes: Optional[str] = Field(default=None, max_length=500, description="备注", examples=["加急生产"])

# --- 创建请求模型 ---
class WorkOrderCreateRequest(WorkOrderBase):
    status: Optional[OrderStatus] = Field(default=OrderStatus.PENDING, description="初始工单状态")

# --- 更新请求模型 ---
class WorkOrderUpdateRequest(BaseModel):
    order_number: Optional[str] = Field(default=None, min_length=1, max_length=50, description="工单号")
    product_name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="产品名称")
    quantity: Optional[int] = Field(default=None, gt=0, description="计划数量")
    status: Optional[OrderStatus] = Field(default=None, description="工单状态")
    due_date: Optional[datetime] = Field(default=None, description="计划完成日期")
    notes: Optional[str] = Field(default=None, max_length=500, description="备注")

# --- 响应模型 ---
class WorkOrderResponse(WorkOrderBase):
    id: uuid.UUID
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # 兼容 ORM 模型直接转换 (Pydantic V2) / orm_mode = True (Pydantic V1)

class WorkOrderListResponse(BaseModel):
    items: List[WorkOrderResponse]
    total: int
    skip: int
    limit: int