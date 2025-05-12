# domain/entities/work_order.py
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from domain.value_objects.order_status import OrderStatus

class WorkOrder(BaseModel):
    """
    工单实体
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    order_number: str = Field(..., min_length=1, max_length=50, description="工单号")
    product_name: str = Field(..., min_length=1, max_length=100, description="产品名称")
    quantity: int = Field(..., gt=0, description="计划数量")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="工单状态")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="最后更新时间")
    due_date: Optional[datetime] = Field(default=None, description="计划完成日期")
    notes: Optional[str] = Field(default=None, max_length=500, description="备注")

    def update_status(self, new_status: OrderStatus):
        # 这里可以添加领域逻辑，例如状态转换规则
        if self.status == OrderStatus.COMPLETED and new_status != OrderStatus.COMPLETED:
            raise ValueError("Cannot change status of a completed order.")
        if self.status == OrderStatus.CANCELLED and new_status != OrderStatus.CANCELLED:
            raise ValueError("Cannot change status of a cancelled order.")
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def update_details(self, product_name: Optional[str] = None, quantity: Optional[int] = None, due_date: Optional[datetime] = None, notes: Optional[str] = None):
        if self.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            raise ValueError(f"Cannot update details of a {self.status.value} order.")
        if product_name is not None:
            self.product_name = product_name
        if quantity is not None:
            if quantity <= 0:
                raise ValueError("Quantity must be positive.")
            self.quantity = quantity
        if due_date is not None:
            self.due_date = due_date
        if notes is not None:
            self.notes = notes
        self.updated_at = datetime.utcnow()

    class Config:
        validate_assignment = True # 允许在赋值时进行校验