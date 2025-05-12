# infrastructure/sqlmodels/work_order.py
import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID # For PostgreSQL specific UUID type
from sqlalchemy import Enum as SAEnum # For SQLAlchemy Enum type

from domain.value_objects.order_status import OrderStatus # Your domain enum

class WorkOrderBase(SQLModel):
    """
    Base SQLModel for WorkOrder, containing common fields.
    This can be used for request bodies (Create/Update) and response bodies.
    """
    order_number: str = Field(max_length=50, unique=True, index=True, description="工单号")
    product_name: str = Field(max_length=100, description="产品名称")
    quantity: int = Field(gt=0, description="计划数量")
    status: OrderStatus = Field(
        # Ensure the name matches the ENUM type created by Alembic.
        # create_type=False because Alembic is responsible for creating the type.
        sa_column=Column(SAEnum(OrderStatus, name="order_status_enum", create_type=False), nullable=False),
        default=OrderStatus.PENDING,
        description="工单状态"
    )
    due_date: Optional[datetime] = Field(default=None, description="计划完成日期")
    notes: Optional[str] = Field(default=None, max_length=500, description="备注")


class WorkOrder(WorkOrderBase, table=True):
    """
    SQLModel representing the 'work_orders' table.
    This inherits from WorkOrderBase and adds table-specific fields like id, created_at, updated_at.
    """
    __tablename__ = "work_orders" # Explicitly set table name, matches Alembic migration

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, # SQLModel/Pydantic level default for new instances
        # primary_key, index, nullable moved to sa_column
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, index=True, nullable=False)
    )
    created_at: Optional[datetime] = Field(
        default=None, # Will be set by DB default (see Alembic migration)
        description="创建时间"
        # sa_column_kwargs={'server_default': sa.text('now()')} # Can also be defined here
    )
    updated_at: Optional[datetime] = Field(
        default=None, # Will be set by DB default/trigger (see Alembic migration)
        description="最后更新时间"
        # sa_column_kwargs={'server_default': sa.text('now()'), 'onupdate': sa.text('now()')}
    )

# API Data Models (derived from SQLModel)

class WorkOrderCreate(WorkOrderBase):
    """
    Schema for creating a new Work Order.
    All fields from WorkOrderBase are used.
    """
    pass


class WorkOrderRead(WorkOrderBase):
    """
    Schema for reading/returning a Work Order, including DB-generated fields.
    """
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    # status is already in WorkOrderBase


class WorkOrderUpdate(SQLModel):
    """
    Schema for updating an existing Work Order.
    All fields are optional.
    """
    order_number: Optional[str] = Field(default=None, max_length=50, unique=True, index=True) # Keep unique/index if updatable
    product_name: Optional[str] = Field(default=None, max_length=100)
    quantity: Optional[int] = Field(default=None, gt=0)
    status: Optional[OrderStatus] = Field(default=None) # sa_column not needed for update schema
    due_date: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=500)

# For responses that include all table fields:
class WorkOrderReadFull(WorkOrder):
    """
    Schema for reading a Work Order with all its database fields.
    """
    pass
