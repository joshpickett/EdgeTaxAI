import { useState, useEffect } from 'react';
import { DocumentChecklistService } from '../services/document_checklist_service';

export const useDocumentRequirements = (
  userId: string,
  taxYear: number,
  answers: Record<string, any>
) => {
  const [requiredDocuments, setRequiredDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const loadRequirements = async () => {
      try {
        setIsLoading(true);
        const checklistService = new DocumentChecklistService();
        const requirements = await checklistService.generateChecklist(
          userId,
          taxYear,
          answers
        );
        setRequiredDocuments(requirements);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    };

    loadRequirements();
  }, [userId, taxYear, JSON.stringify(answers)]);

  return { requiredDocuments, isLoading, error };
};
