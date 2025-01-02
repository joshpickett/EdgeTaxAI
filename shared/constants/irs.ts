export const IRS_CONSTANTS = {
  FORM_TYPES: {
    FORM_1040: '1040',
    FORM_1099_NEC: '1099-NEC',
    FORM_1099_K: '1099-K',
    SCHEDULE_C: 'SCHEDULE-C',
    W2: {
      name: 'Form W-2',
      description: 'Wage and Tax Statement',
      required: true
    },
    FORM_1099_NEC: {
      name: 'Form 1099-NEC',
      description: 'Nonemployee Compensation',
      required: true
    },
    FORM_1099_K: {
      name: 'Form 1099-K',
      description: 'Payment Card and Third Party Network Transactions',
      required: true
    },
    SCHEDULE_C: {
      name: 'Schedule C',
      description: 'Profit or Loss from Business',
      required: true
    }
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
