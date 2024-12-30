export const TAX_WIZARD_CONFIG = {
  steps: {
    initialScreening: {
      order: 1,
      title: 'Basic Information',
      required: true,
      validation: ['filingStatus', 'taxYear']
    },
    personalInfo: {
      order: 2,
      title: 'Personal Information',
      required: true,
      validation: ['firstName', 'lastName', 'ssn']
    },
    income: {
      order: 3,
      title: 'Income Sources',
      required: true,
      validation: ['totalIncome']
    },
    adjustments: {
      order: 4,
      title: 'Adjustments',
      required: false
    },
    credits: {
      order: 5,
      title: 'Credits & Deductions',
      required: false
    },
    review: {
      order: 6,
      title: 'Review & Submit',
      required: true
    }
  },
  
  validation: {
    ssn: {
      pattern: /^\d{3}-?\d{2}-?\d{4}$/,
      message: 'Please enter a valid SSN'
    },
    ein: {
      pattern: /^\d{2}-?\d{7}$/,
      message: 'Please enter a valid EIN'
    }
  },

  thresholds: {
    selfEmploymentIncome: 400, // Minimum self-employment income requiring filing
    dependentIncome: 12550, // Standard deduction 2023
    itemizedDeductions: 12950 // Threshold for itemizing
  },

  platformIntegration: {
    supportedPlatforms: [
      'uber',
      'lyft',
      'doordash',
      'instacart',
      'grubhub'
    ],
    requiredFields: {
      income: ['grossEarnings', 'expenses', 'miles'],
      documents: ['1099K', '1099NEC']
    }
  }
};
