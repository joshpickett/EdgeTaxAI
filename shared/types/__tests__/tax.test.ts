import { 
  TaxCalculation, 
  TaxDeduction, 
  QuarterlyEstimate, 
  IRSCompliance,
  TaxOptimization 
} from '../tax';

describe('TaxCalculation Interface', () => {
  it('should create valid TaxCalculation object', () => {
    const calculation: TaxCalculation = {
      grossIncome: 75000,
      expenses: 15000,
      deductions: 10000,
      taxableIncome: 50000,
      estimatedTax: 10000,
      effectiveRate: 0.2
    };

    expect(calculation.grossIncome).toBeGreaterThan(0);
    expect(calculation.taxableIncome).toBe(
      calculation.grossIncome - calculation.expenses - calculation.deductions
    );
    expect(calculation.effectiveRate).toBeGreaterThan(0);
    expect(calculation.effectiveRate).toBeLessThan(1);
  });
});

describe('TaxDeduction Interface', () => {
  it('should create valid TaxDeduction object', () => {
    const deduction: TaxDeduction = {
      category: 'home_office',
      amount: 2500,
      description: 'Home office deduction',
      date: '2023-01-15',
      isVerified: true
    };

    expect(deduction.category).toBeDefined();
    expect(deduction.amount).toBeGreaterThan(0);
    expect(typeof deduction.isVerified).toBe('boolean');
    expect(new Date(deduction.date)).toBeInstanceOf(Date);
  });
});

describe('QuarterlyEstimate Interface', () => {
  it('should create valid QuarterlyEstimate object', () => {
    const estimate: QuarterlyEstimate = {
      quarter: 2,
      year: 2023,
      estimatedTax: 3500,
      dueDate: '2023-06-15',
      income: 15000,
      expenses: 4500
    };

    expect(estimate.quarter).toBeGreaterThan(0);
    expect(estimate.quarter).toBeLessThan(5);
    expect(estimate.year).toBeGreaterThan(2000);
    expect(new Date(estimate.dueDate)).toBeInstanceOf(Date);
    expect(estimate.estimatedTax).toBeGreaterThan(0);
  });
});

describe('IRSCompliance Interface', () => {
  it('should create valid IRSCompliance object', () => {
    const compliance: IRSCompliance = {
      isCompliant: true,
      missingDocumentation: ['1099-K'],
      suggestions: ['File quarterly estimates'],
      riskLevel: 'low'
    };

    expect(typeof compliance.isCompliant).toBe('boolean');
    expect(Array.isArray(compliance.missingDocumentation)).toBeTruthy();
    expect(Array.isArray(compliance.suggestions)).toBeTruthy();
    expect(['low', 'medium', 'high']).toContain(compliance.riskLevel);
  });
});

describe('TaxOptimization Interface', () => {
  it('should create valid TaxOptimization object', () => {
    const optimization: TaxOptimization = {
      suggestions: ['Increase retirement contributions'],
      potentialSavings: 2500,
      confidence: 0.85,
      category: 'retirement'
    };

    expect(Array.isArray(optimization.suggestions)).toBeTruthy();
    expect(optimization.potentialSavings).toBeGreaterThan(0);
    expect(optimization.confidence).toBeGreaterThan(0);
    expect(optimization.confidence).toBeLessThan(1);
    expect(optimization.category).toBeDefined();
  });
});
