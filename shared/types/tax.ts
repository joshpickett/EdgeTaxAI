export interface TaxCalculation {
    grossIncome: number;
    expenses: number;
    deductions: number;
    taxableIncome: number;
    estimatedTax: number;
    effectiveRate: number;
}

export interface TaxDeduction {
    category: string;
    amount: number;
    description: string;
    date: string;
    isVerified: boolean;
}

export interface QuarterlyEstimate {
    quarter: number;
    year: number;
    estimatedTax: number;
    dueDate: string;
    income: number;
    expenses: number;
}

export interface IRSCompliance {
    isCompliant: boolean;
    missingDocumentation: string[];
    suggestions: string[];
    riskLevel: 'low' | 'medium' | 'high';
}

export interface TaxOptimization {
    suggestions: string[];
    potentialSavings: number;
    confidence: number;
    category: string;
}
