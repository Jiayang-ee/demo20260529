"""基金数据同步 API"""
from fastapi import APIRouter, HTTPException
from app.core.config import FUND_WHITELIST
from app.services.fund_api import fetch_fund_nav
from app.services.storage import save_nav_records

router = APIRouter()


@router.post("/sync")
async def sync_funds():
    """抓取或刷新全部白名单基金历史净值"""
    results = []
    for item in FUND_WHITELIST:
        code = item["code"]
        name = item["name"]
        try:
            records = await fetch_fund_nav(code)
            save_nav_records(code, records)
            results.append({
                "code": code,
                "name": name,
                "status": "success",
                "count": len(records),
            })
        except Exception as e:
            results.append({
                "code": code,
                "name": name,
                "status": "failed",
                "error": str(e),
            })

    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = len(results) - success_count

    return {
        "total": len(results),
        "success": success_count,
        "failed": failed_count,
        "results": results,
    }


@router.post("/sync/{fund_code}")
async def sync_single_fund(fund_code: str):
    """抓取或刷新单支基金历史净值"""
    found = False
    name = ""
    for item in FUND_WHITELIST:
        if item["code"] == fund_code:
            found = True
            name = item["name"]
            break

    if not found:
        raise HTTPException(status_code=404, detail=f"基金 {fund_code} 不在白名单中")

    try:
        records = await fetch_fund_nav(fund_code)
        save_nav_records(fund_code, records)
        return {
            "code": fund_code,
            "name": name,
            "status": "success",
            "count": len(records),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))