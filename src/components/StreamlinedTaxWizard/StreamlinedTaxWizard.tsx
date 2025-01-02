import React, { useState, useEffect } from 'react';
import { DocumentManager } from '../DocumentCollection/DocumentManager';
import { QuestionnaireStepper } from './QuestionnaireStepper';
import { RequiredDocumentsList } from './RequiredDocumentsList';
import { useDocumentRequirements } from '../../hooks/useDocumentRequirements';
import { LoadingOverlay } from '../LoadingOverlay';
import { FormProgressService } from '../../services/form/form_progress_service';
import { FormValidationService } from '../../services/form/form_validation_service';
import { QuestionnaireMapper } from '../../services/QuestionnaireMapper';

const formProgressService = new FormProgressService();
const formValidationService = new FormValidationService();

interface StreamlinedTaxWizardProps {
  userId: string;
  taxYear: number;
  onComplete: () => void;
}

export const StreamlinedTaxWizard: React.FC<StreamlinedTaxWizardProps> = ({
  userId,
  taxYear,
  onComplete
}) => {
  const questionnaireMapper = new QuestionnaireMapper();
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [requiredDocuments, setRequiredDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    // Load saved progress on mount
    const loadSavedProgress = async () => {
      const savedProgress = await formProgressService.get_progress(userId);
      if (savedProgress) {
        setAnswers(savedProgress.answers);
        setCurrentStep(savedProgress.currentStep);
      }
    };
    loadSavedProgress();
  }, [userId]);

  const handleAnswerSubmit = (questionId: string, answer: any) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  useEffect(() => {
    const updateRequiredDocuments = async () => {
      const docs = await questionnaireMapper.getRequiredDocuments(answers);
      setRequiredDocuments(docs);
    };
    updateRequiredDocuments();
  }, [answers]);

  const handleStepComplete = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      onComplete();
    }
  };

  const handleSaveProgress = async () => {
    try {
      await formProgressService.save_progress(userId, {
        answers,
        currentStep,
        lastUpdated: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error saving progress:', error);
    }
  };

  if (isLoading || isLoadingRequirements) {
    return <LoadingOverlay />;
  }

  return (
    <div className="streamlined-tax-wizard">
      {currentStep < questions.length ? (
        <QuestionnaireStepper
          questions={questions}
          currentStep={currentStep}
          answers={answers}
          onAnswerSubmit={handleAnswerSubmit}
          onStepComplete={handleStepComplete}
        />
      ) : (
        <div className="document-requirements">
          <RequiredDocumentsList documents={requiredDocuments} />
          <DocumentManager
            userId={userId}
            requiredDocuments={requiredDocuments}
            onComplete={onComplete}
          />
        </div>
      )}
    </div>
  );
};

const questions = [
  {
    id: 'income_sources',
    text: 'What types of income did you receive this year?',
    helpText: 'Please select all that apply.',
    type: 'multiselect',
    options: [
      'W2 Employment',
      'Self Employment',
      'Rental Income',
      'Investment Income'
    ]
  },
  {
    id: 'self_employment',
    text: 'Did you have any business expenses?',
    helpText: 'Only answer if you selected Self Employment.',
    type: 'boolean',
    conditional: (answers: Record<string, any>) => 
      answers.income_sources?.includes('Self Employment')
  },
  {
    id: 'foreign_income',
    text: 'Did you have any foreign income or accounts?',
    helpText: 'This includes any income from outside your country.',
    type: 'boolean'
  }
];
