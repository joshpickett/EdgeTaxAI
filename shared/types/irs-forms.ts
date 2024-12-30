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
