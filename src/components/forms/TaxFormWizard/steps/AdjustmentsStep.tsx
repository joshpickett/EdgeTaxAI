import React, { useState, useEffect } from 'react';
import { Form1040Data } from 'shared/types/form1040';
import { formFieldStyles } from '../styles/FormFieldStyles';
import { formSectionStyles } from '../styles/FormSectionStyles';
import { taxService } from 'shared/services/taxService';

interface AdjustmentsStepProps {
  formData: Partial<Form1040Data>;
  onUpdate: (data: Partial<Form1040Data>) => void;
}

export const AdjustmentsStep: React.FC<AdjustmentsStepProps> = ({
  formData,
  onUpdate
}) => {
  const [selfEmploymentTax, setSelfEmploymentTax] = useState<number>(0);

  useEffect(() => {
    // Calculate self-employment tax if there's business income
    const calculateSelfEmploymentTax = async () => {
      if (formData.income?.business) {
        try {
          const result = await taxService.calculateTaxSavings(formData.income.business);
          setSelfEmploymentTax(result);
          handleAdjustmentChange('selfEmploymentTax', result.toString());
        } catch (error) {
          console.error('Error calculating self-employment tax:', error);
        }
      }
    };

    calculateSelfEmploymentTax();
  }, [formData.income?.business]);

  const handleAdjustmentChange = (field: string, value: string) => {
    onUpdate({
      ...formData,
      adjustments: {
        ...formData.adjustments,
        [field]: parseFloat(value) || 0
      }
    });
  };

  const calculateTotalAdjustments = () => {
    const adjustments = formData.adjustments || {};
    return Object.values(adjustments).reduce((sum, val) => sum + (val || 0), 0);
  };

  return (
    <div style={formSectionStyles.container}>
      {formData.income?.business > 0 && (
        <section style={formSectionStyles.container}>
          <h3 style={formSectionStyles.title}>Self-Employment Adjustments</h3>
          <div style={formFieldStyles.container}>
            <label style={formFieldStyles.label}>Self-Employment Tax Deduction</label>
            <input
              type="number"
              value={formData.adjustments?.selfEmploymentTax || ''}
              onChange={(e) => handleAdjustmentChange('selfEmploymentTax', e.target.value)}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
            <p style={formSectionStyles.helpText}>
              Based on your self-employment income, you can deduct half of your self-employment tax.
            </p>
          </div>

          <div style={formFieldStyles.container}>
            <label style={formFieldStyles.label}>Self-Employed Health Insurance</label>
            <input
              type="number"
              value={formData.adjustments?.healthInsurance || ''}
              onChange={(e) => handleAdjustmentChange('healthInsurance', e.target.value)}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </section>
      )}

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Retirement Contributions</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>IRA Contributions</label>
          <input
            type="number"
            value={formData.adjustments?.retirementContributions || ''}
            onChange={(e) => handleAdjustmentChange('retirementContributions', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Other Adjustments</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Student Loan Interest</label>
          <input
            type="number"
            value={formData.adjustments?.studentLoanInterest || ''}
            onChange={(e) => handleAdjustmentChange('studentLoanInterest', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>

        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Other Adjustments</label>
          <input
            type="number"
            value={formData.adjustments?.otherAdjustments || ''}
            onChange={(e) => handleAdjustmentChange('otherAdjustments', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Total Adjustments</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>
            Total Adjustments to Income for {new Date().getFullYear()}
          </label>
          <input
            type="number"
            value={calculateTotalAdjustments()}
            style={{ ...formFieldStyles.input, backgroundColor: '#f0f0f0' }}
            disabled
          />
        </div>
      </section>
    </div>
  );
};
