import React from 'react';
import { Row, Col } from 'antd';
import type { BacktestResult } from '../types';
import MetricsCard from './MetricsCard';

interface ResultsDisplayProps {
  result: BacktestResult;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ result }) => {
  return (
    <div className="results-display">
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <MetricsCard
            title="定投策略"
            metrics={result.dca_metrics}
            type="dca"
          />
        </Col>
        <Col xs={24} lg={12}>
          <MetricsCard
            title="一次性买入"
            metrics={result.lump_sum_metrics}
            type="lump_sum"
          />
        </Col>
      </Row>

      <div className="disclaimer">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span>仅用于历史回测，不构成投资建议</span>
      </div>
    </div>
  );
};

export default ResultsDisplay;