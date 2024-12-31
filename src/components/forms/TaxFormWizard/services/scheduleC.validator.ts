import { 
  BusinessInfo, 
  IncomeData, 
  ExpenseCategory, 
  ValidationResult,
  ScheduleCData 
} from '../types/scheduleC.types';

export class ScheduleCValidator {
  validateBusinessInfo(data: BusinessInfo): ValidationResult {
    const errors = [];
    const warnings = [];

    if (!data.name) {
      errors.push({
        field: 'name',
        message: 'Business name is required'
      });
    }

    if (!data.ein) {
      errors.push({
        field: 'ein',
        message: 'EIN is required'
      });
    } else if (!/^\d{2}-\d{7}$/.test(data.ein)) {
      errors.push({
        field: 'ein',
        message: 'EIN must be in format XX-XXXXXXX'
      });
    }

    if (!data.businessType) {
      errors.push({
        field: 'businessType',
        message: 'Business type is required'
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  validateIncome(data: IncomeData): ValidationResult {
    const errors = [];
    const warnings = [];

    if (data.grossReceipts < 0) {
      errors.push({
        field: 'grossReceipts',
        message: 'Gross receipts cannot be negative'
      });
    }

    if (data.returns > data.grossReceipts) {
      warnings.push({
        field: 'returns',
        message: 'Returns exceed gross receipts'
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  validateExpenses(expenses: ExpenseCategory[]): ValidationResult {
    const errors = [];
    const warnings = [];

    expenses.forEach(expense => {
      if (expense.amount < 0) {
        errors.push({
          field: `expense_${expense.id}`,
          message: `${expense.name} amount cannot be negative`
        });
      }
    });

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  validateComplete(data: ScheduleCData): ValidationResult {
    const errors = [];
    const warnings = [];

    // Combine all validations
    const businessValidation = this.validateBusinessInfo(data.businessInfo);
    const incomeValidation = this.validateIncome(data.income);
    const expenseValidation = this.validateExpenses(data.expenses);

    errors.push(...businessValidation.errors);
    errors.push(...incomeValidation.errors);
    errors.push(...expenseValidation.errors);
    
    warnings.push(...businessValidation.warnings);
    warnings.push(...incomeValidation.warnings);
    warnings.push(...expenseValidation.warnings);

    // Cross-section validations
    if (data.totals.netProfit < -100000) {
      warnings.push({
        field: 'netProfit',
        message: 'Large net loss may require additional documentation'
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
}
