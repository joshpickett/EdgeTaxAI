import React, { useEffect } from 'react';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { FormIntegrationService } from 'api/services/integration/form_integration_service';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';

interface FarmExpenses {
  carTruck: number;
  chemicals: number;
  livestock: number;
  breeding: number;
  conservation: number;
  customHire: number;
  depreciation: number;
  employeeBenefit: number;
  feed: number;
  fertilizers: number;
  freight: number;
  fuel: number;
  insurance: number;
  interest: number;
  labor: number;
  pension: number;
  rentLease: number;
  repairs: number;
  seeds: number;
  storage: number;
  supplies: number;
  taxes: number;
  utilities: number;
  veterinary: number;
  otherExpenses: number;
}

interface Props {
  data: FarmExpenses;
  onChange: (data: FarmExpenses) => void;
}

export const FarmExpenseSection: React.FC<Props> = ({
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
          'farm_expenses',
          data
        );
        
        onValidate?.(validation);
      } catch (error) {
        console.error('Error validating farm expenses:', error);
      }
    };
    validateAndCalculate();
  }, [data]);

  const handleExpenseChange = (field: keyof FarmExpenses, value: number) => {
    onChange({
      ...data,
      [field]: value
    });
  };

  const calculateTotalExpenses = () => {
    return Object.values(data).reduce((sum, val) => sum + (val || 0), 0);
  };

  return (
    <section style={formSectionStyles.section}>
      <h4>Farm Expenses</h4>
      <div style={formFieldStyles.group}>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Car and Truck Expenses</label>
            <input
              type="number"
              value={data.carTruck}
              onChange={(e) => handleExpenseChange('carTruck', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Chemicals</label>
            <input
              type="number"
              value={data.chemicals}
              onChange={(e) => handleExpenseChange('chemicals', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Conservation Expenses</label>
            <input
              type="number"
              value={data.conservation}
              onChange={(e) => handleExpenseChange('conservation', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Custom Hire</label>
            <input
              type="number"
              value={data.customHire}
              onChange={(e) => handleExpenseChange('customHire', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Depreciation</label>
            <input
              type="number"
              value={data.depreciation}
              onChange={(e) => handleExpenseChange('depreciation', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Employee Benefits</label>
            <input
              type="number"
              value={data.employeeBenefit}
              onChange={(e) => handleExpenseChange('employeeBenefit', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Feed</label>
            <input
              type="number"
              value={data.feed}
              onChange={(e) => handleExpenseChange('feed', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Fertilizers</label>
            <input
              type="number"
              value={data.fertilizers}
              onChange={(e) => handleExpenseChange('fertilizers', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Freight and Trucking</label>
            <input
              type="number"
              value={data.freight}
              onChange={(e) => handleExpenseChange('freight', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Gasoline, Fuel, and Oil</label>
            <input
              type="number"
              value={data.fuel}
              onChange={(e) => handleExpenseChange('fuel', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Insurance</label>
            <input
              type="number"
              value={data.insurance}
              onChange={(e) => handleExpenseChange('insurance', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Interest</label>
            <input
              type="number"
              value={data.interest}
              onChange={(e) => handleExpenseChange('interest', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.total}>
          <label>Total Farm Expenses</label>
          <span>${calculateTotalExpenses().toFixed(2)}</span>
        </div>
        
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Livestock Purchases</label>
            <input
              type="number"
              value={data.livestock}
              onChange={(e) => handleExpenseChange('livestock', parseFloat(e.target.value))}
              style={formFieldStyles.input}
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Breeding Fees</label>
            <input
              type="number"
              value={data.breeding}
              onChange={(e) => handleExpenseChange('breeding', parseFloat(e.target.value))}
              style={formFieldStyles.input}
            />
          </div>
        </div>
      </div>
    </section>
  );
};
