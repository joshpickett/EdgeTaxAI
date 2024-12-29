export interface TaxFormData {
  id: string;
  type: TaxFormType;
  year: number;
  status: FormStatus;
  data: Record<string, any>;
  submittedAt?: string;
  lastModified?: string;
}

export interface TaxFormValidation {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationWarning {
  field: string;
  message: string;
  suggestion?: string;
}

export interface TaxFormTemplate {
  id: string;
  type: TaxFormType;
  fields: FormField[];
  validations: FormValidation[];
  calculations: FormCalculation[];
}

export interface FormField {
  id: string;
  name: string;
  type: FieldType;
  required: boolean;
  validation?: string;
  defaultValue?: any;
  dependsOn?: string[];
}

export interface FormValidation {
  field: string;
  type: ValidationType;
  params: Record<string, any>;
  message: string;
}

export interface FormCalculation {
  target: string;
  dependencies: string[];
  formula: string;
}

export enum FieldType {
  TEXT = 'text',
  NUMBER = 'number',
  DATE = 'date',
  BOOLEAN = 'boolean',
  SELECT = 'select',
  MULTI_SELECT = 'multi_select'
}

export enum ValidationType {
  REQUIRED = 'required',
  MIN = 'min',
  MAX = 'max',
  PATTERN = 'pattern',
  CUSTOM = 'custom'
}

export enum TaxFormType {
  FORM_1040 = '1040',
  SCHEDULE_C = 'schedule_c',
  SCHEDULE_SE = 'schedule_se'
}

export enum FormStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress',
  READY = 'ready',
  SUBMITTED = 'submitted',
  ACCEPTED = 'accepted',
  REJECTED = 'rejected'
}
