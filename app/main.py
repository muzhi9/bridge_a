from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import API_KEY, DATA_DIR
from .engines import EngineBundle
from .routers import extract, info, text


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engines = EngineBundle(DATA_DIR)
    yield


app = FastAPI(
    title="多功能文本处理网关服务",
    description="集文本工具箱、网页正文提取、离线信息挖掘于一体的轻量网关服务。",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(text.router)
app.include_router(extract.router)
app.include_router(info.router)


@app.get("/", summary="服务状态")
def root():
    engines: EngineBundle = app.state.engines
    return {
        "service": "multifunction-text-gateway",
        "version": "1.0.0",
        "status": "ok",
        "data_errors": engines.data_errors,
        "endpoints": {
            "text": "/api/tool/text",
            "extract": "/api/tool/extract",
            "idcard": "/api/tool/idcard",
            "phone": "/api/tool/phone",
        },
    }
