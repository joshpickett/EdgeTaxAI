import React, { useState } from 'react';
import { Question } from './Question';
import { QuestionnaireNavigation } from './QuestionnaireNavigation';
import { QuestionnaireProgress } from './QuestionnaireProgress';
import { QuestionnaireMapper } from '../../services/QuestionnaireMapper';

const questionnaireMapper = new QuestionnaireMapper();

interface QuestionnaireStepperProps {
  questions: Array<{
    id: string;
    text: string;
    type: string;
    options?: string[];
    conditional?: (answers: Record<string, any>) => boolean;
  }>;
  currentStep: number;
  answers: Record<string, any>;
  onAnswerSubmit: (questionId: string, answer: any) => void;
  onSaveProgress?: () => void;
  onStepComplete: (requiredDocuments: DocumentType[]) => void;
}

export const QuestionnaireStepper: React.FC<QuestionnaireStepperProps> = ({
  questions,
  currentStep,
  answers,
  onAnswerSubmit,
  onSaveProgress,
  onStepComplete
}) => {
  const currentQuestion = questions[currentStep];
  const [isSaving, setIsSaving] = useState(false);

  const sections = questions.map((q, index) => ({
    id: q.id,
    title: `Step ${index + 1}`,
    isCompleted: answers[q.id] !== undefined
  }));

  if (!currentQuestion) return null;

  // Skip questions that don't meet their conditional
  if (currentQuestion.conditional && !currentQuestion.conditional(answers)) {
    onStepComplete([]);
    return null;
  }

  const handleAnswerSubmit = (answer: any) => {
    onAnswerSubmit(currentQuestion.id, answer);
    const requiredDocuments = questionnaireMapper.getRequiredDocuments(answers);
    onStepComplete(requiredDocuments);
  };

  return (
    <div className="questionnaire-stepper">
      <QuestionnaireProgress
        currentStep={currentStep}
        totalSteps={questions.length}
        completedSteps={Object.keys(answers)}
        sections={sections}
      />

      <Question
        question={currentQuestion}
        answer={answers[currentQuestion.id]}
        onAnswer={handleAnswerSubmit}
      />

      <QuestionnaireNavigation
        canGoBack={currentStep > 0}
        canGoForward={answers[currentQuestion.id] !== undefined}
        onBack={() => onStepComplete([])}
        onNext={() => {
          const requiredDocuments = questionnaireMapper.getRequiredDocuments(answers);
          onStepComplete(requiredDocuments);
        }}
        onSave={onSaveProgress}
        isLastStep={currentStep === questions.length - 1}
        isSaving={isSaving}
      />
    </div>
  );
};
