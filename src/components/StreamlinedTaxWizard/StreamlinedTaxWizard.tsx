import React, { useState, useEffect } from 'react';
import { DocumentManager } from '../DocumentCollection/DocumentManager';
import { QuestionnaireStepper } from './QuestionnaireStepper';
import { RequiredDocumentsList } from './RequiredDocumentsList';
import { useDocumentRequirements } from '../../hooks/useDocumentRequirements';
import { LoadingOverlay } from '../LoadingOverlay';
import { FormProgressService } from '../../services/form/form_progress_service';
import { FormValidationService } from '../../services/form/form_validation_service';
import { QuestionnaireMapper } from '../../services/QuestionnaireMapper';
import { SharedWizardLandingScreen } from './SharedWizardLandingScreen';
import { SharedWizardQuestionnaireScreen } from './SharedWizardQuestionnaireScreen';
import { SharedWizardDocumentRequirementsScreen } from './SharedWizardDocumentRequirementsScreen';
import { SharedWizardDocumentUploadScreen } from './SharedWizardDocumentUploadScreen';
import { SharedWizardReviewScreen } from './SharedWizardReviewScreen';
import { SharedWizardCompletionScreen } from './SharedWizardCompletionScreen';

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
  const [currentScreen, setCurrentScreen] = useState<'landing' | 'questionnaire' | 'requirements' | 'upload' | 'review' | 'complete'>('landing');
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [requiredDocuments, setRequiredDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [uploadedDocuments, setUploadedDocuments] = useState([]);

  useEffect(() => {
    // Load saved progress on mount
    const loadSavedProgress = async () => {
      const savedProgress = await formProgressService.get_progress(userId);
      if (savedProgress) {
        setAnswers(savedProgress.answers);
        setCurrentScreen(savedProgress.currentStep);
      }
    };
    loadSavedProgress();
  }, [userId]);

  const handleStartWizard = () => {
    setCurrentScreen('questionnaire');
  };

  const handleQuestionnaireComplete = (questionnaireAnswers: Record<string, any>) => {
    setAnswers(questionnaireAnswers);
    setCurrentScreen('requirements'); 
  };

  const handleDocumentUpload = async (file: File, documentId: string) => {
    // Upload logic
    setUploadedDocuments(prev => [...prev, { id: documentId, file }]);
  };

  const handleReviewComplete = () => {
    setCurrentScreen('complete');
    onComplete();
  };

  useEffect(() => {
    const updateRequiredDocuments = async () => {
      const docs = await questionnaireMapper.getRequiredDocuments(answers);
      setRequiredDocuments(docs);
    };
    updateRequiredDocuments();
  }, [answers]);

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

  if (isLoading) {
    return <LoadingOverlay />;
  }

  const additionalQuestions = [
    {
      id: 'itemized_deductions',
      text: 'Do you want to itemize your deductions?',
      type: 'boolean'
    },
    {
      id: 'foreign_tax_credit',
      text: 'Did you pay taxes to a foreign government?',
      type: 'boolean',
      conditional: (answers) => answers.foreign_income === true
    },
    {
      id: 'home_office',
      text: 'Do you use part of your home for business?',
      type: 'boolean',
      conditional: (answers) => answers.self_employment === true
    }
  ];

  return (
    <div className="streamlined-tax-wizard"> 
      {currentScreen === 'landing' && (
        <SharedWizardLandingScreen
          onStart={handleStartWizard}
          documents={requiredDocuments}
          documentCount={requiredDocuments.length}
          completedDocuments={uploadedDocuments.length}
        />
      )}

      {currentScreen === 'questionnaire' && (
        <SharedWizardQuestionnaireScreen
          onComplete={handleQuestionnaireComplete}
          initialAnswers={answers}
        />
      )}

      {currentScreen === 'requirements' && (
        <SharedWizardDocumentRequirementsScreen
          requiredDocuments={requiredDocuments}
          onContinue={() => setCurrentScreen('upload')}
          onBack={() => setCurrentScreen('questionnaire')}
        />
      )}

      {currentScreen === 'upload' && (
        <SharedWizardDocumentUploadScreen
          requiredDocuments={requiredDocuments}
          onUpload={handleDocumentUpload}
          onComplete={() => setCurrentScreen('review')}
          onBack={() => setCurrentScreen('requirements')}
        />
      )}

      {currentScreen === 'review' && (
        <SharedWizardReviewScreen
          documents={uploadedDocuments}
          onSubmit={handleReviewComplete}
          onBack={() => setCurrentScreen('upload')}
          onReupload={handleDocumentUpload}
        />
      )}

      {currentScreen === 'complete' && (
        <SharedWizardCompletionScreen
          documentCount={requiredDocuments.length}
          completedDocuments={uploadedDocuments.length}
          onDashboardRedirect={() => {/* Navigate to dashboard */}}
        />
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
