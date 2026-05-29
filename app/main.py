"""基金定投回测工具 - 主应用入口"""
from fastapi import FastAPI
from app.api import funds, sync, backtest

app = FastAPI(title="基金定投回测工具 API", version="1.0.0")

app.include_router(funds.router, prefix="/api/funds", tags=["基金"])
app.include_router(sync.router, prefix="/api/funds", tags=["同步"])
app.include_router(backtest.router, prefix="/api", tags=["回测"])


@app.get("/health")
def health():
    return {"status": "ok"}