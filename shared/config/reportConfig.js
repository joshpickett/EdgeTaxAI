export const REPORT_TYPES = {
  TAX_SUMMARY: 'tax_summary',
  QUARTERLY: 'quarterly',
  ANNUAL: 'annual',
  CUSTOM: 'custom',
  EXPENSE: 'expense',
  MILEAGE: 'mileage'
};

export const VALIDATION_RULES = {
  date: {
    type: 'date',
    required: true,
    validate: (value) => !isNaN(Date.parse(value))
  },
  userId: {
    type: 'string',
    required: true,
    validate: (value) => typeof value === 'string' && value.length > 0
  },
  quarter: {
    type: 'number',
    required: true,
    validate: (value) => value >= 1 && value <= 4
  },
  year: {
    type: 'number',
    required: true,
    validate: (value) => value >= 2000 && value <= new Date().getFullYear() + 1
  }
};

export const REPORT_CONFIGS = {
  tax_summary: {
    cacheDuration: 3600,
    requiresAuth: true,
    validationRules: {
      startDate: VALIDATION_RULES.date,
      endDate: VALIDATION_RULES.date,
      userId: VALIDATION_RULES.userId
    }
  },
  quarterly: {
    cacheDuration: 7200,
    requiresAuth: true,
    validationRules: {
      quarter: VALIDATION_RULES.quarter,
      year: VALIDATION_RULES.year
    }
  }
};

export const CACHE_KEYS = {
  getReportCacheKey: (type, params) => `report_${type}_${JSON.stringify(params)}`,
};
