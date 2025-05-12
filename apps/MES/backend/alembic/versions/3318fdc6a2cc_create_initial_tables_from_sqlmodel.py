"""create_initial_tables_from_sqlmodel

Revision ID: <alembic_will_generate_this>
Revises: 
Create Date: <alembic_will_generate_this>

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel # 导入 sqlmodel 以便引用其类型，如果需要的话
# 导入您的领域枚举，以便在迁移脚本中显式创建数据库 ENUM 类型
from domain.value_objects.order_status import OrderStatus


# revision identifiers, used by Alembic.
revision: str = '<alembic_will_generate_this>' # Alembic 会自动填充
down_revision: Union[str, None] = None # 这是第一个迁移，所以没有前一个版本
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### 手动调整或基于 Alembic autogenerate 的命令 ###

    # 1. 显式创建 ENUM 类型 (如果您的数据库是 PostgreSQL 且模型中使用了 ENUM)
    #    确保名称 'order_status_enum' 与您 SQLModel 中 sa_column 定义的名称一致
    #    使用 checkfirst=True 来避免在类型已存在时出错。
    enum_type_for_creation = sa.Enum(OrderStatus, name='order_status_enum')
    enum_type_for_creation.create(op.get_bind(), checkfirst=True)

    # 2. 创建 work_orders 表
    op.create_table('work_orders',
        sa.Column('order_number', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('product_name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        # 在列定义中使用 ENUM 类型时，指定 create_type=False，
        # 因为我们已经在上面显式创建了它。
        sa.Column('status', sa.Enum(OrderStatus, name='order_status_enum', create_type=False), nullable=False, server_default=OrderStatus.PENDING.value),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_work_orders_order_number'), 'work_orders', ['order_number'], unique=True)
    op.create_index(op.f('ix_work_orders_id'), 'work_orders', ['id'], unique=False)

    # 3. 为 updated_at 创建触发器 (PostgreSQL 特定)
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
           NEW.updated_at = now();
           RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    op.execute("""
        CREATE TRIGGER update_work_orders_updated_at
        BEFORE UPDATE ON work_orders
        FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
    """)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### 手动调整或基于 Alembic autogenerate 的命令 ###

    # 1. 移除触发器和函数
    op.execute("DROP TRIGGER IF EXISTS update_work_orders_updated_at ON work_orders;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # 2. 移除索引和表
    op.drop_index(op.f('ix_work_orders_id'), table_name='work_orders')
    op.drop_index(op.f('ix_work_orders_order_number'), table_name='work_orders')
    op.drop_table('work_orders')

    # 3. 移除 ENUM 类型
    #    使用 checkfirst=True 来避免在类型不存在时出错。
    enum_type_for_dropping = sa.Enum(OrderStatus, name='order_status_enum')
    enum_type_for_dropping.drop(op.get_bind(), checkfirst=True)
    # ### end Alembic commands ###
