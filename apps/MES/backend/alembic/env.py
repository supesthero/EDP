# alembic/env.py
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from dotenv import load_dotenv # 用于加载 .env 文件

from alembic import context

# 导入 SQLModel 基类 和 您的表模型
# 确保路径正确，如果 alembic 目录与您的项目代码在同一级或子级
# 将项目根目录添加到 sys.path，以便 Alembic 能找到您的模型
project_root = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlmodel import SQLModel
# 导入所有您希望 Alembic 管理的 SQLModel 表模型
# 例如:
from infrastructure.sqlmodels.work_order import WorkOrder
# 如果有其他模型，也在这里导入

# 这是 Alembic 配置对象，提供了对 .ini 文件中值的访问
config = context.config

# 为 Python 日志解释配置文件
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- 自定义配置开始 ---

# 加载 .env 文件以获取 DATABASE_URL
# .env 文件应该位于项目根目录 (与 alembic.ini 同级或上一级)
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

# 从环境变量获取数据库 URL，并设置到 Alembic 配置中
# 这会覆盖 alembic.ini 中的 sqlalchemy.url (如果已设置)
db_url_from_env = os.getenv("DATABASE_URL")
if db_url_from_env:
    config.set_main_option("sqlalchemy.url", db_url_from_env)
elif not config.get_main_option("sqlalchemy.url"):
    # 如果 .env 和 alembic.ini 都没有配置 URL，则抛出错误
    raise ValueError("DATABASE_URL is not set in environment or alembic.ini")

# 设置 Alembic 的 target_metadata 为 SQLModel.metadata
# 这样 Alembic 才能知道您的模型结构以进行自动生成 (autogenerate)
target_metadata = SQLModel.metadata

# --- 自定义配置结束 ---


def run_migrations_offline() -> None:
    """在“离线”模式下运行迁移。
    此配置仅使用 URL 而非 Engine 配置上下文。
    虽然这里也可以接受 Engine。通过跳过 Engine 创建，
    我们甚至不需要 DBAPI 可用。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # 为了更好地检测 ENUM 类型等，可以启用 compare_type
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在“在线”模式下运行迁移。
    在这种情况下，我们需要创建一个 Engine 并将连接与上下文关联起来。
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # 为了更好地检测 ENUM 类型等，可以启用 compare_type
            compare_type=True,
            # 对于 PostgreSQL ENUM，如果自动生成有问题，可能需要特殊处理
            # 确保您的 SQLModel 定义和迁移脚本同步
            render_as_batch=True # 对于 SQLite 等不支持 ALTER 的数据库，批处理模式可能有用
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
