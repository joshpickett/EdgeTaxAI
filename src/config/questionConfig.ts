import { DocumentType } from '../types/documents';

export interface QuestionConfig {
  id: string;
  text: string;
  helpText?: string;
  type: 'boolean' | 'state' | 'currency' | 'number' | 'multiselect' | 'date';
  required?: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
  options?: string[];
  documentTriggers?: DocumentType[];
  conditions?: {
    field: string;
    operator: 'equals' | 'greaterThan' | 'lessThan';
    value: any;
  }[];
}

export const TAX_QUESTIONS: QuestionConfig[] = [
  {
    id: 'foreignIncome',
    text: 'Did you earn income from outside the U.S.?',
    type: 'boolean',
    required: true,
    helpText: 'Include income from foreign employers, investments, or business activities',
    documentTriggers: [DocumentType.FORM_2555, DocumentType.FORM_8938]
  },
  {
    id: 'selfEmployed',
    text: 'Are you self-employed or own a small business?',
    type: 'boolean',
    required: true,
    documentTriggers: [DocumentType.FORM_1099_NEC, DocumentType.SCHEDULE_C]
  },
  {
    id: 'state',
    text: 'What is your state of residence?',
    type: 'state',
    required: true
  },
  {
    id: 'nonCashDonations',
    text: 'Did you donate items (non-cash) exceeding $500?',
    type: 'boolean',
    required: true,
    documentTriggers: [DocumentType.FORM_8283]
  },
  {
    id: 'casualtyLoss',
    text: 'Did you experience property damage due to a disaster?',
    type: 'boolean',
    required: true,
    documentTriggers: [DocumentType.FORM_4684]
  },
  {
    id: 'rentalIncome',
    text: 'Did you earn income from rental properties?',
    type: 'boolean',
    required: true,
    documentTriggers: [DocumentType.SCHEDULE_E]
  },
  {
    id: 'capitalGains',
    text: 'Did you sell stocks, bonds, or other investments?',
    type: 'boolean',
    required: true,
    documentTriggers: [DocumentType.SCHEDULE_D, DocumentType.FORM_8949]
  },
  {
    id: 'energyImprovements',
    text: 'Did you make energy-efficient improvements to your home?',
    type: 'boolean',
    required: true,
    documentTriggers: [DocumentType.FORM_5695]
  },
  {
    id: 'childCareExpenses',
    text: 'Did you pay for childcare services?',
    type: 'boolean',
    required: true,
    documentTriggers: [DocumentType.FORM_2441]
  },
  {
    id: 'educationExpenses',
    text: 'Did you or a dependent pay for tuition?',
    type: 'boolean',
    required: true,
    documentTriggers: [DocumentType.FORM_1098T, DocumentType.FORM_8863]
  },
  {
    id: 'foreignAccounts',
    text: 'Do you own foreign financial accounts over $10,000?',
    type: 'boolean',
    required: true,
    documentTriggers: [DocumentType.FBAR, DocumentType.FORM_8938]
  },
  {
    id: 'earlyRetirement',
    text: 'Did you withdraw from retirement accounts early?',
    type: 'boolean',
    required: true,
    documentTriggers: [DocumentType.FORM_5329, DocumentType.FORM_8606]
  },
  {
    id: 'inheritance',
    text: 'Did you inherit significant assets?',
    type: 'boolean',
    required: true
  },
  {
    id: 'foreignGifts',
    text: 'Did you receive foreign gifts over $100,000?',
    type: 'boolean',
    required: true,
    documentTriggers: [DocumentType.FORM_3520]
  },
  {
    id: 'vehicleForBusiness',
    text: 'Did you use a personal vehicle for business?',
    type: 'boolean',
    required: true,
    documentTriggers: [DocumentType.FORM_4562]
  }
];
