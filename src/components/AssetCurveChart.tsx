import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { BacktestResult } from '../types';

interface AssetCurveChartProps {
  result: BacktestResult;
}

const AssetCurveChart: React.FC<AssetCurveChartProps> = ({ result }) => {
  const dates = result.dca_curve.map((p) => p.date);
  const dcaAssets = result.dca_curve.map((p) => p.asset);
  const lumpAssets = result.lump_sum_curve.map((p) => p.asset);

  const option = {
    title: {
      text: '资产曲线对比',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: { axisValue: string; seriesName: string; value: number; color: string }[]) => {
        let result = `<strong>${params[0].axisValue}</strong><br/>`;
        params.forEach((p) => {
          result += `${p.seriesName}: ¥${p.value.toLocaleString('zh-CN')}<br/>`;
        });
        return result;
      },
    },
    legend: {
      data: ['定投资产', '一次性买入资产'],
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
      name: '资产（元）',
      axisLabel: {
        formatter: (value: number) => `¥${(value / 10000).toFixed(1)}万`,
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
        name: '定投资产',
        type: 'line',
        data: dcaAssets,
        smooth: true,
        itemStyle: { color: '#1890ff' },
      },
      {
        name: '一次性买入资产',
        type: 'line',
        data: lumpAssets,
        smooth: true,
        itemStyle: { color: '#52c41a' },
      },
    ],
  };

  return (
    <div className="chart-container">
      <ReactECharts option={option} style={{ height: '400px' }} />
    </div>
  );
};

export default AssetCurveChart;