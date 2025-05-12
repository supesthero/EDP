# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from api.endpoints import work_orders_router
# engine 仍然可以从 connection 导入，以备 Alembic 或其他直接操作使用
from infrastructure.database.connection import engine 
# 不再需要从这里导入 SQLModel 基类和表模型用于 create_all

# 在应用的最开始加载 .env 文件
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("MES 后端服务正在启动...")
    
    # Alembic 将负责数据库表的创建和迁移
    # 因此此处不再调用 SQLModel.metadata.create_all(engine)
    print("数据库表结构将由 Alembic 管理。")

    yield # 应用在此处运行

    print("MES 后端服务正在关闭...")


app = FastAPI(
    title="MES 后端 API (SQLModel + Alembic)",
    version="0.1.0",
    description="制造执行系统 (MES) 后端服务，基于 FastAPI, DDD, SQLModel, 并使用 Alembic 进行数据库迁移。",
    lifespan=lifespan
)

app.include_router(work_orders_router.router, prefix="/api/v1")

@app.get("/health", tags=["Health Check - 健康检查"])
async def health_check():
    """
    服务健康检查接口
    """
    return {"status": "ok", "message": "MES 后端服务运行正常!"}

if __name__ == "__main__":
    import uvicorn
    # 确保您的 .env 文件中的 DATABASE_URL 配置正确，
    # 并且 PostgreSQL 服务正在运行，目标数据库（例如 mes_db）已存在。
    # 然后运行 `alembic upgrade head` 来创建/更新表结构。
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
