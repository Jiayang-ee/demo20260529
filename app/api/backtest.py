"""回测 API"""
from fastapi import APIRouter, HTTPException
from app.core.config import FUND_WHITELIST
from app.core.backtest import calculate_backtest
from app.models.schemas import BacktestRequest, BacktestResult
from app.services.storage import load_nav_records

router = APIRouter()


@router.post("/backtest", response_model=BacktestResult)
async def run_backtest(request: BacktestRequest):
    """执行定投回测"""
    for item in FUND_WHITELIST:
        if item["code"] == request.fund_code:
            break
    else:
        raise HTTPException(status_code=404, detail=f"基金 {request.fund_code} 不在白名单中")

    if not is_fund_cached(request.fund_code):
        raise HTTPException(status_code=400, detail=f"基金 {request.fund_code} 数据未缓存，请先同步")

    nav_records = load_nav_records(request.fund_code)
    if not nav_records:
        raise HTTPException(status_code=400, detail=f"基金 {request.fund_code} 无缓存数据")

    try:
        result = calculate_backtest(
            nav_records=nav_records,
            amount=request.amount,
            frequency=request.frequency,
            start_date=request.start_date,
            end_date=request.end_date,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def is_fund_cached(fund_code: str) -> bool:
    """检查基金数据是否已缓存"""
    from app.services.storage import is_fund_cached as _is_cached
    return _is_cached(fund_code)