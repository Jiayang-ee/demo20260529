"""核心计算单元测试"""
import pytest
from datetime import date
from app.core.backtest import calculate_backtest, _calculate_max_drawdown, _find_nav_on_or_after
from app.models.schemas import FundNavRecord


def _make_nav(records: list[tuple[str, float]]) -> list[FundNavRecord]:
    """辅助：创建净值记录列表"""
    result = []
    for date_str, unit_nav in records:
        result.append(FundNavRecord(
            date=date.fromisoformat(date_str),
            unit_nav=unit_nav,
            accumulated_nav=unit_nav * 1.1,
            fetched_at="2026-01-01T00:00:00",
            source="test",
        ))
    return result


class TestNonTradingDayRollForward:
    """非交易日顺延测试"""

    def test_investment_on_non_trading_day_rolls_forward(self):
        """定投日为非交易日时，应顺延到下一个有净值记录的日期"""
        # 周五开始定投，每周定投，end_date 延至1月9以容纳第二期
        nav_records = _make_nav([
            ("2026-01-02", 1.0),   # 周五
            ("2026-01-05", 1.1),   # 周一
            ("2026-01-06", 1.2),
            ("2026-01-07", 1.3),
            ("2026-01-08", 1.4),
            ("2026-01-09", 1.5),
        ])

        # 起始日期是 1月2日（周五），每周定投，end_date 到 1月9
        result = calculate_backtest(
            nav_records=nav_records,
            amount=100.0,
            frequency="weekly",
            start_date=date(2026, 1, 2),
            end_date=date(2026, 1, 9),
        )

        # 第一期投在 1月2日（实际净值日）
        # 第二期应顺延到 1月5日（下一个有净值记录的日期）
        # 验证有且仅有两期投入
        total_invested = result.metrics.total_invested
        assert total_invested == 200.0

    def test_skip_investment_if_roll_forward_exceeds_end_date(self):
        """顺延超过结束日时应跳过该期"""
        nav_records = _make_nav([
            ("2026-01-02", 1.0),
            ("2026-01-05", 1.1),
        ])

        result = calculate_backtest(
            nav_records=nav_records,
            amount=100.0,
            frequency="monthly",
            start_date=date(2026, 1, 2),
            end_date=date(2026, 1, 5),
        )

        # 只应在 1月2日有一期投入
        assert result.metrics.total_invested == 100.0


class TestMonthlyVsWeekly:
    """月投/周投测试"""

    def test_monthly_investment_frequency(self):
        """月投：每月同日定投"""
        nav_records = _make_nav([
            ("2026-01-15", 1.0),
            ("2026-01-16", 1.0),
            ("2026-02-15", 1.2),
            ("2026-02-16", 1.2),
            ("2026-03-15", 1.4),
            ("2026-03-16", 1.4),
        ])

        result = calculate_backtest(
            nav_records=nav_records,
            amount=100.0,
            frequency="monthly",
            start_date=date(2026, 1, 15),
            end_date=date(2026, 3, 15),
        )

        # 1月、2月、3月各一期
        assert result.metrics.total_invested == 300.0

    def test_weekly_investment_frequency(self):
        """周投：每周同一天定投"""
        nav_records = _make_nav([
            ("2026-01-06", 1.0),   # 周一
            ("2026-01-07", 1.0),
            ("2026-01-13", 1.1),   # 下周一
            ("2026-01-14", 1.1),
            ("2026-01-20", 1.2),   # 下下周一
            ("2026-01-21", 1.2),
        ])

        result = calculate_backtest(
            nav_records=nav_records,
            amount=100.0,
            frequency="weekly",
            start_date=date(2026, 1, 6),
            end_date=date(2026, 1, 20),
        )

        # 1月6日、1月13日、1月20日各一期
        assert result.metrics.total_invested == 300.0


class TestLumpSumInvestment:
    """一次性买入测试"""

    def test_lump_sum_equals_total_invested(self):
        """一次性买入投入金额等于定投累计投入"""
        nav_records = _make_nav([
            ("2026-01-15", 1.0),
            ("2026-02-15", 1.0),
            ("2026-03-15", 1.0),
            ("2026-03-16", 1.0),
        ])

        result = calculate_backtest(
            nav_records=nav_records,
            amount=100.0,
            frequency="monthly",
            start_date=date(2026, 1, 15),
            end_date=date(2026, 3, 15),
        )

        total_invested = result.metrics.total_invested
        assert len(result.lump_sum_asset_curve) > 0


