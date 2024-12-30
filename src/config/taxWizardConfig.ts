export const TAX_WIZARD_CONFIG = {
  steps: {
    initialScreening: {
      title: 'Initial Screening',
      required: true,
      validation: ['filingStatus', 'incomeSources']
    },
    personalInfo: {
      title: 'Personal Information',
      required: true,
      validation: ['taxpayerInfo', 'address']
    },
    income: {
      title: 'Income',
      required: true,
      validation: ['income', 'w2Forms', 'form1099s']
    },
    adjustments: {
      title: 'Adjustments',
      required: false,
      validation: ['adjustments']
    },
    credits: {
      title: 'Credits',
      required: false,
      validation: ['credits']
    },
    review: {
      title: 'Review & Submit',
      required: true,
      validation: ['completeness']
    }
  },
  validation: {
    requiredFields: {
      taxpayerInfo: ['firstName', 'lastName', 'socialSecurityNumber', 'filingStatus'],
      address: ['street', 'city', 'state', 'zipCode'],
      income: ['totalIncome']
    },
    patterns: {
      socialSecurityNumber: /^\d{3}-?\d{2}-?\d{4}$/,
      zipCode: /^\d{5}(-\d{4})?$/,
      employerIdentificationNumber: /^\d{2}-\d{7}$/
    }
  },
  autoSave: {
    interval: 60000, // 1 minute
    enabled: true
  }
};
