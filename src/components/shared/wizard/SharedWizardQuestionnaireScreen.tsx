import React, { useState, useEffect } from 'react';
import { COLORS } from '../../../../assets/config/colors';
import { SPACING } from '../../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../../assets/config/typography';
import { QuestionnaireMapper } from '../../../services/QuestionnaireMapper';
import { TAX_QUESTIONS } from '../../../config/questionConfig';

interface SharedWizardQuestionnaireScreenProps {
  onComplete: (answers: Record<string, any>) => void;
  onSaveProgress?: (answers: Record<string, any>) => void;
  initialAnswers?: Record<string, any>;
}

interface Question {
  id: string;
  text: string;
  type: 'boolean' | 'multiselect' | 'text';
  options?: string[];
  conditional?: (answers: Record<string, any>) => boolean;
}

export const SharedWizardQuestionnaireScreen: React.FC<SharedWizardQuestionnaireScreenProps> = ({
  onComplete,
  onSaveProgress,
  initialAnswers = {}
}) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>(initialAnswers);
  const [isProcessing, setIsProcessing] = useState(false);

  const questions = TAX_QUESTIONS;

  useEffect(() => {
    if (onSaveProgress) {
      const saveTimeout = setTimeout(() => {
        onSaveProgress(answers);
      }, 1000);

      return () => clearTimeout(saveTimeout);
    }
  }, [answers]);

  const handleAnswer = (answer: any) => {
    const currentQuestion = questions[currentQuestionIndex];
    setAnswers(prev => ({
      ...prev,
      [currentQuestion.id]: answer
    }));

    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      handleComplete();
    }
  };

  const handleComplete = async () => {
    setIsProcessing(true);
    try {
      const mapper = new QuestionnaireMapper();
      const requiredDocuments = await mapper.getRequiredDocuments(answers);
      onComplete({ answers, requiredDocuments });
    } catch (error) {
      console.error('Error processing questionnaire:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const currentQuestion = questions[currentQuestionIndex];

  // Skip questions that don't meet their conditional
  useEffect(() => {
    if (currentQuestion?.conditional && !currentQuestion.conditional(answers)) {
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(prev => prev + 1);
      } else {
        handleComplete();
      }
    }
  }, [currentQuestionIndex, answers]);

  return (
    <div style={styles.container}>
      <div style={styles.progressBar}>
        <div 
          style={{
            ...styles.progressFill,
            width: `${((currentQuestionIndex + 1) / questions.length) * 100}%`
          }}
        />
      </div>

      <div style={styles.content}>
        <h2 style={styles.questionText}>{currentQuestion.text}</h2>

        <div style={styles.answerSection}>
          {currentQuestion.type === 'boolean' && (
            <div style={styles.booleanButtons}>
              <button
                onClick={() => handleAnswer(true)}
                style={styles.button}
              >
                Yes
              </button>
              <button
                onClick={() => handleAnswer(false)}
                style={styles.button}
              >
                No
              </button>
            </div>
          )}

          {currentQuestion.type === 'multiselect' && (
            <div style={styles.multiselect}>
              {currentQuestion.options?.map(option => (
                <label key={option} style={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    checked={answers[currentQuestion.id]?.includes(option)}
                    onChange={(e) => {
                      const currentAnswers = answers[currentQuestion.id] || [];
                      const newAnswers = e.target.checked
                        ? [...currentAnswers, option]
                        : currentAnswers.filter((a: string) => a !== option);
                      handleAnswer(newAnswers);
                    }}
                  />
                  {option}
                </label>
              ))}
            </div>
          )}
        </div>
      </div>

      {isProcessing && (
        <div style={styles.processingOverlay}>
          Processing your answers...
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: SPACING.xl,
    maxWidth: '800px',
    margin: '0 auto',
    position: 'relative' as const
  },
  progressBar: {
    height: '4px',
    backgroundColor: COLORS.surface,
    borderRadius: '2px',
    marginBottom: SPACING.xl
  },
  progressFill: {
    height: '100%',
    backgroundColor: COLORS.primary,
    borderRadius: '2px',
    transition: 'width 0.3s ease'
  },
  content: {
    textAlign: 'center' as const
  },
  questionText: {
    fontSize: TYPOGRAPHY.fontSize.xl,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    color: COLORS.text.primary,
    marginBottom: SPACING.xl
  },
  answerSection: {
    marginTop: SPACING.xl
  },
  booleanButtons: {
    display: 'flex',
    justifyContent: 'center',
    gap: SPACING.md
  },
  button: {
    backgroundColor: COLORS.primary,
    color: COLORS.background,
    padding: `${SPACING.md}px ${SPACING.xl}px`,
    borderRadius: '4px',
    border: 'none',
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
    '&:hover': {
      backgroundColor: COLORS.secondary
    }
  },
  multiselect: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: SPACING.md,
    alignItems: 'flex-start',
    maxWidth: '300px',
    margin: '0 auto'
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: SPACING.sm,
    fontSize: TYPOGRAPHY.fontSize.md,
    color: COLORS.text.primary,
    cursor: 'pointer'
  },
  processingOverlay: {
    position: 'absolute' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: TYPOGRAPHY.fontSize.lg,
    color: COLORS.text.primary
  }
};
