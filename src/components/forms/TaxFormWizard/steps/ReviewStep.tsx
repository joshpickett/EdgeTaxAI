import React, { useMemo, useState, useEffect } from 'react';
import { Form1040Data } from 'shared/types/form1040';
import { FormIntegrationService } from 'api/services/integration/form_integration_service';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { formFieldStyles } from '../styles/FormFieldStyles';
import { formSectionStyles } from '../styles/FormSectionStyles';

interface ReviewStepProps {
  formData: Partial<Form1040Data>;
  onUpdate: (data: Partial<Form1040Data>) => void;
}

const formIntegrationService = new FormIntegrationService();
const formValidationService = new FormValidationService();

export const ReviewStep: React.FC<ReviewStepProps> = ({
  formData,
  onUpdate
}) => {
  const [reviewResults, setReviewResults] = useState(null);
  const [validationResults, setValidationResults] = useState(null);
  const [paymentOptions, setPaymentOptions] = useState(null);

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

  useEffect(() => {
    const performReview = async () => {
      try {
        const results = await formIntegrationService.review_form_submission(
          formData.userId,
          new Date().getFullYear(),
          formData
        );
        setReviewResults(results);

        const validation = await formValidationService.validate_section(
          'Form1040',
          'review',
          formData
        );
        setValidationResults(validation);
        
        // Get payment options
        const paymentData = await formIntegrationService.initialize_payment_options(
            formData.userId,
            'Form1040',
            formData
        );
        setPaymentOptions(paymentData);

      } catch (error) {
        console.error('Error reviewing form:', error);
      }
    };
    performReview();
  }, [formData]);

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
            <p>✔ Schedule C (Business Income)</p>
          )}
          {formData.income?.interest > 0 || formData.income?.dividends > 0 && (
            <p>✔ Schedule B (Interest and Dividends)</p>
          )}
        </div>
      </section>

      {reviewResults && (
        <section style={formSectionStyles.container}>
          <h3>Review Results</h3>
          {reviewResults.review_status.errors.map((error, index) => (
            <div key={index} style={formFieldStyles.error}>
              {error.message}
            </div>
          ))}
          {reviewResults.optimization_suggestions.map((suggestion, index) => (
            <div key={index} style={formFieldStyles.suggestion}>
              {suggestion.message}
            </div>
          ))}
        </section>
      )}

      {reviewResults?.optimization_suggestions?.length > 0 && (
        <section style={formSectionStyles.container}>
          <h3>Final Optimization Opportunities</h3>
          {reviewResults.optimization_suggestions.map((suggestion, index) => (
            <div key={index} style={formFieldStyles.suggestion}>
              <p>{suggestion.description}</p>
              <p>Potential Impact: ${suggestion.potentialSavings}</p>
            </div>
          ))}
        </section>
      )}

      {validationResults?.errors?.length > 0 && (
        <section style={formSectionStyles.container}>
          <h3 style={{ color: 'red' }}>Required Corrections</h3>
          {validationResults.errors.map((error, index) => (
            <div key={index} style={formFieldStyles.error}>
              {error.message}
            </div>
          ))}
        </section>
      )}

      {paymentOptions && (
        <section style={formSectionStyles.container}>
          <h3>Payment Options</h3>
          
          {paymentOptions.payment_plans.map((plan, index) => (
            <div key={index} style={formFieldStyles.paymentOption}>
              <h4>{plan.plan_type}</h4>
              <p>Monthly Payment: {formatCurrency(plan.monthly_payment)}</p>
              <p>Total Payment: {formatCurrency(plan.total_payment)}</p>
              <p>Setup Fee: {formatCurrency(plan.setup_fee)}</p>
              <button
                onClick={() => handleSelectPaymentPlan(plan)}
                style={formFieldStyles.button.secondary}
              >
                Select Plan
              </button>
            </div>
          ))}
          
          <div style={formFieldStyles.paymentMethods}>
            <h4>Payment Methods</h4>
            {paymentOptions.payment_methods.map((method, index) => (
              <div key={index} style={formFieldStyles.paymentMethod}>
                <input
                  type="radio"
                  name="paymentMethod"
                  value={method.id}
                  onChange={() => handleSelectPaymentMethod(method)}
                />
                <label>{method.name}</label>
                {method.fees > 0 && (
                  <span style={formFieldStyles.fees}>
                    {(method.fees * 100).toFixed(1)}% fee
                  </span>
                )}
              </div>
            ))}
          </div>
          
          {paymentOptions.estimated_payments && (
            <div style={formFieldStyles.estimatedPayments}>
              <h4>Estimated Tax Payments</h4>
              {/* Add estimated payment schedule display */}
            </div>
          )}
        </section>
      )}
    </div>
  );
};
