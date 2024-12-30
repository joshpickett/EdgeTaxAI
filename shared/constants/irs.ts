export const IRS_CONSTANTS = {
  FORM_TYPES: {
    FORM_1040: '1040',
    FORM_1099_NEC: '1099-NEC',
    FORM_1099_K: '1099-K',
    SCHEDULE_C: 'SCHEDULE-C'
  },

  VALIDATION_CODES: {
    REQUIRED_FIELD: 'REQUIRED',
    INVALID_FORMAT: 'INVALID_FORMAT',
    OUT_OF_RANGE: 'OUT_OF_RANGE',
    DEPENDENCY_ERROR: 'DEPENDENCY_ERROR'
  },

  ERROR_MESSAGES: {
    REQUIRED_FIELD: 'This field is required by the IRS',
    INVALID_FORMAT: 'Invalid format for IRS submission',
    OUT_OF_RANGE: 'Value is outside acceptable range',
    DEPENDENCY_ERROR: 'Related field is required'
  },

  DOCUMENT_REQUIREMENTS: {
    RECEIPTS: {
      type: 'receipt',
      format: ['pdf', 'jpg', 'png'],
      maxSize: 5 * 1024 * 1024 // 5MB
    },
    TAX_FORMS: {
      type: 'tax_form',
      format: ['pdf'],
      maxSize: 10 * 1024 * 1024 // 10MB
    }
  },

  SUBMISSION_STATUSES: {
    PENDING: 'pending',
    ACCEPTED: 'accepted',
    REJECTED: 'rejected',
    ERROR: 'error'
  }
};
