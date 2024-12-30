import React, { useState, useEffect } from 'react';
import { formFieldStyles } from '../../styles/FormFieldStyles';
import { formSectionStyles } from '../../styles/FormSectionStyles';
import { DocumentCapture } from '../DocumentCapture';
import { ValidationFeedback } from '../ValidationFeedback';
import { FormValidationService } from 'api/services/form/form_validation_service';

interface ScheduleAData {
  medicalExpenses: number;
  taxesPaid: number;
  interestPaid: number;
  charitableGifts: number;
  casualties: number;
  otherDeductions: number;
}

interface ScheduleAProps {
  data: ScheduleAData;
  onUpdate: (data: ScheduleAData) => void;
}

const formValidationService = new FormValidationService();

export const ScheduleA: React.FC<ScheduleAProps> = ({
  data,
  onUpdate
}) => {
  const [validationResults, setValidationResults] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    validateSchedule();
  }, [data]);

  const validateSchedule = async () => {
    try {
      const validation = await formValidationService.validate_section(
        'ScheduleA',
        'itemized_deductions',
        data
      );
      setValidationResults(validation);
    } catch (error) {
      console.error('Error validating Schedule A:', error);
    }
  };

  const handleChange = (field: keyof ScheduleAData, value: string) => {
    onUpdate({
      ...data,
      [field]: parseFloat(value) || 0
    });
  };

  const calculateTotal = () => {
    return Object.values(data).reduce((sum, val) => sum + (val || 0), 0);
  };

  return (
    <div style={formSectionStyles.container}>
      <h3>Schedule A - Itemized Deductions</h3>

      <section style={formSectionStyles.section}>
        <h4>Medical and Dental Expenses</h4>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Medical and Dental Expenses</label>
          <input
            type="number"
            value={data.medicalExpenses || ''}
            onChange={(e) => handleChange('medicalExpenses', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>
      </section>

      <section style={formSectionStyles.section}>
        <h4>Taxes Paid</h4>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>State and Local Taxes</label>
          <input
            type="number"
            value={data.taxesPaid || ''}
            onChange={(e) => handleChange('taxesPaid', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>
      </section>

      <section style={formSectionStyles.section}>
        <h4>Interest Paid</h4>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Home Mortgage Interest</label>
          <input
            type="number"
            value={data.interestPaid || ''}
            onChange={(e) => handleChange('interestPaid', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>
      </section>

      <section style={formSectionStyles.section}>
        <h4>Charitable Contributions</h4>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Gifts by Cash or Check</label>
          <input
            type="number"
            value={data.charitableGifts || ''}
            onChange={(e) => handleChange('charitableGifts', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>
      </section>

      <section style={formSectionStyles.section}>
        <h4>Casualty and Theft Losses</h4>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Casualty and Theft Losses</label>
          <input
            type="number"
            value={data.casualties || ''}
            onChange={(e) => handleChange('casualties', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>
      </section>

      <section style={formSectionStyles.section}>
        <h4>Other Itemized Deductions</h4>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Other Deductions</label>
          <input
            type="number"
            value={data.otherDeductions || ''}
            onChange={(e) => handleChange('otherDeductions', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>
      </section>

      <section style={formSectionStyles.section}>
        <h4>Total Itemized Deductions</h4>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Total</label>
          <input
            type="number"
            value={calculateTotal()}
            style={{ ...formFieldStyles.input, backgroundColor: '#f0f0f0' }}
            disabled
          />
        </div>
      </section>

      <DocumentCapture
        onCapture={async (file) => {
          setIsProcessing(true);
          try {
            // Handle document upload
          } catch (error) {
            console.error('Error processing document:', error);
          } finally {
            setIsProcessing(false);
          }
        }}
        onError={(error) => console.error('Document capture error:', error)}
      />

      {validationResults && (
        <ValidationFeedback
          errors={validationResults.errors}
          warnings={validationResults.warnings}
          suggestions={validationResults.suggestions}
        />
      )}
    </div>
  );
};
