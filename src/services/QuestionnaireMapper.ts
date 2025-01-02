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

  constructor() {
    this.documentRules = new Map();
    this.initializeRules();
  }

  private initializeRules() {
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
        case 'income_threshold_met':
          return (answers.estimated_income || 0) >= 20000;
        default:
          return true;
      }
    });
  }
}
