"""基金列表 API"""
from fastapi import APIRouter, HTTPException
from app.core.config import FUND_WHITELIST
from app.models.schemas import Fund
from app.services.storage import get_nav_date_range, is_fund_cached

router = APIRouter()


@router.get("", response_model=list[Fund])
def list_funds():
    """返回白名单基金列表及缓存状态"""
    funds = []
    for item in FUND_WHITELIST:
        code = item["code"]
        cached = is_fund_cached(code)
        nav_start, nav_end = get_nav_date_range(code) if cached else (None, None)

        funds.append(Fund(
            code=code,
            name=item["name"],
            min_date=nav_start,
            max_date=nav_end,
            cached=cached,
        ))

    return funds


@router.get("/{fund_code}", response_model=Fund)
def get_fund(fund_code: str):
    """获取指定基金信息"""
    for item in FUND_WHITELIST:
        if item["code"] == fund_code:
            cached = is_fund_cached(fund_code)
            nav_start, nav_end = get_nav_date_range(fund_code) if cached else (None, None)
            return Fund(
                code=fund_code,
                name=item["name"],
                min_date=nav_start,
                max_date=nav_end,
                cached=cached,
            )

    raise HTTPException(status_code=404, detail=f"基金 {fund_code} 不在白名单中")