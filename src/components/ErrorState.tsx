import React from 'react';
import { Button, Result } from 'antd';
import { RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  message: string;
  onRetry: () => void;
}

const ErrorState: React.FC<ErrorStateProps> = ({ message, onRetry }) => {
  return (
    <div className="error-state">
      <Result
        status="error"
        title="请求失败"
        subTitle={message}
        extra={
          <Button type="primary" icon={<RefreshCw size={16} />} onClick={onRetry}>
            重试
          </Button>
        }
      />
    </div>
  );
};

export default ErrorState;