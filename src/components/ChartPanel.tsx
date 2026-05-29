import React from 'react';
import { Tabs } from 'antd';
import type { BacktestResult } from '../types';
import AssetCurveChart from './AssetCurveChart';
import NAVCurveChart from './NAVCurveChart';
import ReturnCurveChart from './ReturnCurveChart';

interface ChartPanelProps {
  result: BacktestResult;
}

const ChartPanel: React.FC<ChartPanelProps> = ({ result }) => {
  return (
    <div className="chart-panel">
      <Tabs
        defaultActiveKey="asset"
        items={[
          {
            key: 'asset',
            label: '资产曲线',
            children: <AssetCurveChart result={result} />,
          },
          {
            key: 'nav',
            label: '净值曲线',
            children: <NAVCurveChart result={result} />,
          },
          {
            key: 'return',
            label: '收益率曲线',
            children: <ReturnCurveChart result={result} />,
          },
        ]}
      />
    </div>
  );
};

export default ChartPanel;