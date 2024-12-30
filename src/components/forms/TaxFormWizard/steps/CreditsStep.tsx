import React, { useState, useEffect } from 'react';
import { Form1040Data } from 'shared/types/form1040';
import { FormIntegrationService } from 'api/services/integration/form_integration_service';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { formFieldStyles } from '../styles/FormFieldStyles';
import { formSectionStyles } from '../styles/FormSectionStyles';

const formIntegrationService = new FormIntegrationService();
const formValidationService = new FormValidationService();

interface CreditsStepProps {
  formData: Partial<Form1040Data>;
  onUpdate: (data: Partial<Form1040Data>) => void;
}

export const CreditsStep: React.FC<CreditsStepProps> = ({
  formData,
  onUpdate
}) => {
  const [hasQualifyingChildren, setHasQualifyingChildren] = useState(false);
  const [hasEducationExpenses, setHasEducationExpenses] = useState(false);
  const [validationResults, setValidationResults] = useState(null);
  const [optimizationSuggestions, setOptimizationSuggestions] = useState([]);

  useEffect(() => {
    // Reset credits when qualifying conditions change
    if (!hasQualifyingChildren) {
      handleCreditChange('childTaxCredit', '0');
      handleCreditChange('qualifyingChildren', '0');
    }
    if (!hasEducationExpenses) {
      handleCreditChange('educationCredit', '0');
    }
  }, [hasQualifyingChildren, hasEducationExpenses]);

  useEffect(() => {
    const validateCredits = async () => {
      try {
        const validation = await formValidationService.validate_field(
          'Form1040',
          'credits',
          formData.credits,
          formData
        );
        setValidationResults(validation);

        const suggestions = await formIntegrationService.getOptimizationOpportunities(
          formData.userId,
          'Form1040',
          formData
        );
        setOptimizationSuggestions(suggestions);
      } catch (error) {
        console.error('Error validating credits:', error);
      }
    };
    validateCredits();
  }, [formData.credits]);

  const handleCreditChange = (field: string, value: string) => {
    onUpdate({
      ...formData,
      credits: {
        ...formData.credits,
        [field]: parseFloat(value) || 0
      }
    });
  };

  const calculateTotalCredits = () => {
    const credits = formData.credits || {};
    return Object.values(credits).reduce((sum, val) => sum + (val || 0), 0);
  };

  return (
    <div style={formSectionStyles.container}>
      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Child Tax Credit</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.checkbox.container}>
            <input
              type="checkbox"
              checked={hasQualifyingChildren}
              onChange={(e) => setHasQualifyingChildren(e.target.checked)}
              style={formFieldStyles.checkbox.input}
            />
            I have qualifying children under 17
          </label>
        </div>

        {hasQualifyingChildren && (
          <>
            <div style={formFieldStyles.container}>
              <label style={formFieldStyles.label}>Number of Qualifying Children</label>
              <input
                type="number"
                value={formData.credits?.qualifyingChildren || ''}
                onChange={(e) => handleCreditChange('qualifyingChildren', e.target.value)}
                style={formFieldStyles.input}
                min="0"
                max="99"
              />
            </div>

            <div style={formFieldStyles.container}>
              <label style={formFieldStyles.label}>Child Tax Credit Amount</label>
              <input
                type="number"
                value={formData.credits?.childTaxCredit || ''}
                onChange={(e) => handleCreditChange('childTaxCredit', e.target.value)}
                style={formFieldStyles.input}
                min="0"
                step="0.01"
              />
            </div>
          </>
        )}
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Education Credits</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.checkbox.container}>
            <input
              type="checkbox"
              checked={hasEducationExpenses}
              onChange={(e) => setHasEducationExpenses(e.target.checked)}
              style={formFieldStyles.checkbox.input}
            />
            I have qualifying education expenses
          </label>
        </div>

        {hasEducationExpenses && (
          <div style={formFieldStyles.container}>
            <label style={formFieldStyles.label}>Education Credit Amount</label>
            <input
              type="number"
              value={formData.credits?.educationCredit || ''}
              onChange={(e) => handleCreditChange('educationCredit', e.target.value)}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        )}
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Earned Income Credit</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Earned Income Credit Amount</label>
          <input
            type="number"
            value={formData.credits?.earnedIncomeCredit || ''}
            onChange={(e) => handleCreditChange('earnedIncomeCredit', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Other Credits</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Other Credits Amount</label>
          <input
            type="number"
            value={formData.credits?.otherCredits || ''}
            onChange={(e) => handleCreditChange('otherCredits', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Total Credits</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>
            Total Tax Credits for {new Date().getFullYear()}
          </label>
          <input
            type="number"
            value={calculateTotalCredits()}
            style={{ ...formFieldStyles.input, backgroundColor: '#f0f0f0' }}
            disabled
          />
        </div>
      </section>

      {optimizationSuggestions.length > 0 && (
        <section style={formSectionStyles.container}>
          <h3>Credit Optimization Suggestions</h3>
          {optimizationSuggestions.map((suggestion, index) => (
            <div key={index} style={formFieldStyles.suggestion}>
              <p>{suggestion.description}</p>
              <p>Potential Additional Credits: ${suggestion.potentialSavings}</p>
            </div>
          ))}
        </section>
      )}
    </div>
  );
};
