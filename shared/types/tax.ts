export enum FilingStatus {
  SINGLE = 'single',
  MARRIED_JOINT = 'married_joint',
  MARRIED_SEPARATE = 'married_separate',
  HEAD_OF_HOUSEHOLD = 'head_of_household'
}

export enum BusinessType {
  SOLE_PROPRIETOR = 'sole_proprietor',
  LLC = 'llc',
  PARTNERSHIP = 'partnership',
  CORPORATION = 'corporation'
}

export enum DeductionCategory {
  BUSINESS = 'business',
  PERSONAL = 'personal',
  MEDICAL = 'medical',
  CHARITABLE = 'charitable',
  OTHER = 'other'
}

export enum DocumentationStatus {
  COMPLETE = 'complete',
  PARTIAL = 'partial',
  MISSING = 'missing',
  INVALID = 'invalid'
}

export interface TaxContext {
  year: number;
  quarter?: number;
  isAmended: boolean;
  filingStatus: FilingStatus;
  businessType: BusinessType;
}

export interface TaxCalculationResult {
  quarterlyAmount: number;
  annualEstimate: number;
  effectiveRate: number;
  dueDate: string;
  calculations?: {
    grossIncome: number;
    totalDeductions: number;
    taxableIncome: number;
    selfEmploymentTax: number;
    incomeTax: number;
  };
}

export interface TaxDeduction {
  id: string;
  category: DeductionCategory;
  amount: number;
  description: string;
  isEligible: boolean;
  savings: number;
  documentation: DocumentationStatus;
}

export interface TaxForm {
  id: string;
  type: string;
  data: any;
  status: string;
  submissionDate?: string;
  acknowledgmentDate?: string;
  errors?: Array<{
    code: string;
    message: string;
  }>;
}
