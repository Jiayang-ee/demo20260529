import React from 'react';
import { Card, Statistic, Row, Col } from 'antd';
import type { Metrics } from '../types';

interface MetricsCardProps {
  title: string;
  metrics: Metrics;
  type: 'dca' | 'lump_sum';
}

const formatCurrency = (value: number) => `${value.toLocaleString('zh-CN')} 元`;
const formatPercent = (value: number) => `${value > 0 ? '+' : ''}${value}%`;

const MetricsCard: React.FC<MetricsCardProps> = ({ title, metrics, type }) => {
  const isPositive = metrics.return_rate >= 0;

  return (
    <Card
      title={title}
      className={`metrics-card metrics-card--${type}`}
      styles={{ body: { padding: '16px' } }}
    >
      <Row gutter={[16, 16]}>
        <Col xs={12} sm={8}>
          <Statistic
            title="累计投入"
            value={metrics.total_invested}
            formatter={(val) => formatCurrency(Number(val))}
            valueStyle={{ fontSize: '16px', color: '#1890ff' }}
          />
        </Col>
        <Col xs={12} sm={8}>
          <Statistic
            title="期末资产"
            value={metrics.final_asset}
            formatter={(val) => formatCurrency(Number(val))}
            valueStyle={{ fontSize: '16px', color: isPositive ? '#52c41a' : '#ff4d4f' }}
          />
        </Col>
        <Col xs={12} sm={8}>
          <Statistic
            title="总收益"
            value={metrics.total_return}
            formatter={(val) => formatCurrency(Number(val))}
            valueStyle={{ fontSize: '16px', color: isPositive ? '#52c41a' : '#ff4d4f' }}
          />
        </Col>
        <Col xs={12} sm={8}>
          <Statistic
            title="收益率"
            value={metrics.return_rate}
            formatter={(val) => formatPercent(Number(val))}
            valueStyle={{ fontSize: '18px', fontWeight: 'bold', color: isPositive ? '#52c41a' : '#ff4d4f' }}
          />
        </Col>
        <Col xs={12} sm={8}>
          <Statistic
            title="最大回撤"
            value={metrics.max_drawdown}
            formatter={(val) => `${val}%`}
            valueStyle={{ fontSize: '16px', color: '#ff4d4f' }}
          />
        </Col>
      </Row>
    </Card>
  );
};

export default MetricsCard;