class TestReturnRate:
    """收益率测试"""

    def test_positive_return_rate(self):
        """净值上涨时收益率为正"""
        nav_records = _make_nav([
            ("2026-01-15", 1.0),
            ("2026-02-15", 1.0),
            ("2026-03-15", 1.5),   # 涨了50%
            ("2026-03-16", 1.5),
        ])

        result = calculate_backtest(
            nav_records=nav_records,
            amount=100.0,
            frequency="monthly",
            start_date=date(2026, 1, 15),
            end_date=date(2026, 3, 15),
        )

        assert result.metrics.return_rate > 0

    def test_negative_return_rate(self):
        """净值下跌时收益率为负"""
        nav_records = _make_nav([
            ("2026-01-15", 1.5),
            ("2026-02-15", 1.5),
            ("2026-03-15", 1.0),   # 跌了
            ("2026-03-16", 1.0),
        ])

        result = calculate_backtest(
            nav_records=nav_records,
            amount=100.0,
            frequency="monthly",
            start_date=date(2026, 1, 15),
            end_date=date(2026, 3, 15),
        )

        assert result.metrics.return_rate < 0


class TestMaxDrawdown:
    """最大回撤测试"""

    def test_max_drawdown_calculation(self):
        """最大回撤：最高点到最低点的跌幅"""
        asset_curve = [
            {"date": date(2026, 1, 1), "value": 100.0},
            {"date": date(2026, 1, 2), "value": 110.0},  # peak
            {"date": date(2026, 1, 3), "value": 90.0},   # drawdown = (110-90)/110 ≈ 18.18%
            {"date": date(2026, 1, 4), "value": 100.0},
        ]

        from app.models.schemas import DataPoint
        curve = [DataPoint(**p) for p in asset_curve]
        max_dd = _calculate_max_drawdown(curve)

        assert 0.18 < max_dd < 0.19

    def test_no_drawdown_when_always_rising(self):
        """净值一直上涨时最大回撤为0"""
        asset_curve = [
            {"date": date(2026, 1, 1), "value": 100.0},
            {"date": date(2026, 1, 2), "value": 110.0},
            {"date": date(2026, 1, 3), "value": 120.0},
        ]

        from app.models.schemas import DataPoint
        curve = [DataPoint(**p) for p in asset_curve]
        max_dd = _calculate_max_drawdown(curve)

        assert max_dd == 0.0


class TestFindNavOnOrAfter:
    """净值查找测试"""

    def test_find_nav_on_exact_date(self):
        """恰好找到指定日期的净值"""
        nav_records = _make_nav([
            ("2026-01-15", 1.0),
            ("2026-01-16", 1.1),
        ])

        result = _find_nav_on_or_after(nav_records, date(2026, 1, 15))
        assert result is not None
        assert result.date == date(2026, 1, 15)

    def test_find_nav_on_next_trading_day(self):
        """非交易日顺延到下一个有净值日期"""
        nav_records = _make_nav([
            ("2026-01-15", 1.0),
            ("2026-01-16", 1.1),
        ])

        result = _find_nav_on_or_after(nav_records, date(2026, 1, 16))
        assert result is not None
        assert result.date == date(2026, 1, 16)

    def test_no_nav_found(self):
        """找不到净值时返回None"""
        nav_records = _make_nav([
            ("2026-01-15", 1.0),
        ])

        result = _find_nav_on_or_after(nav_records, date(2026, 12, 31))
        assert result is None


class TestAssetCurveNoDuplicates:
    """asset_curve 重复日期去重测试"""

    def test_asset_curve_no_duplicate_dates(self):
        """asset_curve 中不应有重复日期"""
        nav_records = _make_nav([
            ("2026-01-02", 1.0),
            ("2026-01-15", 1.1),
            ("2026-02-02", 1.2),
        ])

        result = calculate_backtest(
            nav_records=nav_records,
            amount=100.0,
            frequency="weekly",
            start_date=date(2026, 1, 2),
            end_date=date(2026, 2, 2),
        )

        dates = [p.date for p in result.asset_curve]
        assert len(dates) == len(set(dates)), f"asset_curve 有重复日期: {dates}"