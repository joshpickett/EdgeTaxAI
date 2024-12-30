import { FormStatus } from './common';

export interface IRSFormField {
  id: string;
  name: string;
  label: string;
  type: 'text' | 'number' | 'date' | 'select' | 'checkbox';
  required: boolean;
  validation?: {
    pattern?: string;
    min?: number;
    max?: number;
    message?: string;
  };
  options?: Array<{
    value: string;
    label: string;
  }>;
  helpText?: string;
  placeholder?: string;
  dependsOn?: string;
}

export interface IRSFormSection {
  id: string;
  title: string;
  description?: string;
  fields: IRSFormField[];
}

export interface IRSFormTemplate {
  id: string;
  type: string;
  version: string;
  year: number;
  sections: IRSFormSection[];
  validations: IRSValidationRule[];
}

export interface IRSValidationRule {
  field: string;
  type: 'required' | 'pattern' | 'range' | 'dependency';
  value?: any;
  message: string;
  severity: 'error' | 'warning';
}

export interface IRSFormData {
  id?: string;
  templateId: string;
  status: FormStatus;
  data: Record<string, any>;
  validation?: {
    isValid: boolean;
    errors: Array<{
      field: string;
      message: string;
    }>;
  };
}

export interface Form1099KRequired {
  // Payment Settlement Entity (PSE) Information - Required
  pse: {
    name: string;          // Required
    tin: string;           // Required - Tax ID Number
    phone: string;         // Required
    address: {
      street: string;      // Required
      city: string;        // Required
      state: string;       // Required
      zipCode: string;     // Required
    };
  };
  
  // Payee Information - Required
  payee: {
    name: string;          // Required
    tin: string;          // Required - Tax ID Number
    address: {
      street: string;      // Required
      city: string;        // Required
      state: string;       // Required
      zipCode: string;     // Required
    };
  };
  
  // Transaction Information - Required
  transactions: {
    grossAmount: number;              // Required
    cardNotPresent: number;           // Required
    paymentCardTransactions: number;  // Required
    thirdPartyNetwork: number;        // Required
    monthlyAmounts: {                 // Required
      month1: number;
      month2: number;
      month3: number;
      month4: number;
      month5: number;
      month6: number;
      month7: number;
      month8: number;
      month9: number;
      month10: number;
      month11: number;
      month12: number;
    };
  };
}

export interface Form1099NECRequired {
  // Payer Information - Required
  payer: {
    name: string;          // Required
    tin: string;           // Required - Tax ID Number
    phone: string;         // Required
    address: {
      street: string;      // Required
      city: string;        // Required
      state: string;       // Required
      zipCode: string;     // Required
    };
  };
  
  // Recipient Information - Required
  recipient: {
    name: string;          // Required
    tin: string;           // Required - Tax ID Number
    address: {
      street: string;      // Required
      city: string;        // Required
      state: string;       // Required
      zipCode: string;     // Required
    };
  };
  
  // Payment Information - Required
  payments: {
    nonemployeeCompensation: number;  // Required if over $600
    federalTaxWithheld: number;       // Required if tax was withheld
  };
}

export interface ScheduleCRequired {
  // Business Information - Required
  businessInfo: {
    name: string;                     // Required
    ein?: string;                     // Optional - Employer ID Number
    address: {
      street: string;                 // Required
      city: string;                   // Required
      state: string;                  // Required
      zipCode: string;                // Required
    };
    accountingMethod: 'Cash' | 'Accrual';  // Required
  };
  
  // Income - Required
  income: {
    grossReceipts: number;            // Required
    returns: number;                  // Required if applicable
    otherIncome: number;              // Required if applicable
    totalIncome: number;              // Required
  };
  
  // Expenses - Required
  expenses: {
    advertising?: number;             // Optional
    carAndTruck?: number;             // Optional
    commissions?: number;             // Optional
    contractLabor?: number;           // Optional
    depreciation?: number;            // Optional
    insurance?: number;               // Optional
    interest?: number;                // Optional
    legal?: number;                   // Optional
    office?: number;                  // Optional
    supplies?: number;                // Optional
    travel?: number;                  // Optional
    meals?: number;                   // Optional
    utilities?: number;               // Optional
    totalExpenses: number;            // Required
  };
  
  // Vehicle Information - Conditional
  vehicleInfo?: {
    totalMiles: number;               // Required if claiming vehicle expenses
    businessMiles: number;            // Required if claiming vehicle expenses
    commutingMiles: number;           // Required if claiming vehicle expenses
    otherMiles: number;               // Required if claiming vehicle expenses
  };
}
