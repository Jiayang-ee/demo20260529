export interface Fund {
  code: string;
  name: string;
  min_date: string;
  max_date: string;
}

export interface BacktestParams {
  fund_code: string;
  amount: number;
  frequency: 'monthly' | 'weekly';
  start_date: string;
  end_date: string;
}

export interface Metrics {
  total_invested: number;
  final_asset: number;
  total_return: number;
  return_rate: number;
  max_drawdown: number;
  sharpe_ratio?: number;
}

export interface BacktestResult {
  dca_metrics: Metrics;
  lump_sum_metrics: Metrics;
  dca_curve: { date: string; asset: number; nav: number }[];
  lump_sum_curve: { date: string; asset: number; nav: number }[];
  nav_curve: { date: string; nav: number }[];
  return_curve: { date: string; dca_return: number; lump_sum_return: number }[];
}

export interface BacktestResponse {
  success: boolean;
  data?: BacktestResult;
  error?: string;
}