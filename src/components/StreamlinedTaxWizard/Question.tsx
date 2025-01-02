import React, { useState } from 'react';
import { COLORS } from '../../../assets/config/colors';
import { SPACING } from '../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../assets/config/typography';

interface QuestionProps {
  question: {
    id: string;
    text: string;
    helpText?: string;
    type: string;
    options?: string[];
  };
  answer: any;
  onAnswer: (answer: any) => void;
}

export const Question: React.FC<QuestionProps> = ({
  question,
  answer,
  onAnswer,
  validation
}) => {
  const [touched, setTouched] = useState(false);
  
  const handleChange = (value: any) => {
    setTouched(true);
    onAnswer(value);
  };

  const renderInput = () => {
    switch (question.type) {
      case 'state':
        return (
          <select value={answer || ''} onChange={(e) => handleChange(e.target.value)}>
            <option value="">Select State</option>
            {US_STATES.map(state => (
              <option key={state.code} value={state.code}>
                {state.name}
              </option>
            ))}
          </select>
        );

      case 'dropdown':
        return (
          <select value={answer || ''} onChange={(e) => handleChange(e.target.value)}>
            {question.options?.map(option => <option key={option} value={option}>{option}</option>)}
          </select>
        );

      case 'boolean':
        return (
          <div className="boolean-input" style={styles.booleanContainer}>
            <button
              style={{
                ...styles.booleanButton,
                ...(answer === true ? styles.selectedButton : {})
              }}
              onClick={() => handleChange(true)}
            >
              Yes
            </button>
            <button
              style={{
                ...styles.booleanButton,
                ...(answer === false ? styles.selectedButton : {})
              }}
              onClick={() => handleChange(false)}
            >
              No
            </button>
          </div>
        );

      case 'multiselect':
        return (
          <div className="multiselect-input" style={styles.multiselectContainer}>
            {question.options?.map(option => (
              <label key={option} style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={Array.isArray(answer) && answer.includes(option)}
                  onChange={(e) => {
                    const newAnswer = Array.isArray(answer) ? [...answer] : [];
                    if (e.target.checked) {
                      newAnswer.push(option);
                    } else {
                      const index = newAnswer.indexOf(option);
                      if (index > -1) {
                        newAnswer.splice(index, 1);
                      }
                    }
                    handleChange(newAnswer);
                  }}
                  style={styles.checkbox}
                />
                {option}
              </label>
            ))}
          </div>
        );

      default:
        return (
          <input
            type="text"
            value={answer || ''}
            onChange={(e) => handleChange(e.target.value)}
            style={styles.textInput}
          />
        );
    }
  };

  return (
    <div className="question" style={styles.container}>
      <h3 style={styles.questionText}>
        {question.text}
      </h3>

      {question.helpText && (
        <p className="help-text">
          {question.helpText}
        </p>
      )}
      {renderInput()}
    </div>
  );
};

const US_STATES = [
  { code: 'CA', name: 'California' },
  { code: 'NY', name: 'New York' },
  // Add all other states...
  { code: 'WY', name: 'Wyoming' }
].sort((a, b) => a.name.localeCompare(b.name));

const styles = {
  container: {
    padding: SPACING.lg,
    backgroundColor: COLORS.background,
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    marginBottom: SPACING.md
  },
  questionText: {
    fontSize: TYPOGRAPHY.fontSize.lg,
    fontFamily: TYPOGRAPHY.fontFamily.medium,
    color: COLORS.text.primary,
    marginBottom: SPACING.md
  },
  helpText: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.text.secondary,
    marginBottom: SPACING.md
  },
  booleanContainer: {
    display: 'flex',
    gap: SPACING.md
  },
  booleanButton: {
    padding: `${SPACING.sm}px ${SPACING.md}px`,
    border: `1px solid ${COLORS.border}`,
    borderRadius: '4px',
    backgroundColor: COLORS.background,
    cursor: 'pointer',
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.regular
  },
  selectedButton: {
    backgroundColor: COLORS.primary,
    color: COLORS.background,
    borderColor: COLORS.primary
  },
  multiselectContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: SPACING.sm
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: SPACING.sm,
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.regular,
    color: COLORS.text.primary
  },
  checkbox: {
    width: '20px',
    height: '20px'
  },
  textInput: {
    width: '100%',
    padding: SPACING.sm,
    border: `1px solid ${COLORS.border}`,
    borderRadius: '4px',
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.regular
  }
};
