"""核心回测计算引擎"""
from datetime import date, timedelta
from typing import Optional, List
from app.models.schemas import FundNavRecord, BacktestResult, BacktestMetrics


def _find_nav_on_or_after(nav_records: List[FundNavRecord], target_date: date) -> Optional[FundNavRecord]:
    """查找指定日期或之后的第一个净值记录"""
    for record in nav_records:
        if record.date >= target_date:
            return record
    return None


def _find_nav_on_or_before(nav_records: List[FundNavRecord], target_date: date) -> Optional[FundNavRecord]:
    """查找指定日期或之前最近的净值记录"""
    for record in reversed(nav_records):
        if record.date <= target_date:
            return record
    return None


def _generate_investment_dates(
    frequency: str,
    start_date: date,
    end_date: date,
    nav_records: List[FundNavRecord],
) -> List[date]:
    """生成定投日期序列（仅包含实际有净值记录的日期）"""
    investment_dates = []

    if frequency == "monthly":
        current = start_date.replace(day=min(start_date.day, 28))
        while current <= end_date:
            adjusted = _find_nav_on_or_after(nav_records, current)
            if adjusted:
                if adjusted.date <= end_date:
                    investment_dates.append(adjusted.date)
                else:
                    break
            year = current.year + (current.month // 12)
            month = (current.month % 12) + 1
            current = current.replace(year=year, month=month)

    elif frequency == "weekly":
        current = start_date
        week_offset = 0
        while current <= end_date:
            target_day = start_date + timedelta(weeks=week_offset)
            adjusted = _find_nav_on_or_after(nav_records, target_day)
            if adjusted:
                if adjusted.date <= end_date:
                    investment_dates.append(adjusted.date)
                else:
                    break
            week_offset += 1
            current = start_date + timedelta(weeks=week_offset)

    return investment_dates


def _calculate_max_drawdown(asset_curve: List[dict]) -> float:
    """计算最大回撤"""
    if not asset_curve or len(asset_curve) < 2:
        return 0.0

    peak = 0.0
    max_drawdown = 0.0

    for point in asset_curve:
        value = point.get("value", point.get("asset", 0))
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak if peak > 0 else 0
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    return round(max_drawdown, 4)


def calculate_backtest(
    nav_records: List[FundNavRecord],
    amount: float,
    frequency: str,
    start_date: date,
    end_date: date,
) -> BacktestResult:
    """计算定投回测结果"""
    if not nav_records:
        raise ValueError("无净值数据")

    first_nav = _find_nav_on_or_after(nav_records, start_date)
    if not first_nav:
        raise ValueError(f"开始日期 {start_date} 后无净值数据")
    first_invest_date = first_nav.date

    last_nav = _find_nav_on_or_before(nav_records, end_date)
    if not last_nav:
        raise ValueError(f"结束日期 {end_date} 前无净值数据")
    final_nav_date = last_nav.date

    investment_dates = _generate_investment_dates(frequency, first_invest_date, end_date, nav_records)

    nav_map = {r.date: r for r in nav_records}

    total_invested = 0.0
    total_shares = 0.0
    dca_curve: List[dict] = []
    lump_sum_shares = amount
    lump_sum_invested = amount

    for investment_date in investment_dates:
        nav = nav_map[investment_date]
        shares = amount / nav.unit_nav
        total_shares += shares
        total_invested += amount

        for record in nav_records:
            if record.date >= investment_date and record.date <= final_nav_date:
                current_asset = total_shares * record.unit_nav
                dca_curve.append({
                    "date": record.date.isoformat(),
                    "asset": round(current_asset, 2),
                    "nav": record.unit_nav,
                })

    # 去重并按日期升序排序（每期投入后全量遍历导致重复日期）
    seen_dates = set()
    dca_curve_dedup = []
    for point in dca_curve:
        if point["date"] not in seen_dates:
            seen_dates.add(point["date"])
            dca_curve_dedup.append(point)
    dca_curve = sorted(dca_curve_dedup, key=lambda p: p["date"])

    final_nav = nav_map[final_nav_date]
    final_asset = total_shares * final_nav.unit_nav
    total_return = final_asset - total_invested
    return_rate = total_return / total_invested if total_invested > 0 else 0
    max_drawdown = _calculate_max_drawdown(dca_curve) if dca_curve else 0

    dca_metrics = BacktestMetrics(
        total_invested=round(total_invested, 2),
        final_asset=round(final_asset, 2),
        total_return=round(total_return, 2),
        return_rate=round(return_rate, 4),
        max_drawdown=max_drawdown,
    )

    lump_sum_asset_curve: List[dict] = []
    lump_sum_final_asset = lump_sum_shares * final_nav.unit_nav
    for record in nav_records:
        if record.date >= first_invest_date and record.date <= final_nav_date:
            asset = lump_sum_shares * record.unit_nav
            lump_sum_asset_curve.append({
                "date": record.date.isoformat(),
                "asset": round(asset, 2),
                "nav": record.unit_nav,
            })

    lump_sum_return = lump_sum_final_asset - lump_sum_invested
    lump_sum_return_rate = lump_sum_return / lump_sum_invested if lump_sum_invested > 0 else 0
    lump_sum_max_drawdown = _calculate_max_drawdown(lump_sum_asset_curve) if lump_sum_asset_curve else 0

    lump_sum_metrics = BacktestMetrics(
        total_invested=round(lump_sum_invested, 2),
        final_asset=round(lump_sum_final_asset, 2),
        total_return=round(lump_sum_return, 2),
        return_rate=round(lump_sum_return_rate, 4),
        max_drawdown=lump_sum_max_drawdown,
    )

    nav_curve = [
        {"date": r.date.isoformat(), "nav": r.unit_nav}
        for r in nav_records
        if first_invest_date <= r.date <= final_nav_date
    ]

    return_curve = [
        {
            "date": p["date"],
            "dca_return": round((p["asset"] - total_invested) / total_invested, 4) if total_invested > 0 else 0,
            "lump_sum_return": round((lump_sum_asset_curve[i]["asset"] - lump_sum_invested) / lump_sum_invested, 4) if lump_sum_invested > 0 else 0,
        }
        for i, p in enumerate(dca_curve)
    ]

    return BacktestResult(
        dca_metrics=dca_metrics,
        lump_sum_metrics=lump_sum_metrics,
        dca_curve=dca_curve,
        lump_sum_curve=lump_sum_asset_curve,
        nav_curve=nav_curve,
        return_curve=return_curve,
    )