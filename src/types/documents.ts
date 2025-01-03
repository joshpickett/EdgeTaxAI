export enum DocumentType {
  W2 = 'W2',
  FORM_1099_NEC = 'FORM_1099_NEC',
  FORM_1099_K = 'FORM_1099_K',
  FORM_1099_DIV = 'FORM_1099_DIV',
  FORM_1099_INT = 'FORM_1099_INT',
  SCHEDULE_C = 'SCHEDULE_C',
  SCHEDULE_E = 'SCHEDULE_E',
  BUSINESS_EXPENSES = 'BUSINESS_EXPENSES',
  HOME_OFFICE_EXPENSES = 'HOME_OFFICE_EXPENSES',
  BANK_STATEMENTS = 'BANK_STATEMENTS',
  PAY_STUBS = 'PAY_STUBS',
  RENTAL_INCOME_DOCS = 'RENTAL_INCOME_DOCS',
  PROPERTY_TAX = 'PROPERTY_TAX',
  INVESTMENT_STATEMENTS = 'INVESTMENT_STATEMENTS',
  FOREIGN_INCOME_STATEMENT = 'FOREIGN_INCOME_STATEMENT',
  FBAR = 'FBAR',
  OTHER = 'OTHER'
}

export enum DocumentStatus {
  PENDING = 'PENDING',
  UPLOADED = 'UPLOADED',
  PROCESSING = 'PROCESSING',
  PROCESSED = 'PROCESSED',
  VERIFIED = 'VERIFIED',
  REJECTED = 'REJECTED',
  ERROR = 'ERROR'
}

export interface DocumentMetadata {
  extractedData?: Record<string, any>;
  confidence?: number;
  processingTime?: number;
  version?: number;
  lastModified?: string;
  status?: DocumentStatus;
  rejectionReason?: string;
}

export interface DocumentRequirement {
  type: DocumentType;
  required: boolean;
  description: string;
  instructions?: string;
  deadline?: string;
  alternatives?: DocumentType[];
}
