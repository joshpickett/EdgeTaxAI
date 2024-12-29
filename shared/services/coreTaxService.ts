import { 
  TaxCalculationResult, 
  TaxDeduction, 
  TaxForm, 
  TaxContext,
  DeductionCategory,
  DocumentationStatus 
} from '../types/tax';
import { ApiClient } from './apiClient';
import { CacheManager } from './cacheManager';
import { OfflineQueueManager } from './offlineQueueManager';

export class CoreTaxService {
  private apiClient: ApiClient;
  private cacheManager: CacheManager;
  private offlineQueue: OfflineQueueManager;
  private readonly TAX_RATES = {
    selfEmployment: 0.153,
    standardDeduction: 12950,
    brackets: [
      { min: 0, max: 10275, rate: 0.10 },
      { min: 10276, max: 41775, rate: 0.12 },
      { min: 41776, max: 89075, rate: 0.22 },
      { min: 89076, max: 170050, rate: 0.24 },
      { min: 170051, max: 215950, rate: 0.32 },
      { min: 215951, max: 539900, rate: 0.35 },
      { min: 539901, max: Infinity, rate: 0.37 }
    ]
  };

  constructor() {
    this.apiClient = new ApiClient();
    this.cacheManager = new CacheManager();
    this.offlineQueue = new OfflineQueueManager();
  }

  async calculateTax(income: number, expenses: number, context: TaxContext): Promise<TaxCalculationResult> {
    try {
      const cacheKey = `tax_calc_${income}_${expenses}_${context.year}_${context.quarter}`;
      const cached = await this.cacheManager.get(cacheKey);
      
      if (cached) {
        return cached;
      }

      const taxableIncome = Math.max(income - expenses, 0);
      const selfEmploymentTax = this.calculateSelfEmploymentTax(taxableIncome);
      const incomeTax = this.calculateIncomeTax(taxableIncome);
      
      const result: TaxCalculationResult = {
        quarterlyAmount: (selfEmploymentTax + incomeTax) / 4,
        annualEstimate: selfEmploymentTax + incomeTax,
        effectiveRate: (selfEmploymentTax + incomeTax) / taxableIncome,
        dueDate: this.calculateDueDate(context.quarter || 1),
        calculations: {
          grossIncome: income,
          totalDeductions: expenses,
          taxableIncome,
          selfEmploymentTax,
          incomeTax
        }
      };

      await this.cacheManager.set(cacheKey, result, 3600);
      return result;
    } catch (error) {
      if (!navigator.onLine) {
        await this.offlineQueue.addToQueue('calculateTax', { income, expenses, context });
      }
      throw error;
    }
  }

  async analyzeDeductions(expenses: any[]): Promise<TaxDeduction[]> {
    try {
      const deductions = expenses.map(expense => ({
        id: expense.id,
        category: this.categorizeExpense(expense),
        amount: expense.amount,
        description: expense.description,
        isEligible: this.checkDeductionEligibility(expense),
        savings: this.calculateDeductionSavings(expense.amount),
        documentation: this.validateDocumentation(expense)
      }));

      return deductions;
    } catch (error) {
      if (!navigator.onLine) {
        await this.offlineQueue.addToQueue('analyzeDeductions', { expenses });
      }
      throw error;
    }
  }

  private calculateSelfEmploymentTax(income: number): number {
    return income * this.TAX_RATES.selfEmployment;
  }

  private calculateIncomeTax(income: number): number {
    let tax = 0;
    let remainingIncome = income;

    for (const bracket of this.TAX_RATES.brackets) {
      const taxableInBracket = Math.min(
        Math.max(0, remainingIncome),
        bracket.max - bracket.min
      );
      tax += taxableInBracket * bracket.rate;
      remainingIncome -= taxableInBracket;
      if (remainingIncome <= 0) break;
    }

    return tax;
  }

  private calculateDueDate(quarter: number): string {
    const year = new Date().getFullYear();
    const dueDates = {
      1: `${year}-04-15`,
      2: `${year}-06-15`,
      3: `${year}-09-15`,
      4: `${year + 1}-01-15`
    };
    return dueDates[quarter] || dueDates[1];
  }

  private categorizeExpense(expense: any): DeductionCategory {
    // Implement expense categorization logic
    return DeductionCategory.BUSINESS;
  }

  private checkDeductionEligibility(expense: any): boolean {
    // Implement deduction eligibility rules
    return true;
  }

  private calculateDeductionSavings(amount: number): number {
    return amount * this.TAX_RATES.brackets[0].rate;
  }

  private validateDocumentation(expense: any): DocumentationStatus {
    // Implement documentation validation logic
    return DocumentationStatus.COMPLETE;
  }
}

export const coreTaxService = new CoreTaxService();
