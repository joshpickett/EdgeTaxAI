import React, { useState } from 'react';
import { QuestionConfig } from '../../config/questionConfig';
import { COLORS } from '../../../assets/config/colors';
import { SPACING } from '../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../assets/config/typography';

interface QuestionProps {
  question: QuestionConfig;
  answer: any;
  onAnswer: (answer: any) => void;
}

export const Question: React.FC<QuestionProps> = ({
  question,
  answer,
  onAnswer,
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

      case 'currency':
        return (
          <div style={styles.currencyInput}>
            <span style={styles.currencySymbol}>$</span>
            <input
              type="number"
              value={answer || ''}
              onChange={(e) => handleChange(parseFloat(e.target.value))}
              min={0}
              step="0.01"
              style={styles.numberInput}
            />
          </div>
        );

      case 'number':
        return (
          <input
            type="number"
            value={answer || ''}
            onChange={(e) => handleChange(parseFloat(e.target.value))}
            min={question.validation?.min || 0}
            max={question.validation?.max}
            style={styles.numberInput}
          />
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

      case 'date':
        return (
          <input
            type="date"
            value={answer || ''}
            onChange={(e) => handleChange(e.target.value)}
            style={styles.dateInput}
          />
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
        {question.required && (
          <span style={styles.requiredIndicator}>*</span>
        )}
      </h3>

      {question.helpText && (
        <div style={styles.helpText}>{question.helpText}</div>
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
  },
  currencyInput: {
    position: 'relative',
    display: 'inline-block'
  },
  currencySymbol: {
    position: 'absolute',
    left: SPACING.sm,
    top: '50%',
    transform: 'translateY(-50%)',
    color: COLORS.text.secondary
  },
  numberInput: {
    paddingLeft: SPACING.xl,
    width: '100%',
    padding: SPACING.sm,
    border: `1px solid ${COLORS.border}`,
    borderRadius: '4px',
    fontSize: TYPOGRAPHY.fontSize.md
  },
  dateInput: {
    width: '100%',
    padding: SPACING.sm,
    border: `1px solid ${COLORS.border}`,
    borderRadius: '4px',
    fontSize: TYPOGRAPHY.fontSize.md
  },
  requiredIndicator: {
    color: COLORS.error,
    marginLeft: SPACING.xs
  }
};
