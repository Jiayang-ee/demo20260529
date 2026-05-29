import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { BacktestResult } from '../types';

interface NAVCurveChartProps {
  result: BacktestResult;
}

const NAVCurveChart: React.FC<NAVCurveChartProps> = ({ result }) => {
  const dates = result.nav_curve.map((p) => p.date);
  const navs = result.nav_curve.map((p) => p.nav);

  const option = {
    title: {
      text: '基金净值曲线',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: { axisValue: string; value: number }[]) => {
        return `<strong>${params[0].axisValue}</strong><br/>净值: ${params[0].value.toFixed(4)}`;
      },
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
      name: '净值',
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
        name: '净值',
        type: 'line',
        data: navs,
        smooth: true,
        itemStyle: { color: '#722ed1' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(114, 46, 209, 0.3)' },
              { offset: 1, color: 'rgba(114, 46, 209, 0.05)' },
            ],
          },
        },
      },
    ],
  };

  return (
    <div className="chart-container">
      <ReactECharts option={option} style={{ height: '350px' }} />
    </div>
  );
};

export default NAVCurveChart;