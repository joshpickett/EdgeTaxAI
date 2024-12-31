import React, { useEffect } from 'react';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { FormIntegrationService } from 'api/services/integration/form_integration_service';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';

interface RentalIncomeExpense {
  income: {
    rents: number;
    other: number;
  };
  expenses: {
    advertising: number;
    auto: number;
    cleaning: number;
    commissions: number;
    insurance: number;
    legal: number;
    management: number;
    mortgage: number;
    repairs: number;
    supplies: number;
    taxes: number;
    utilities: number;
    other: number;
  };
}

interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

interface Props {
  data: RentalIncomeExpense;
  onChange: (data: RentalIncomeExpense) => void;
  onValidate?: (result: ValidationResult) => void;
}

export const IncomeExpenseSection: React.FC<Props> = ({
  data,
  onChange,
  onValidate
}) => {
  const formValidationService = new FormValidationService();
  const formIntegrationService = new FormIntegrationService();

  useEffect(() => {
    const validateAndCalculate = async () => {
      try {
        // Validate with backend service
        const validation = await formValidationService.validate_section(
          'ScheduleE',
          'income_expense',
          data
        );
        
        onValidate?.(validation);
      } catch (error) {
        console.error('Error validating income/expenses:', error);
      }
    };
    validateAndCalculate();
  }, [data]);

  const handleIncomeChange = async (field: keyof typeof data.income, value: number) => {
    try {
      const result = await formIntegrationService.calculateScheduleE({
        income: {
          ...data.income,
          [field]: value
        },
        expenses: data.expenses
      });
      onChange(result);
    } catch (error) {
      console.error('Error calculating rental income:', error);
    }
  };

  const handleExpenseChange = (field: keyof typeof data.expenses, value: number) => {
    onChange({
      ...data,
      expenses: {
        ...data.expenses,
        [field]: value
      }
    });
  };

  const calculateTotalIncome = () => {
    return Object.values(data.income).reduce((sum, val) => sum + (val || 0), 0);
  };

  const calculateTotalExpenses = () => {
    return Object.values(data.expenses).reduce((sum, val) => sum + (val || 0), 0);
  };

  return (
    <div style={formFieldStyles.group}>
      <h4>Income</h4>
      <div style={formFieldStyles.row}>
        <div style={formFieldStyles.column}>
          <label style={formFieldStyles.label}>Rents Received</label>
          <input
            type="number"
            value={data.income.rents}
            onChange={(e) => handleIncomeChange('rents', parseFloat(e.target.value))}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>
        <div style={formFieldStyles.column}>
          <label style={formFieldStyles.label}>Other Income</label>
          <input
            type="number"
            value={data.income.other}
            onChange={(e) => handleIncomeChange('other', parseFloat(e.target.value))}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>
      </div>

      <h4>Expenses</h4>
      {Object.entries(data.expenses).map(([key, value]) => (
        <div key={key} style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>
              {key.charAt(0).toUpperCase() + key.slice(1)}
            </label>
            <input
              type="number"
              value={value}
              onChange={(e) => handleExpenseChange(
                key as keyof typeof data.expenses,
                parseFloat(e.target.value)
              )}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>
      ))}

      <div style={formFieldStyles.totals}>
        <div style={formFieldStyles.total}>
          <label>Total Income</label>
          <span>${calculateTotalIncome().toFixed(2)}</span>
        </div>
        <div style={formFieldStyles.total}>
          <label>Total Expenses</label>
          <span>${calculateTotalExpenses().toFixed(2)}</span>
        </div>
        <div style={formFieldStyles.total}>
          <label>Net Income/Loss</label>
          <span style={{
            color: calculateTotalIncome() - calculateTotalExpenses() >= 0 ? 'green' : 'red'
          }}>
            ${(calculateTotalIncome() - calculateTotalExpenses()).toFixed(2)}
          </span>
        </div>
      </div>
    </div>
  );
};
