import React from 'react';
import { Result, Button } from 'antd';
import { TrendingUp } from 'lucide-react';

interface EmptyStateProps {
  onReset?: () => void;
}

const EmptyState: React.FC<EmptyStateProps> = ({ onReset }) => {
  return (
    <div className="empty-state">
      <Result
        icon={<TrendingUp size={64} style={{ color: '#1890ff' }} />}
        title="基金定投回测工具"
        subTitle="选择基金并设置参数，开始您的定投回测之旅"
        extra={
          onReset ? (
            <Button type="primary" onClick={onReset}>
              重新选择
            </Button>
          ) : null
        }
      />
    </div>
  );
};

export default EmptyState;