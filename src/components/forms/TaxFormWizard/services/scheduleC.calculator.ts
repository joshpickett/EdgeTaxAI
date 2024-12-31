import { 
  ScheduleCData, 
  ScheduleCTotals,
  IncomeData,
  ExpenseCategory 
} from '../types/scheduleC.types';

export class ScheduleCCalculator {
  calculateGrossIncome(income: IncomeData): number {
    const { grossReceipts, returns, otherIncome, costOfGoods } = income;
    const totalCostOfGoods = Object.values(costOfGoods).reduce((sum, val) => sum + val, 0);
    return grossReceipts - returns + otherIncome - totalCostOfGoods;
  }

  calculateTotalExpenses(expenses: ExpenseCategory[]): number {
    return expenses.reduce((sum, expense) => sum + expense.amount, 0);
  }

  calculateNetProfit(grossIncome: number, totalExpenses: number): number {
    return grossIncome - totalExpenses;
  }

  calculateSelfEmploymentTax(netProfit: number): number {
    const taxableIncome = netProfit * 0.9235; // 92.35% of net profit is taxable
    return taxableIncome * 0.153; // 15.3% self-employment tax rate
  }

  calculateEstimatedTax(netProfit: number): number {
    // Simplified calculation - actual calculation would be more complex
    const estimatedTaxRate = 0.25; // 25% estimated tax rate
    return netProfit * estimatedTaxRate;
  }

  calculateTotals(data: ScheduleCData): ScheduleCTotals {
    const grossIncome = this.calculateGrossIncome(data.income);
    const totalExpenses = this.calculateTotalExpenses(data.expenses);
    const netProfit = this.calculateNetProfit(grossIncome, totalExpenses);
    
    return {
      grossIncome,
      totalExpenses,
      netProfit,
      vehicleExpenses: data.vehicleExpense?.actualExpenses 
        ? Object.values(data.vehicleExpense.actualExpenses).reduce((sum, val) => sum + val, 0)
        : data.vehicleExpense?.mileage * 0.655, // 2023 standard mileage rate
      homeOfficeDeduction: data.homeOffice 
        ? Object.values(data.homeOffice.expenses).reduce((sum, val) => sum + (val || 0), 0) * 
          (data.homeOffice.percentage / 100)
        : 0,
      selfEmploymentTax: this.calculateSelfEmploymentTax(netProfit)
    };
  }
}
