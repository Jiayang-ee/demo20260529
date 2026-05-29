import dayjs from 'dayjs';

const MOCK_FUNDS = [
  { code: '000001', name: '上证指数ETF', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '159919', name: '沪深300ETF', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '510050', name: '上证50ETF', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '159915', name: '创业板ETF', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '512880', name: '证券ETF', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '515000', name: '科技ETF', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '159941', name: '纳指ETF', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '513500', name: '标普500ETF', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '518880', name: '黄金ETF', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '000012', name: '国债ETF', min_date: '2020-01-01', max_date: '2026-05-28' },
  { code: '012922', name: '易方达全球成长精选混合(QDII)C', min_date: '2020-01-01', max_date: '2026-05-28' },
];

function generateMockNAV(startDate: string, endDate: string): { date: string; nav: number }[] {
  const start = dayjs(startDate);
  const end = dayjs(endDate);
  const dates: { date: string; nav: number }[] = [];
  let nav = 1.0;
  const dailyReturn = 0.0002;
  const volatility = 0.015;

  let current = start;
  while (current.isBefore(end) || current.isSame(end, 'day')) {
    const weekday = current.day();
    if (weekday !== 0 && weekday !== 6) {
      const randomChange = (Math.random() - 0.5) * 2 * volatility + dailyReturn;
      nav = nav * (1 + randomChange);
      dates.push({
        date: current.format('YYYY-MM-DD'),
        nav: Math.round(nav * 10000) / 10000,
      });
    }
    current = current.add(1, 'day');
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
  let lastTriggerDate: dayjs.Dayjs | null = null;


  for (const data of navData) {
    const current = dayjs(data.date);
    if (lastTriggerDate === null) {
      lastTriggerDate = current;
    }

    const shouldTrigger =
      frequency === 'weekly'
        ? current.diff(lastTriggerDate, 'week') >= 1
        : current.diff(lastTriggerDate, 'month') >= 1;

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
    const drawdown = (peak - point.asset) / peak;
    if (drawdown > maxDrawdown) {
      maxDrawdown = drawdown;
    }
  }

  return {
    total_invested: totalInvested,
    final_asset: finalAsset,
    total_return: Math.round(totalReturn * 100) / 100,
    return_rate: Math.round(returnRate * 100) / 100,
    max_drawdown: Math.round(maxDrawdown * 10000) / 100,
  };
}

export function getMockFunds() {
  return MOCK_FUNDS;
}

export function getMockBacktestResult(params: {
  fund_code: string;
  amount: number;
  frequency: 'monthly' | 'weekly';
  start_date: string;
  end_date: string;
}) {
  const navData = generateMockNAV(params.start_date, params.end_date);
  const totalPeriods = params.frequency === 'monthly'
    ? dayjs(params.end_date).diff(dayjs(params.start_date), 'month') + 1
    : dayjs(params.end_date).diff(dayjs(params.start_date), 'week') + 1;
  const totalInvested = params.amount * totalPeriods;

  const dcaCurve = simulateDCA(navData, params.amount, params.frequency);
  const lumpSumCurve = simulateLumpSum(navData, totalInvested);

  return {
    success: true,
    data: {
      dca_metrics: calculateMetrics(dcaCurve, totalInvested),
      lump_sum_metrics: calculateMetrics(lumpSumCurve, totalInvested),
      dca_curve: dcaCurve,
      lump_sum_curve: lumpSumCurve,
      nav_curve: navData,
      return_curve: navData.map((nav, index) => {
        const dcaAsset = dcaCurve[index]?.asset || 0;
        const lumpAsset = lumpSumCurve[index]?.asset || 0;
        const dcaReturn = totalInvested > 0 ? ((dcaAsset - totalInvested) / totalInvested) * 100 : 0;
        const lumpReturn = totalInvested > 0 ? ((lumpAsset - totalInvested) / totalInvested) * 100 : 0;
        return {
          date: nav.date,
          dca_return: Math.round(dcaReturn * 100) / 100,
          lump_sum_return: Math.round(lumpReturn * 100) / 100,
        };
      }),
    },
  };
}