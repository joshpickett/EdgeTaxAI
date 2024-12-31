import React, { useEffect } from 'react';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { FormIntegrationService } from 'api/services/integration/form_integration_service';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';
import { HomeOfficeExpense, ValidationResult } from '../../../types/scheduleC.types';

interface HomeOfficeExpense {
  totalSquareFeet: number;
  businessSquareFeet: number;
  percentage: number;
  expenses: {
    rent?: number;
    mortgage?: number;
    insurance: number;
    utilities: number;
    repairs: number;
    depreciation?: number;
  };
}

interface Props {
  data: HomeOfficeExpense;
  onChange: (data: HomeOfficeExpense) => void;
  onValidate?: (result: ValidationResult) => void;
}

const formValidationService = new FormValidationService();
const formIntegrationService = new FormIntegrationService();

export const HomeOfficeCalculator: React.FC<Props> = ({
  data,
  onChange,
  onValidate
}) => {
  useEffect(() => {
    const validateHomeOffice = async () => {
      try {
        const validation = await formValidationService.validate_section(
          'ScheduleC',
          'home_office',
          data
        );
        onValidate?.(validation);
      } catch (error) {
        console.error('Error validating home office:', error);
      }
    };
    validateHomeOffice();
  }, [data]);

  const handleChange = (field: keyof HomeOfficeExpense, value: any) => {
    const updatedData = {
      ...data,
      [field]: value
    };
    
    onChange(updatedData);
    onValidate?.({
      isValid: true,
      errors: [],
      warnings: []
    });

    if (field === 'totalSquareFeet' || field === 'businessSquareFeet') {
      const total = field === 'totalSquareFeet' ? value : data.totalSquareFeet;
      const business = field === 'businessSquareFeet' ? value : data.businessSquareFeet;
      const percentage = (business / total) * 100;

      onChange({
        ...data,
        [field]: value,
        percentage
      });
    } else {
      onChange({
        ...data,
        [field]: value
      });
    }
  };

  const handleExpenseChange = (field: keyof typeof data.expenses, value: number) => {
    const updateExpenses = async () => {
      try {
        const result = await formIntegrationService.calculateHomeOfficeExpenses({
          ...data,
          expenses: {
            ...data.expenses,
            [field]: value
          }
        });
        onChange(result);
      } catch (error) {
        console.error('Error calculating home office expenses:', error);
      }
    };
    updateExpenses();
  };

  const calculateTotalExpense = () => {
    const totalExpenses = Object.values(data.expenses).reduce((sum, val) => sum + (val || 0), 0);
    return (totalExpenses * data.percentage) / 100;
  };

  return (
    <section style={formSectionStyles.section}>
      <h4>Home Office Deduction</h4>
      <div style={formFieldStyles.group}>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Total Home Square Feet</label>
            <input
              type="number"
              value={data.totalSquareFeet}
              onChange={(e) => handleChange('totalSquareFeet', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="1"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Business Use Square Feet</label>
            <input
              type="number"
              value={data.businessSquareFeet}
              onChange={(e) => handleChange('businessSquareFeet', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="1"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Business Use Percentage</label>
            <input
              type="number"
              value={data.percentage}
              disabled
              style={{ ...formFieldStyles.input, backgroundColor: '#f0f0f0' }}
            />
          </div>
        </div>

        <h5>Home Expenses</h5>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Rent</label>
            <input
              type="number"
              value={data.expenses.rent || 0}
              onChange={(e) => handleExpenseChange('rent', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Mortgage Interest</label>
            <input
              type="number"
              value={data.expenses.mortgage || 0}
              onChange={(e) => handleExpenseChange('mortgage', parseFloat(e.target.value))}
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
              value={data.expenses.insurance}
              onChange={(e) => handleExpenseChange('insurance', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Utilities</label>
            <input
              type="number"
              value={data.expenses.utilities}
              onChange={(e) => handleExpenseChange('utilities', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Repairs and Maintenance</label>
            <input
              type="number"
              value={data.expenses.repairs}
              onChange={(e) => handleExpenseChange('repairs', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Depreciation</label>
            <input
              type="number"
              value={data.expenses.depreciation || 0}
              onChange={(e) => handleExpenseChange('depreciation', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.total}>
          <label>Total Home Office Deduction</label>
          <span>${calculateTotalExpense().toFixed(2)}</span>
        </div>
      </div>
    </section>
  );
};
