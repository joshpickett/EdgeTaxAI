class QuestionnaireMapper {
  private documentRequirements: Map<string, Array<{ type: DocumentType; required: boolean; description: string; priority: string }>>;

  constructor() {
    this.documentRequirements = new Map();
    this.initializeRequirements();
  }

  private initializeRequirements() {
    // W2 Employment
    this.documentRequirements.set('income_sources_w2', [
      {
        type: DocumentType.W2,
        required: true,
        description: 'Form W-2 from each employer',
        priority: 'high'
      },
      {
        type: DocumentType.PAY_STUBS,
        required: false,
        description: 'Recent pay stubs',
        priority: 'medium'
      }
    ]);

    // Self Employment
    this.documentRequirements.set('income_sources_self_employed', [
      {
        type: DocumentType.FORM_1099_NEC,
        required: true,
        description: 'Form 1099-NEC for contractor income',
        priority: 'high'
      }
    ]);

    // ...rest of the code...
  }

  public async getRequiredDocuments(answers: QuestionnaireResponse): Promise<DocumentType[]> {
    const requiredDocs = new Set<DocumentType>();
    const processedAnswers = new Set<string>();

    // Process income sources
    if (answers.income_sources) {
      for (const source of answers.income_sources) {
        if (processedAnswers.has(source)) continue;
        const docs = this.documentRequirements.get(`income_sources_${source.toLowerCase()}`);
        if (docs) {
          docs.forEach(doc => requiredDocs.add(doc));
        }
        processedAnswers.add(source);
      }
    }

    // ...rest of the code...
  }
}
