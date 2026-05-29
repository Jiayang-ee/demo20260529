import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

const MOCK_FUNDS = [
  { code: '000001', name: '华夏成长混合', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '000021', name: '华夏优势增长混合', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '000083', name: '汇添富消费行业混合', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '000263', name: '工银信息产业混合A', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '000336', name: '农银研究精选混合', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '000478', name: '建信中证500指数增强A', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '000596', name: '前海开源中证军工指数A', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '001054', name: '工银新金融股票A', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '001410', name: '信澳新能源产业股票', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '110011', name: '易方达中小盘混合', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '012922', name: '易方达全球成长精选混合(QDII)C', min_date: '2020-01-01', max_date: '2026-05-28' },
];

function generateMockNAV(startDate: string, endDate: string): { date: string; nav: number }[] {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const dates: { date: string; nav: number }[] = [];
  let nav = 1.0;
  const dailyReturn = 0.0002;
  const volatility = 0.015;

  let current = start;
  while (current <= end) {
    const day = current.getDay();
    if (day !== 0 && day !== 6) {
      const randomChange = (Math.random() - 0.5) * 2 * volatility + dailyReturn;
      nav = nav * (1 + randomChange);
      dates.push({
        date: current.toISOString().split('T')[0],
        nav: Math.round(nav * 10000) / 10000,
      });
    }
    current.setDate(current.getDate() + 1);
  }
  return dates;
}

function simulateDCA(
  navData: { date: string; nav: number }[],
  amount: number,
  frequency: 'monthly' | 'weekly'
): { date: string; asset: number; nav: number }[] {
  const curve: { date: string; asset: number; nav: number }[] = [];
  let totalShares = 0;
  let totalInvested = 0;
  let lastTriggerDate: Date | null = null;

  for (const data of navData) {
    const current = new Date(data.date);
    if (lastTriggerDate === null) {
      lastTriggerDate = current;
    }

    const diffTime = current.getTime() - lastTriggerDate.getTime();
    const diffDays = diffTime / (1000 * 60 * 60 * 24);
    const shouldTrigger =
      frequency === 'weekly' ? diffDays >= 7 : diffDays >= 30;

    if (shouldTrigger) {
      totalShares += amount / data.nav;
      totalInvested += amount;
      lastTriggerDate = current;
    }

    curve.push({
      date: data.date,
      asset: Math.round(totalShares * data.nav * 100) / 100,
      nav: data.nav,
    });
  }

  return curve;
}

function simulateLumpSum(
  navData: { date: string; nav: number }[],
  totalAmount: number
): { date: string; asset: number; nav: number }[] {
  const curve: { date: string; asset: number; nav: number }[] = [];
  const firstNav = navData[0]?.nav || 1;
  const totalShares = totalAmount / firstNav;

  for (const data of navData) {
    curve.push({
      date: data.date,
      asset: Math.round(totalShares * data.nav * 100) / 100,
      nav: data.nav,
    });
  }

  return curve;
}

function calculateMetrics(
  curve: { date: string; asset: number; nav: number }[],
  totalInvested: number
) {
  const finalAsset = curve[curve.length - 1]?.asset || 0;
  const totalReturn = finalAsset - totalInvested;
  const returnRate = totalInvested > 0 ? (totalReturn / totalInvested) * 100 : 0;

  let maxDrawdown = 0;
  let peak = 0;
  for (const point of curve) {
    if (point.asset > peak) {
      peak = point.asset;
    }
    const drawdown = peak > 0 ? (peak - point.asset) / peak : 0;
    if (drawdown > maxDrawdown) {
      maxDrawdown = drawdown;
    }
  }

  return {
    total_invested: totalInvested,
    final_asset: Math.round(finalAsset * 100) / 100,
    total_return: Math.round(totalReturn * 100) / 100,
    return_rate: Math.round(returnRate * 100) / 100,
    max_drawdown: Math.round(maxDrawdown * 10000) / 100,
  };
}

function diffMonths(start: Date, end: Date): number {
  return (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1;
}

function diffWeeks(start: Date, end: Date): number {
  return Math.floor((end.getTime() - start.getTime()) / (7 * 24 * 60 * 60 * 1000)) + 1;
}

// GET /api/funds
app.get('/api/funds', (_req, res) => {
  res.json(MOCK_FUNDS);
});

// POST /api/backtest
app.post('/api/backtest', (req, res) => {
  const { fund_code, amount, frequency, start_date, end_date } = req.body;

  if (!fund_code || !amount || !frequency || !start_date || !end_date) {
    return res.status(400).json({ success: false, error: 'Missing required parameters' });
  }

  if (amount <= 0) {
    return res.status(400).json({ success: false, error: 'Amount must be positive' });
  }

  if (!['monthly', 'weekly'].includes(frequency)) {
    return res.status(400).json({ success: false, error: 'Frequency must be monthly or weekly' });
  }

  const navData = generateMockNAV(start_date, end_date);
  const start = new Date(start_date);
  const end = new Date(end_date);
  const totalPeriods = frequency === 'monthly' ? diffMonths(start, end) : diffWeeks(start, end);
  const totalInvested = amount * totalPeriods;

  const dcaCurve = simulateDCA(navData, amount, frequency);
  const lumpSumCurve = simulateLumpSum(navData, totalInvested);

  const return_curve = navData.map((nav, index) => {
    const dcaAsset = dcaCurve[index]?.asset || 0;
    const lumpAsset = lumpSumCurve[index]?.asset || 0;
    const dcaReturn = totalInvested > 0 ? ((dcaAsset - totalInvested) / totalInvested) * 100 : 0;
    const lumpReturn = totalInvested > 0 ? ((lumpAsset - totalInvested) / totalInvested) * 100 : 0;
    return {
      date: nav.date,
      dca_return: Math.round(dcaReturn * 100) / 100,
      lump_sum_return: Math.round(lumpReturn * 100) / 100,
    };
  });

  res.json({
    success: true,
    data: {
      dca_metrics: calculateMetrics(dcaCurve, totalInvested),
      lump_sum_metrics: calculateMetrics(lumpSumCurve, totalInvested),
      dca_curve: dcaCurve,
      lump_sum_curve: lumpSumCurve,
      nav_curve: navData,
      return_curve,
    },
  });
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
});
