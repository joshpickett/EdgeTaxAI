export interface ReportParams {
  userId: string;
  startDate?: string;
  endDate?: string;
  year?: number;
  quarter?: number;
  categories?: string[];
  includeProjections?: boolean;
}

export interface TaxSummary {
  totalIncome: number;
  totalExpenses: number;
  netIncome: number;
  estimatedTax: number;
  deductions: Record<string, number>;
  categories: Record<string, number>;
}

export interface QuarterlyReport {
  quarter: number;
  year: number;
  income: number;
  expenses: number;
  taxEstimate: number;
  dueDate: string;
}

export interface CustomReport {
  data: any[];
  summary: {
    total: number;
    average: number;
    categories: Record<string, number>;
  };
}
