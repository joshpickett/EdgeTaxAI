import { DocumentType } from '../types/documents';
import { IRS_CONSTANTS } from '../shared/constants/irs';

interface DocumentRequirement {
  id: string;
  type: DocumentType;
  name: string;
  description: string;
  required: boolean;
  conditions?: string[];
}

export class QuestionnaireMapper {
  private documentRules: Map<string, DocumentRequirement[]>;
  private internationalRules: Map<string, DocumentRequirement[]>;
  private stateSpecificRules: Map<string, DocumentRequirement[]>;

  constructor() {
    this.documentRules = new Map();
    this.internationalRules = new Map();
    this.stateSpecificRules = new Map();
    this.initializeStateRules();
    this.initializeInternationalRules();
    this.initializeBasicRules();
  }

  private initializeBasicRules() {
    // Existing rules remain...
     
    // Add Schedule A (Itemized Deductions)
    this.documentRules.set('itemized_deductions', [
      {
        id: 'schedule_a',
        type: DocumentType.SCHEDULE_A,
        name: 'Schedule A',
        description: 'Itemized Deductions',
        required: true,
        conditions: ['itemized_threshold_met']
      },
      {
        id: 'deduction_receipts',
        type: DocumentType.RECEIPT,
        name: 'Deduction Documentation',
        description: 'Receipts and documentation for itemized deductions',
        required: true,
        conditions: ['itemized_threshold_met']
      }
    ]);

    // Add Schedule B (Interest and Dividends)
    this.documentRules.set('interest_dividends', [
      {
        id: 'schedule_b',
        type: DocumentType.SCHEDULE_B,
        name: 'Schedule B',
        description: 'Interest and Ordinary Dividends',
        required: true,
        conditions: [
          'has_interest_income',
          'has_dividend_income'
        ]
      }
    ]);

    // Add Schedule D (Capital Gains)
    this.documentRules.set('capital_gains', [
      {
        id: 'schedule_d',
        type: DocumentType.SCHEDULE_D,
        name: 'Schedule D',
        description: 'Capital Gains and Losses',
        required: true,
        conditions: ['has_investment_sales']
      }
    ]);

    // Add Form 1040 (Base Tax Return)
    this.documentRules.set('base_tax_return', [
      {
        id: 'form_1040',
        type: DocumentType.FORM_1040,
        name: 'Form 1040',
        description: 'U.S. Individual Income Tax Return',
        required: true,
        conditions: []
      },
      {
        id: 'w2_forms',
        type: DocumentType.W2,
        name: 'Form W-2',
        description: 'Wage and Tax Statement',
        required: true,
        conditions: ['has_employment_income']
      }
    ]);

    // Self-employment rules
    this.documentRules.set('self_employment', [
      {
        id: 'schedule_c',
        type: DocumentType.SCHEDULE_C,
        name: 'Schedule C',
        description: 'Profit or Loss from Business',
        required: true
      },
      {
        id: 'business_expenses',
        type: DocumentType.RECEIPT,
        name: 'Business Expense Receipts',
        description: 'Receipts for business-related expenses',
        required: true
      }
    ]);

    // Gig economy rules
    this.documentRules.set('gig_platforms', [
      {
        id: '1099_k',
        type: DocumentType.FORM_1099K,
        name: 'Form 1099-K',
        description: 'Payment Card and Third Party Network Transactions',
        required: true,
        conditions: ['income_threshold_met']
      },
      {
        id: '1099_nec',
        type: DocumentType.FORM_1099NEC,
        name: 'Form 1099-NEC',
        description: 'Nonemployee Compensation',
        required: true
      }
    ]);

    // Rental income rules
    this.documentRules.set('rental_income', [
      {
        id: 'schedule_e',
        type: DocumentType.SCHEDULE_E,
        name: 'Schedule E',
        description: 'Supplemental Income and Loss',
        required: true
      }
    ]);

    // Add international income rules
    this.documentRules.set('foreign_income', [
      {
        id: 'form_2555',
        type: DocumentType.FORM_2555,
        name: 'Form 2555',
        description: 'Foreign Earned Income Exclusion',
        required: true
      },
      {
        id: 'form_8938',
        type: DocumentType.FORM_8938,
        name: 'Form 8938',
        description: 'Statement of Foreign Financial Assets',
        required: true,
        conditions: ['foreign_assets_threshold_met']
      }
    ]);

    // Add foreign account rules
    this.documentRules.set('foreign_accounts', [
      {
        id: 'fbar',
        type: DocumentType.FBAR,
        name: 'FBAR',
        description: 'Foreign Bank and Financial Accounts Report',
        required: true,
        conditions: ['fbar_threshold_met']
      }
    ]);

    // Add non-cash charitable contributions
    this.documentRules.set('nonCashDonations', [
      {
        id: 'form_8283',
        type: DocumentType.FORM_8283,
        name: 'Form 8283',
        description: 'Noncash Charitable Contributions',
        required: true,
        conditions: ['high_value_donations']
      }
    ]);

    // Add casualty loss documents
    this.documentRules.set('casualty_loss', [
      {
        id: 'form_4684',
        type: DocumentType.FORM_4684,
        name: 'Form 4684',
        description: 'Casualties and Thefts',
        required: true,
        conditions: ['has_casualty_loss']
      },
      {
        id: 'damage_documentation',
        type: DocumentType.RECEIPT,
        name: 'Damage Documentation',
        description: 'Photos, receipts, and appraisals of damaged property',
        required: true,
        conditions: ['has_casualty_loss']
      }
    ]);

    // Add energy credits
    this.documentRules.set('energy_improvements', [
      {
        id: 'form_5695',
        type: DocumentType.FORM_5695,
        name: 'Form 5695',
        description: 'Residential Energy Credits',
        required: true,
        conditions: ['has_energy_improvements']
      },
      {
        id: 'energy_receipts',
        type: DocumentType.RECEIPT,
        name: 'Energy Improvement Receipts',
        description: 'Receipts for energy-efficient home improvements',
        required: true,
        conditions: ['has_energy_improvements']
      }
    ]);

    // Add education credits
    this.documentRules.set('education_expenses', [
      {
        id: 'form_1098t',
        type: DocumentType.FORM_1098T,
        name: 'Form 1098-T',
        description: 'Tuition Statement',
        required: true,
        conditions: ['has_education_expenses']
      },
      {
        id: 'form_8863',
        type: DocumentType.FORM_8863,
        name: 'Form 8863',
        description: 'Education Credits (American Opportunity and Lifetime Learning Credits)',
        required: true,
        conditions: ['has_education_expenses']
      },
      {
        id: 'education_receipts',
        type: DocumentType.RECEIPT,
        name: 'Education Expense Receipts',
        description: 'Receipts for qualified education expenses',
        required: true,
        conditions: ['has_education_expenses']
      }
    ]);

    // Add child care expenses
    this.documentRules.set('childCareExpenses', [
      {
        id: 'form_2441',
        type: DocumentType.FORM_2441,
        name: 'Form 2441',
        description: 'Child and Dependent Care Expenses',
        required: true,
        conditions: ['has_child_care']
      },
      {
        id: 'care_provider_documentation',
        type: DocumentType.RECEIPT,
        name: 'Care Provider Documentation',
        description: 'Receipts and documentation from care providers',
        required: true,
        conditions: ['has_child_care']
      }
    ]);

    // Add early withdrawal penalties
    this.documentRules.set('early_withdrawal', [
      {
        id: 'form_5329',
        type: DocumentType.FORM_5329,
        name: 'Form 5329',
        description: 'Additional Taxes on Qualified Plans',
        required: true,
        conditions: ['has_early_withdrawal']
      },
      {
        id: 'distribution_statements',
        type: DocumentType.STATEMENT,
        name: 'Distribution Statements',
        description: 'Statements showing early withdrawals',
        required: true,
        conditions: ['has_early_withdrawal']
      }
    ]);

    // Add Form 8606 (Nondeductible IRAs)
    this.documentRules.set('ira_contributions', [
      {
        id: 'form_8606',
        type: DocumentType.FORM_8606,
        name: 'Form 8606',
        description: 'Nondeductible IRAs',
        required: true,
        conditions: ['has_nondeductible_ira']
      },
      {
        id: 'ira_statements',
        type: DocumentType.STATEMENT,
        name: 'IRA Contribution Statements',
        description: 'Statements showing IRA contributions',
        required: true,
        conditions: ['has_nondeductible_ira']
      }
    ]);

    // Add foreign gifts
    this.documentRules.set('foreign_gifts', [
      {
        id: 'form_3520',
        type: DocumentType.FORM_3520,
        name: 'Form 3520',
        description: 'Foreign Gifts and Trusts',
        required: true,
        conditions: ['has_foreign_gifts']
      },
      {
        id: 'gift_documentation',
        type: DocumentType.DOCUMENTATION,
        name: 'Foreign Gift Documentation',
        description: 'Documentation of foreign gifts received',
        required: true,
        conditions: ['has_foreign_gifts']
      }
    ]);

    // Add vehicle depreciation
    this.documentRules.set('vehicleForBusiness', [
      {
        id: 'form_4562',
        type: DocumentType.FORM_4562,
        name: 'Form 4562',
        description: 'Depreciation and Amortization',
        required: true,
        conditions: ['has_depreciable_assets']
      },
      {
        id: 'asset_records',
        type: DocumentType.RECEIPT,
        name: 'Asset Purchase Records',
        description: 'Records of depreciable asset purchases',
        required: true,
        conditions: ['has_depreciable_assets']
      }
    ]);

    // Add Schedule F (Farm Income)
    this.documentRules.set('farm_income', [
      {
        id: 'schedule_f',
        type: DocumentType.SCHEDULE_F,
        name: 'Schedule F',
        description: 'Profit or Loss From Farming',
        required: true,
        conditions: ['has_farm_income']
      },
      {
        id: 'farm_expenses',
        type: DocumentType.RECEIPT,
        name: 'Farm Expense Receipts',
        description: 'Receipts for farm-related expenses',
        required: true,
        conditions: ['has_farm_expenses']
      }
    ]);
  }

