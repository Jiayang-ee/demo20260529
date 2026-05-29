"""从东方财富/天天基金获取基金净值数据"""
import httpx
from datetime import date, datetime
from app.models.schemas import FundNavRecord


async def fetch_fund_nav(fund_code: str) -> list[FundNavRecord]:
    """从天天基金获取基金历史净值"""
    url = f"https://api.fund.eastmoney.com/f10/lsjz"
    params = {
        "callback": "jQuery",
        "fundCode": fund_code,
        "pageIndex": 1,
        "pageSize": 10000,
        "startDate": "",
        "endDate": "",
    }
    headers = {
        "Referer": "https://fund.eastmoney.com/",
        "User-Agent": "Mozilla/5.0",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(f"请求失败: HTTP {response.status_code}")

    text = response.text
    if not text.startswith("jQuery"):
        raise RuntimeError(f"数据源返回异常格式")

    import json
    try:
        json_str = text[7:-2] if text.endswith(");") else text[7:]
        data = json.loads(json_str)
    except json.JSONDecodeError:
        raise RuntimeError("解析 JSON 失败")

    lsjz_list = data.get("Data", {}).get("LSJZList", [])
    if not lsjz_list:
        raise RuntimeError(f"基金 {fund_code} 无净值数据")

    records = []
    for item in lsjz_list:
        record_date = datetime.strptime(item["FSRQ"], "%Y-%m-%d").date()
        records.append(FundNavRecord(
            date=record_date,
            unit_nav=float(item["DWJZ"]),
            accumulated_nav=float(item["LJJZ"]) if item.get("LJJZ") else None,
            fetched_at=datetime.now().isoformat(),
            source="east_money",
        ))

    records.reverse()
    return records