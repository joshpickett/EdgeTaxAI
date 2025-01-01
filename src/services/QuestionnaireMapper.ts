import { DocumentType } from '../types/documents';

interface QuestionnaireMapping {
  questionId: string;
  answers: any[];
  requiredDocuments: DocumentType[];
}

export class QuestionnaireMapper {
  private mappings: QuestionnaireMapping[] = [
    {
      questionId: 'income_sources',
      answers: ['W2 Employment'],
      requiredDocuments: [DocumentType.W2, DocumentType.PAY_STUBS]
    },
    {
      questionId: 'income_sources',
      answers: ['Self Employment'],
      requiredDocuments: [DocumentType.FORM_1099, DocumentType.EXPENSE_RECEIPTS]
    },
    {
      questionId: 'foreign_income',
      answers: [true],
      requiredDocuments: [DocumentType.FOREIGN_BANK_STATEMENTS, DocumentType.FOREIGN_TAX_RETURNS]
    }
  ];

  public getRequiredDocuments(answers: Record<string, any>): DocumentType[] {
    const requiredDocs = new Set<DocumentType>();

    this.mappings.forEach(mapping => {
      if (this.doesAnswerMatch(answers[mapping.questionId], mapping.answers)) {
        mapping.requiredDocuments.forEach(doc => requiredDocs.add(doc));
      }
    });

    return Array.from(requiredDocs);
  }

  private doesAnswerMatch(userAnswer: any, mappingAnswers: any[]): boolean {
    if (Array.isArray(userAnswer)) {
      return userAnswer.some(answer => mappingAnswers.includes(answer));
    }
    return mappingAnswers.includes(userAnswer);
  }
}