  private initializeInternationalRules() {
    this.internationalRules.set('foreign_tax_credit', [
      {
        id: 'form_1116',
        type: DocumentType.FORM_1116,
        name: 'Form 1116',
        description: 'Foreign Tax Credit',
        required: true,
        conditions: ['foreign_tax_paid']
      }
    ]);

    this.internationalRules.set('foreign_business', [
      {
        id: 'form_8829',
        type: DocumentType.FORM_8829,
        name: 'Form 8829',
        description: 'Expenses for Business Use of Your Home',
        required: true,
        conditions: ['foreign_home_office']
      }
    ]);
  }

  private initializeStateRules() {
    // Add state-specific rules
    this.stateSpecificRules.set('CA', [
      {
        id: 'ca_solar_credit',
        type: DocumentType.STATE_CREDIT,
        name: 'California Solar Credit',
        description: 'Documentation for CA solar installations',
        required: true,
        conditions: ['has_solar_installation']
      },
      {
        id: 'ca_solar_receipts',
        type: DocumentType.RECEIPT,
        name: 'Solar Installation Receipts',
        description: 'Receipts and contracts for solar installation',
        required: true,
        conditions: ['has_solar_installation']
      }
    ]);

    // Add more state-specific rules as needed
    this.stateSpecificRules.set('NY', [
      // New York specific rules
    ]);
  }

