import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { BacktestResult } from '../types';

interface ReturnCurveChartProps {
  result: BacktestResult;
}

const ReturnCurveChart: React.FC<ReturnCurveChartProps> = ({ result }) => {
  const dates = result.return_curve.map((p) => p.date);
  const dcaReturns = result.return_curve.map((p) => p.dca_return);
  const lumpReturns = result.return_curve.map((p) => p.lump_sum_return);

  const option = {
    title: {
      text: '收益率曲线对比',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: { axisValue: string; seriesName: string; value: number; color: string }[]) => {
        let result = `<strong>${params[0].axisValue}</strong><br/>`;
        params.forEach((p) => {
          const sign = p.value >= 0 ? '+' : '';
          result += `${p.seriesName}: ${sign}${p.value.toFixed(2)}%<br/>`;
        });
        return result;
      },
    },
    legend: {
      data: ['定投收益率', '一次性买入收益率'],
      top: 30,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
      name: '收益率（%）',
      axisLabel: {
        formatter: (value: number) => `${value > 0 ? '+' : ''}${value}%`,
      },
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100,
      },
      {
        type: 'slider',
        start: 0,
        end: 100,
      },
    ],
    series: [
      {
        name: '定投收益率',
        type: 'line',
        data: dcaReturns,
        smooth: true,
        itemStyle: { color: '#1890ff' },
      },
      {
        name: '一次性买入收益率',
        type: 'line',
        data: lumpReturns,
        smooth: true,
        itemStyle: { color: '#52c41a' },
      },
    ],
  };

  return (
    <div className="chart-container">
      <ReactECharts option={option} style={{ height: '350px' }} />
    </div>
  );
};

export default ReturnCurveChart;