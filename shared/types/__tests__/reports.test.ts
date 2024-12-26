import { ReportParams, TaxSummary, QuarterlyReport, CustomReport } from '../reports';

describe('ReportParams Interface', () => {
  it('should create valid ReportParams object', () => {
    const params: ReportParams = {
      userId: '123',
      startDate: '2023-01-01',
      endDate: '2023-12-31',
      year: 2023,
      quarter: 2,
      categories: ['business', 'travel'],
      includeProjections: true
    };

    expect(params.userId).toBeDefined();
    expect(typeof params.userId).toBe('string');
    expect(params.startDate).toBeDefined();
    expect(params.endDate).toBeDefined();
  });

  it('should allow optional parameters', () => {
    const minimalParams: ReportParams = {
      userId: '123'
    };

    expect(minimalParams.userId).toBeDefined();
    expect(minimalParams.startDate).toBeUndefined();
    expect(minimalParams.categories).toBeUndefined();
  });
});

describe('TaxSummary Interface', () => {
  it('should create valid TaxSummary object', () => {
    const summary: TaxSummary = {
      totalIncome: 50000,
      totalExpenses: 15000,
      netIncome: 35000,
      estimatedTax: 7000,
      deductions: {
        'home_office': 2000,
        'equipment': 3000
      },
      categories: {
        'business': 10000,
        'travel': 5000
      }
    };

    expect(summary.totalIncome).toBeGreaterThan(0);
    expect(summary.netIncome).toBe(summary.totalIncome - summary.totalExpenses);
    expect(Object.keys(summary.deductions)).toBeDefined();
    expect(Object.keys(summary.categories)).toBeDefined();
  });
});

describe('QuarterlyReport Interface', () => {
  it('should create valid QuarterlyReport object', () => {
    const report: QuarterlyReport = {
      quarter: 1,
      year: 2023,
      income: 12500,
      expenses: 3750,
      taxEstimate: 1750,
      dueDate: '2023-04-15'
    };

    expect(report.quarter).toBeGreaterThan(0);
    expect(report.quarter).toBeLessThan(5);
    expect(report.year).toBeGreaterThan(2000);
    expect(new Date(report.dueDate)).toBeInstanceOf(Date);
  });
});

describe('CustomReport Interface', () => {
  it('should create valid CustomReport object', () => {
    const report: CustomReport = {
      data: [
        { id: 1, amount: 100 },
        { id: 2, amount: 200 }
      ],
      summary: {
        total: 300,
        average: 150,
        categories: {
          'business': 200,
          'personal': 100
        }
      }
    };

    expect(Array.isArray(report.data)).toBeTruthy();
    expect(report.summary.total).toBe(300);
    expect(report.summary.average).toBe(150);
    expect(Object.keys(report.summary.categories)).toBeDefined();
  });
});