  async getRequiredDocuments(answers: Record<string, any>): Promise<DocumentRequirement[]> {
    const requiredDocs = new Set<DocumentRequirement>();

    // Process each answer and add corresponding required documents
    for (const [question, answer] of Object.entries(answers)) {
      if (answer && this.documentRules.has(question)) {
        const docs = this.documentRules.get(question)!;
        docs.forEach(doc => {
          // Check conditions if they exist
          if (!doc.conditions || this.evaluateConditions(doc.conditions, answers)) {
            requiredDocs.add(doc);
          }
        });
      }
    }

    return Array.from(requiredDocs);
  }

  private evaluateConditions(conditions: string[], answers: Record<string, any>): boolean {
    return conditions.every(condition => {
      switch (condition) {
        case 'foreign_assets_threshold_met':
          return (answers.foreign_assets_value || 0) >= 50000;
        case 'fbar_threshold_met':
          return (answers.foreign_accounts_value || 0) >= 10000;
        case 'high_value_donations':
          return (answers.noncash_donations_value || 0) >= 500;
        case 'has_rental_income':
          return answers.rental_income === true;
        case 'has_education_expenses':
          return answers.education_expenses === true;
        case 'income_threshold_met':
          return (answers.estimated_income || 0) >= 20000;
        case 'has_foreign_gifts':
          return (answers.foreign_gifts_value || 0) >= 100000;
        case 'has_early_withdrawal':
          return answers.early_withdrawal === true;
        case 'has_inheritance':
          return answers.inheritance === true;
        case 'has_child_care':
          return answers.child_care_expenses === true;
        case 'has_ira_contributions':
          return answers.ira_contributions === true;
        case 'has_business_vehicle':
          return answers.business_vehicle === true;
        case 'has_farm_income':
          return answers.farm_income === true;
        case 'has_farm_expenses':
          return answers.farm_expenses === true;
        case 'has_investment_sales':
          return answers.investment_sales === true;
        case 'has_interest_income':
          return (answers.interest_income || 0) > 1500;
        case 'has_dividend_income':
          return (answers.dividend_income || 0) > 1500;
        case 'has_employment_income':
          return answers.employment_income === true;
        case 'has_casualty_loss':
          return answers.casualty_loss === true;
        case 'has_energy_improvements':
          return answers.energy_improvements === true;
        case 'itemized_threshold_met':
          return (answers.total_deductions || 0) > IRS_CONSTANTS.STANDARD_DEDUCTION;
        case 'has_nondeductible_ira':
          return answers.nondeductible_ira === true;
        case 'has_depreciable_assets':
          return answers.depreciable_assets === true;
        case 'has_solar_installation':
          return answers.solar_installation === true;
        default:
          return true;
      }
    });
  }
}
