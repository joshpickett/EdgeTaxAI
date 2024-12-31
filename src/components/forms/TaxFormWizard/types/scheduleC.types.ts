export interface BusinessInfo {
  name: string;
  ein: string;
  address: string;
  accountingMethod: 'cash' | 'accrual';
  businessCode: string;
  businessType: string;
  startDate: string;
}

export interface IncomeData {
  grossReceipts: number;
  returns: number;
  otherIncome: number;
  costOfGoods: {
    inventory: number;
    purchases: number;
    materials: number;
    labor: number;
  };
}

export interface ExpenseCategory {
  id: string;
  name: string;
  description: string;
  amount: number;
  documentIds?: string[];
}

export interface VehicleExpense {
  mileage: number;
  businessUsePercentage: number;
  vehicleDescription: string;
  datePlacedInService: string;
  actualExpenses?: {
    gas: number;
    maintenance: number;
    insurance: number;
    depreciation: number;
    other: number;
  };
}

export interface HomeOfficeExpense {
  totalSquareFeet: number;
  businessSquareFeet: number;
  percentage: number;
  expenses: {
    rent?: number;
    mortgage?: number;
    insurance: number;
    utilities: number;
    repairs: number;
    depreciation?: number;
  };
}

export interface ScheduleCTotals {
  grossIncome: number;
  totalExpenses: number;
  netProfit: number;
  vehicleExpenses: number;
  homeOfficeDeduction: number;
  selfEmploymentTax: number;
}

export interface ValidationResult {
  isValid: boolean;
  errors: Array<{
    field: string;
    message: string;
  }>;
  warnings: Array<{
    field: string;
    message: string;
  }>;
}

export interface CalculationResult {
  grossIncome: number;
  totalExpenses: number;
  netProfit: number;
  selfEmploymentTax: number;
  estimatedTax: number;
}

export interface ScheduleCData {
  businessInfo: BusinessInfo;
  income: IncomeData;
  expenses: ExpenseCategory[];
  vehicleExpense?: VehicleExpense;
  homeOffice?: HomeOfficeExpense;
  totals: ScheduleCTotals;
}
