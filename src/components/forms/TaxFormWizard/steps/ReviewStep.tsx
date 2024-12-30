import React, { useMemo } from 'react';
import { Form1040Data } from 'shared/types/form1040';
import { formFieldStyles } from '../styles/FormFieldStyles';
import { formSectionStyles } from '../styles/FormSectionStyles';
import { taxService } from 'shared/services/taxService';

interface ReviewStepProps {
  formData: Partial<Form1040Data>;
  onUpdate: (data: Partial<Form1040Data>) => void;
}

export const ReviewStep: React.FC<ReviewStepProps> = ({
  formData,
  onUpdate
}) => {
  const taxSummary = useMemo(() => {
    const income = formData.income?.totalIncome || 0;
    const adjustments = formData.adjustments?.totalAdjustments || 0;
    const credits = formData.credits?.totalCredits || 0;
    const payments = formData.payments?.totalPayments || 0;

    return {
      adjustedGrossIncome: income - adjustments,
      totalTaxCredits: credits,
      totalPayments: payments,
      estimatedRefund: payments - (income - adjustments - credits)
    };
  }, [formData]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div style={formSectionStyles.container}>
      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Personal Information</h3>
        <div style={formFieldStyles.container}>
          <p><strong>Name:</strong> {formData.taxpayerInfo?.firstName} {formData.taxpayerInfo?.lastName}</p>
          <p><strong>SSN:</strong> XXX-XX-{formData.taxpayerInfo?.ssn?.slice(-4)}</p>
          <p><strong>Filing Status:</strong> {formData.taxpayerInfo?.filingStatus?.replace('_', ' ').toUpperCase()}</p>
          <p><strong>Address:</strong> {formData.taxpayerInfo?.address?.street}, {formData.taxpayerInfo?.address?.city}, {formData.taxpayerInfo?.address?.state} {formData.taxpayerInfo?.address?.zipCode}</p>
        </div>
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Income Summary</h3>
        <div style={formFieldStyles.container}>
          {formData.income?.wages > 0 && (
            <p><strong>W-2 Wages:</strong> {formatCurrency(formData.income.wages)}</p>
          )}
          {formData.income?.business > 0 && (
            <p><strong>Business Income:</strong> {formatCurrency(formData.income.business)}</p>
          )}
          {formData.income?.interest > 0 && (
            <p><strong>Interest Income:</strong> {formatCurrency(formData.income.interest)}</p>
          )}
          {formData.income?.dividends > 0 && (
            <p><strong>Dividend Income:</strong> {formatCurrency(formData.income.dividends)}</p>
          )}
          <p><strong>Total Income:</strong> {formatCurrency(formData.income?.totalIncome || 0)}</p>
        </div>
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Adjustments Summary</h3>
        <div style={formFieldStyles.container}>
          {formData.adjustments?.selfEmploymentTax > 0 && (
            <p><strong>Self-Employment Tax Deduction:</strong> {formatCurrency(formData.adjustments.selfEmploymentTax)}</p>
          )}
          {formData.adjustments?.healthInsurance > 0 && (
            <p><strong>Health Insurance:</strong> {formatCurrency(formData.adjustments.healthInsurance)}</p>
          )}
          {formData.adjustments?.retirementContributions > 0 && (
            <p><strong>Retirement Contributions:</strong> {formatCurrency(formData.adjustments.retirementContributions)}</p>
          )}
          <p><strong>Total Adjustments:</strong> {formatCurrency(formData.adjustments?.totalAdjustments || 0)}</p>
        </div>
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Credits Summary</h3>
        <div style={formFieldStyles.container}>
          {formData.credits?.childTaxCredit > 0 && (
            <p><strong>Child Tax Credit:</strong> {formatCurrency(formData.credits.childTaxCredit)}</p>
          )}
          {formData.credits?.earnedIncomeCredit > 0 && (
            <p><strong>Earned Income Credit:</strong> {formatCurrency(formData.credits.earnedIncomeCredit)}</p>
          )}
          <p><strong>Total Credits:</strong> {formatCurrency(formData.credits?.totalCredits || 0)}</p>
        </div>
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Tax Summary</h3>
        <div style={formFieldStyles.container}>
          <p><strong>Adjusted Gross Income:</strong> {formatCurrency(taxSummary.adjustedGrossIncome)}</p>
          <p><strong>Total Tax Credits:</strong> {formatCurrency(taxSummary.totalTaxCredits)}</p>
          <p><strong>Total Payments:</strong> {formatCurrency(taxSummary.totalPayments)}</p>
          <p style={{ 
            fontSize: '1.2em', 
            fontWeight: 'bold',
            color: taxSummary.estimatedRefund >= 0 ? 'green' : 'red'
          }}>
            {taxSummary.estimatedRefund >= 0 ? 'Estimated Refund: ' : 'Amount Due: '}
            {formatCurrency(Math.abs(taxSummary.estimatedRefund))}
          </p>
        </div>
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Required Schedules</h3>
        <div style={formFieldStyles.container}>
          {formData.income?.business > 0 && (
            <p>✓ Schedule C (Business Income)</p>
          )}
          {formData.income?.interest > 0 || formData.income?.dividends > 0 && (
            <p>✓ Schedule B (Interest and Dividends)</p>
          )}
        </div>
      </section>
    </div>
  );
};
