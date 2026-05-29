"""数据模型"""
from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class FundBase(BaseModel):
    """基金基本信息"""
    code: str = Field(..., description="基金代码")
    name: str = Field(..., description="基金名称")


class Fund(FundBase):
    """基金完整信息"""
    fund_type: str = Field(..., description="基金类型")
    nav_start_date: Optional[date] = Field(None, description="净值数据开始日期")
    nav_end_date: Optional[date] = Field(None, description="净值数据结束日期")
    cached: bool = Field(False, description="是否已缓存本地数据")


class FundNavRecord(BaseModel):
    """基金净值记录"""
    date: date
    unit_nav: float = Field(..., description="单位净值")
    accumulated_nav: Optional[float] = Field(None, description="累计净值")
    fetched_at: str = Field(..., description="抓取时间 ISO 格式")
    source: str = Field(default="east_money", description="数据来源")


class BacktestRequest(BaseModel):
    """回测请求参数"""
    fund_code: str = Field(..., description="基金代码")
    amount: float = Field(..., gt=0, description="每期定投金额")
    frequency: Literal["monthly", "weekly"] = Field(..., description="定投频率")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v, info):
        if "start_date" in info.data and v <= info.data["start_date"]:
            raise ValueError("结束日期不能早于开始日期")
        return v


class DataPoint(BaseModel):
    """曲线数据点"""
    date: date
    value: float


class BacktestMetrics(BaseModel):
    """回测关键指标"""
    total_invested: float = Field(..., description="累计投入")
    final_asset: float = Field(..., description="期末资产")
    total_return: float = Field(..., description="总收益")
    return_rate: float = Field(..., description="收益率")
    max_drawdown: float = Field(..., description="最大回撤")


class BacktestResult(BaseModel):
    """回测结果"""
    metrics: BacktestMetrics
    asset_curve: list[DataPoint] = Field(..., description="资产曲线")
    lump_sum_asset_curve: list[DataPoint] = Field(..., description="一次性买入资产曲线")
    fund_nav_curve: list[DataPoint] = Field(..., description="基金净值曲线")
    return_rate_curve: list[DataPoint] = Field(..., description="收益率曲线")