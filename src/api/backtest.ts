import type { Fund, BacktestParams, BacktestResponse } from '../types';

const API_BASE = '/api';

export async function fetchFunds(): Promise<Fund[]> {
  const response = await fetch(`${API_BASE}/funds`);
  if (!response.ok) {
    throw new Error('获取基金列表失败');
  }
  return response.json();
}

export async function submitBacktest(params: BacktestParams): Promise<BacktestResponse> {
  const response = await fetch(`${API_BASE}/backtest`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });
  if (!response.ok) {
    throw new Error('提交回测失败');
  }
  return response.json();
}