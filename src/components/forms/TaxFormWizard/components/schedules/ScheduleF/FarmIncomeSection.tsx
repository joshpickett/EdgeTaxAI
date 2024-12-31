import React, { useEffect } from 'react';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { FormIntegrationService } from 'api/services/integration/form_integration_service';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';

interface FarmIncome {
  salesLivestock: number;
  salesProduce: number;
  salesBreeding: number;
  customHireIncome: number;
  cooperativeDistributions: number;
  agriculturalPayments: number;
  commodityPayments: number;
  cropInsurance: number;
  otherIncome: number;
}

interface Props {
  data: FarmIncome;
  onChange: (data: FarmIncome) => void;
}

export const FarmIncomeSection: React.FC<Props> = ({
  data,
  onChange
}) => {
  const formValidationService = new FormValidationService();
  const formIntegrationService = new FormIntegrationService();

  useEffect(() => {
    const validateAndCalculate = async () => {
      try {
        // Validate with backend service
        const validation = await formValidationService.validate_section(
          'ScheduleF',
          'farm_income',
          data
        );
        
        onValidate?.(validation);
      } catch (error) {
        console.error('Error validating farm income:', error);
      }
    };
    validateAndCalculate();
  }, [data]);

  const handleChange = (field: keyof FarmIncome, value: number) => {
    onChange({
      ...data,
      [field]: value
    });
  };

  const calculateTotalIncome = () => {
    return Object.values(data).reduce((sum, val) => sum + (val || 0), 0);
  };

  return (
    <section style={formSectionStyles.section}>
      <h4>Farm Income</h4>
      <div style={formFieldStyles.group}>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Sales of Livestock</label>
            <input
              type="number"
              value={data.salesLivestock}
              onChange={(e) => handleChange('salesLivestock', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Sales of Produce</label>
            <input
              type="number"
              value={data.salesProduce}
              onChange={(e) => handleChange('salesProduce', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Cooperative Distributions</label>
            <input
              type="number"
              value={data.cooperativeDistributions}
              onChange={(e) => handleChange('cooperativeDistributions', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Agricultural Program Payments</label>
            <input
              type="number"
              value={data.agriculturalPayments}
              onChange={(e) => handleChange('agriculturalPayments', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Commodity Credit Loans</label>
            <input
              type="number"
              value={data.commodityPayments}
              onChange={(e) => handleChange('commodityPayments', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Crop Insurance Proceeds</label>
            <input
              type="number"
              value={data.cropInsurance}
              onChange={(e) => handleChange('cropInsurance', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Custom Hire Income</label>
            <input
              type="number"
              value={data.customHireIncome}
              onChange={(e) => handleChange('customHireIncome', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Other Farm Income</label>
            <input
              type="number"
              value={data.otherIncome}
              onChange={(e) => handleChange('otherIncome', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Sales of Breeding Livestock</label>
            <input
              type="number"
              value={data.salesBreeding}
              onChange={(e) => handleChange('salesBreeding', parseFloat(e.target.value))}
              style={formFieldStyles.input}
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Custom Hire Income</label>
            <input
              type="number"
              value={data.customHireIncome}
              onChange={(e) => handleChange('customHireIncome', parseFloat(e.target.value))}
              style={formFieldStyles.input}
            />
          </div>
        </div>

        <div style={formFieldStyles.total}>
          <label>Total Farm Income</label>
          <span>${calculateTotalIncome().toFixed(2)}</span>
        </div>
      </div>
    </section>
  );
};
