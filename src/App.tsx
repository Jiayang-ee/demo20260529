import { useState, useEffect } from 'react';
import { Layout, Spin } from 'antd';
import FundForm from './components/FundForm';
import ResultsDisplay from './components/ResultsDisplay';
import ChartPanel from './components/ChartPanel';
import ErrorState from './components/ErrorState';
import EmptyState from './components/EmptyState';
import type { Fund, BacktestResult } from './types';
import { getMockFunds, getMockBacktestResult } from './api/mock';
import './App.css';

const { Header, Content } = Layout;

function App() {
  const [funds, setFunds] = useState<Fund[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadFunds();
  }, []);

  const loadFunds = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = getMockFunds();
      setFunds(data);
    } catch (err) {
      setError('获取基金列表失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values: {
    fund_code: string;
    amount: number;
    frequency: 'monthly' | 'weekly';
    start_date: string;
    end_date: string;
  }) => {
    setSubmitting(true);
    setError(null);
    try {
      const response = getMockBacktestResult(values) as { success: boolean; data?: BacktestResult; error?: string };
      if (response.success && response.data) {
        setResult(response.data);
      } else {
        setError(response.error || '回测请求失败');
      }
    } catch (err) {
      setError('回测请求失败，请稍后重试');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <h1>基金定投回测工具</h1>
      </Header>
      <Content className="app-content">
        <div className="container">
          {loading ? (
            <div className="loading-container">
              <Spin size="large" />
              <p>加载中...</p>
            </div>
          ) : error && !result ? (
            <ErrorState message={error} onRetry={loadFunds} />
          ) : (
            <>
              <div className="form-section">
                <FundForm
                  funds={funds}
                  loading={loading}
                  onSubmit={handleSubmit}
                  submitting={submitting}
                />
              </div>

              {result && (
                <>
                  <ResultsDisplay result={result} />
                  <ChartPanel result={result} />
                </>
              )}

              {!result && !loading && !error && (
                <EmptyState />
              )}
            </>
          )}
        </div>
      </Content>
    </Layout>
  );
}

export default App;