export interface IRSField {
  id: string;
  name: string;
  type: 'string' | 'number' | 'date' | 'boolean';
  required: boolean;
  validation?: {
    pattern?: string;
    min?: number;
    max?: number;
    message?: string;
  };
}

export interface IRSFormMetadata {
  formType: string;
  version: string;
  year: number;
  fields: IRSField[];
}

export interface IRSValidationResult {
  isValid: boolean;
  errors: Array<{
    field: string;
    message: string;
    code: string;
  }>;
  warnings?: Array<{
    field: string;
    message: string;
    code: string;
  }>;
}

export interface IRSSubmissionStatus {
  id: string;
  status: 'pending' | 'accepted' | 'rejected' | 'error';
  timestamp: string;
  errors?: Array<{
    code: string;
    message: string;
  }>;
}

export interface IRSDocumentRequirement {
  type: string;
  required: boolean;
  format: string[];
  maxSize: number;
}

export interface IRSComplianceRule {
  field: string;
  rule: 'required' | 'pattern' | 'range' | 'dependency';
  value?: any;
  message: string;
  severity: 'error' | 'warning';
}
