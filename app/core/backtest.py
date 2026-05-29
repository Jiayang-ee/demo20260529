"""核心回测计算引擎"""
from datetime import date, timedelta
from typing import Optional, List
from app.models.schemas import FundNavRecord, BacktestResult, BacktestMetrics, DataPoint


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


def _calculate_max_drawdown(asset_curve: List[DataPoint]) -> float:
    """计算最大回撤"""
    if not asset_curve or len(asset_curve) < 2:
        return 0.0

    peak = 0.0
    max_drawdown = 0.0

    for point in asset_curve:
        if point.value > peak:
            peak = point.value
        drawdown = (peak - point.value) / peak if peak > 0 else 0
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
    asset_curve: List[DataPoint] = []
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
                asset_curve.append(DataPoint(date=record.date, value=round(current_asset, 2)))

    # 去重并按日期升序排序（每期投入后全量遍历导致重复日期）
    seen_dates = set()
    asset_curve_dedup = []
    for point in asset_curve:
        if point.date not in seen_dates:
            seen_dates.add(point.date)
            asset_curve_dedup.append(point)
    asset_curve = sorted(asset_curve_dedup, key=lambda p: p.date)

    final_nav = nav_map[final_nav_date]
    final_asset = total_shares * final_nav.unit_nav
    total_return = final_asset - total_invested
    return_rate = total_return / total_invested if total_invested > 0 else 0
    max_drawdown = _calculate_max_drawdown(asset_curve) if asset_curve else 0

    lump_sum_asset_curve: List[DataPoint] = []
    lump_sum_final_asset = lump_sum_shares * final_nav.unit_nav
    for record in nav_records:
        if record.date >= first_invest_date and record.date <= final_nav_date:
            asset = lump_sum_shares * record.unit_nav
            lump_sum_asset_curve.append(DataPoint(date=record.date, value=round(asset, 2)))

    lump_sum_return = lump_sum_final_asset - lump_sum_invested
    lump_sum_return_rate = lump_sum_return / lump_sum_invested if lump_sum_invested > 0 else 0
    lump_sum_max_drawdown = _calculate_max_drawdown(lump_sum_asset_curve) if lump_sum_asset_curve else 0

    fund_nav_curve = [
        DataPoint(date=r.date, value=r.unit_nav)
        for r in nav_records
        if first_invest_date <= r.date <= final_nav_date
    ]

    return_rate_curve = [
        DataPoint(date=p.date, value=round((p.value - total_invested) / total_invested, 4))
        for p in asset_curve
    ]

    metrics = BacktestMetrics(
        total_invested=round(total_invested, 2),
        final_asset=round(final_asset, 2),
        total_return=round(total_return, 2),
        return_rate=round(return_rate, 4),
        max_drawdown=max_drawdown,
    )

    return BacktestResult(
        metrics=metrics,
        asset_curve=asset_curve,
        lump_sum_asset_curve=lump_sum_asset_curve,
        fund_nav_curve=fund_nav_curve,
        return_rate_curve=return_rate_curve,
    )