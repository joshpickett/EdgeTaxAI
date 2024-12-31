import React, { useEffect } from 'react';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { FormIntegrationService } from 'api/services/integration/form_integration_service';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';

interface FarmSummaryData {
  grossIncome: number;
  totalExpenses: number;
  totalAgriculturalPayments: number;
  totalCommodityPayments: number;
  cropInsuranceProceeds: number;
  netProfit: number;
  depreciation: number;
  inventory: {
    beginning: number;
    ending: number;
  };
  selfEmploymentTax: number;
}

interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

interface Props {
  data: FarmSummaryData;
  onValidate?: (result: ValidationResult) => void;
}

export const FarmSummarySection: React.FC<Props> = ({ 
  data,
  onValidate 
}) => {
  const formValidationService = new FormValidationService();
  const formIntegrationService = new FormIntegrationService();

  useEffect(() => {
    const validateAndCalculate = async () => {
      try {
        // Validate with backend service
        const validation = await formValidationService.validate_section(
          'ScheduleF',
          'farm_summary',
          data
        );
        
        onValidate?.(validation);

        // Calculate totals
        const calculatedTotals = await formIntegrationService.calculateFarmTotals(data);
        if (calculatedTotals) {
          onUpdate(calculatedTotals);
        }
      } catch (error) {
        console.error('Error validating farm summary:', error);
      }
    };
    validateAndCalculate();
  }, [data]);

  return (
    <section style={formSectionStyles.section}>
      <h4>Farm Income Summary</h4>
      <div style={formFieldStyles.group}>
        <div style={formFieldStyles.summaryRow}>
          <label>Gross Farm Income</label>
          <span>${data.grossIncome.toFixed(2)}</span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Total Farm Expenses</label>
          <span>${data.totalExpenses.toFixed(2)}</span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Depreciation</label>
          <span>${data.depreciation.toFixed(2)}</span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Beginning Inventory</label>
          <span>${data.inventory.beginning.toFixed(2)}</span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Ending Inventory</label>
          <span>${data.inventory.ending.toFixed(2)}</span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Agricultural Program Payments</label>
          <span>${data.totalAgriculturalPayments.toFixed(2)}</span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Commodity Credit Loans</label>
          <span>${data.totalCommodityPayments.toFixed(2)}</span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Crop Insurance Proceeds</label>
          <span>${data.cropInsuranceProceeds.toFixed(2)}</span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Inventory Change</label>
          <span>${(data.inventory.ending - data.inventory.beginning).toFixed(2)}</span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Net Farm Profit/Loss</label>
          <span style={{
            color: data.netProfit >= 0 ? '#2e7d32' : '#c62828',
            fontWeight: 'bold'
          }}>
            ${data.netProfit.toFixed(2)}
          </span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Self-Employment Tax</label>
          <span>${data.selfEmploymentTax.toFixed(2)}</span>
        </div>
      </div>
    </section>
  );
};
