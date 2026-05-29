"""回测 API"""
from fastapi import APIRouter, HTTPException
from app.core.config import FUND_WHITELIST
from app.core.backtest import calculate_backtest
from app.models.schemas import BacktestRequest, BacktestResponse
from app.services.storage import load_nav_records, is_fund_cached

router = APIRouter()


@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """执行定投回测"""
    for item in FUND_WHITELIST:
        if item["code"] == request.fund_code:
            break
    else:
        return BacktestResponse(success=False, error=f"基金 {request.fund_code} 不在白名单中")

    if not is_fund_cached(request.fund_code):
        return BacktestResponse(success=False, error=f"基金 {request.fund_code} 数据未缓存，请先同步")

    nav_records = load_nav_records(request.fund_code)
    if not nav_records:
        return BacktestResponse(success=False, error=f"基金 {request.fund_code} 无缓存数据")

    try:
        result = calculate_backtest(
            nav_records=nav_records,
            amount=request.amount,
            frequency=request.frequency,
            start_date=request.start_date,
            end_date=request.end_date,
        )
        return BacktestResponse(success=True, data=result)
    except ValueError as e:
        return BacktestResponse(success=False, error=str(e))