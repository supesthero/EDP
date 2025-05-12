# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.endpoints import work_orders_router
from core.dependencies import get_work_order_repository # For potential cleanup or init
from infrastructure.repositories.in_memory_work_order_repository import InMemoryWorkOrderRepository


# 可选: 生命周期事件 (例如，初始化数据库连接池，清理资源)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行
    print("MES Backend Service is starting up...")
    # 如果需要，可以在这里初始化/连接数据库
    # repo = get_work_order_repository()
    # if isinstance(repo, InMemoryWorkOrderRepository):
    #     print("Using In-Memory Work Order Repository.")
    #     # repo.load_initial_data() # 例如，加载一些初始数据

    yield # 应用运行

    # 应用关闭时执行
    print("MES Backend Service is shutting down...")
    # repo = get_work_order_repository()
    # if isinstance(repo, InMemoryWorkOrderRepository):
    #     repo.clear() # 清理内存数据 (如果需要)


app = FastAPI(
    title="MES Backend API",
    version="0.1.0",
    description="制造执行系统 (MES) 后端服务，基于 FastAPI 和 DDD。",
    lifespan=lifespan # FastAPI 0.93+
)

# 包含API路由
app.include_router(work_orders_router.router, prefix="/api/v1") # 添加 /api/v1 前缀

@app.get("/health", tags=["Health Check - 健康检查"])
async def health_check():
    """
    服务健康检查接口
    """
    return {"status": "ok", "message": "MES Backend is healthy!"}

# 如果你想直接运行 (例如: python main.py)
if __name__ == "__main__":
    import uvicorn
    # 注意: uvicorn.run("main:app"...) 中的 "main" 指的是文件名 main.py
    # "app" 指的是 FastAPI 实例 `app = FastAPI()`
    # reload=True 只用于开发环境
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)