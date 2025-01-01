import React, { useState, useEffect } from 'react';
import { DocumentManager } from '../DocumentCollection/DocumentManager';
import { QuestionnaireStepper } from './QuestionnaireStepper';
import { RequiredDocumentsList } from './RequiredDocumentsList';
import { useDocumentRequirements } from '../../hooks/useDocumentRequirements';
import { LoadingOverlay } from '../LoadingOverlay';

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
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(false);
  
  const { requiredDocuments, isLoading: isLoadingRequirements } = 
    useDocumentRequirements(userId, taxYear, answers);

  const handleAnswerSubmit = (questionId: string, answer: any) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleStepComplete = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      onComplete();
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
    type: 'boolean',
    conditional: (answers: Record<string, any>) => 
      answers.income_sources?.includes('Self Employment')
  },
  {
    id: 'foreign_income',
    text: 'Did you have any foreign income or accounts?',
    type: 'boolean'
  }
];
