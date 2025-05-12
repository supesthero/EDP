# MES Backend

制造执行系统 (MES) 后端服务，基于 FastAPI 和领域驱动设计 (DDD)。

## 技术栈

* Python 3.10+
* FastAPI
* Pydantic
* Uvicorn
* DDD (领域驱动设计) 架构模式

## 项目结构

详细的项目结构说明... (可以参考上面的结构图)

## 环境设置

1.  **创建虚拟环境**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate    # Windows
    ```

2.  **安装依赖**:
    假设使用 Poetry:
    ```bash
    pip install poetry
    poetry install
    ```
    或者使用 PDM:
    ```bash
    pip install pdm
    pdm install
    ```
    或者如果你直接使用 `pip` 和 `requirements.txt` (需要从`pyproject.toml`生成):
    ```bash
    poetry export -f requirements.txt --output requirements.txt --without-hashes # (如果用poetry)
    pip install -r requirements.txt
    ```
    或者使用 `uv`:
    ```bash
    uv pip install -r requirements.txt # (如果已有 requirements.txt)
    uv venv .venv # 创建虚拟环境
    uv pip sync pyproject.toml # 同步依赖 (如果使用 uv 管理项目)
    ```


## 运行服务

使用 Uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000