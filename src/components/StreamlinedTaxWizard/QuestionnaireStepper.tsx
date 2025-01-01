import React from 'react';
import { Question } from './Question';

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
  onStepComplete: () => void;
}

export const QuestionnaireStepper: React.FC<QuestionnaireStepperProps> = ({
  questions,
  currentStep,
  answers,
  onAnswerSubmit,
  onStepComplete
}) => {
  const currentQuestion = questions[currentStep];
  
  if (!currentQuestion) return null;
  
  // Skip questions that don't meet their conditional
  if (currentQuestion.conditional && !currentQuestion.conditional(answers)) {
    onStepComplete();
    return null;
  }

  return (
    <div className="questionnaire-stepper">
      <div className="progress-indicator">
        Step {currentStep + 1} of {questions.length}
      </div>
      
      <Question
        question={currentQuestion}
        answer={answers[currentQuestion.id]}
        onAnswer={(answer) => {
          onAnswerSubmit(currentQuestion.id, answer);
          onStepComplete();
        }}
      />
    </div>
  );
};
