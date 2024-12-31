import React, { useState } from 'react';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';
import { VehicleExpense, ValidationResult } from '../../../types/scheduleC.types';

interface VehicleExpense {
  mileage: number;
  businessUsePercentage: number;
  vehicleDescription: string;
  datePlacedInService: string;
  actualExpenses?: {
    gas: number;
    maintenance: number;
    insurance: number;
    depreciation: number;
    other: number;
  };
}

interface Props {
  data: VehicleExpense;
  onChange: (data: VehicleExpense) => void;
  onValidate?: (result: ValidationResult) => void;
}

export const VehicleExpenseCalculator: React.FC<Props> = ({
  data,
  onChange,
  onValidate
}) => {
  const [useActualExpenses, setUseActualExpenses] = useState(!!data.actualExpenses);
  const standardMileageRate = 0.655; // 2023 IRS standard mileage rate

  const handleChange = (field: keyof VehicleExpense, value: any) => {
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
  };

  const handleActualExpenseChange = (field: keyof typeof data.actualExpenses, value: number) => {
    const updatedData = {
      ...data,
      actualExpenses: {
        ...data.actualExpenses,
        [field]: value
      }
    };
    
    onChange(updatedData);
    onValidate?.({
      isValid: true,
      errors: [],
      warnings: []
    });
  };

  const calculateTotalExpense = () => {
    if (useActualExpenses && data.actualExpenses) {
      return Object.values(data.actualExpenses).reduce((sum, val) => sum + val, 0);
    }
    return data.mileage * standardMileageRate;
  };

  return (
    <section style={formSectionStyles.section}>
      <h4>Vehicle Expenses</h4>
      <div style={formFieldStyles.group}>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Vehicle Description</label>
            <input
              type="text"
              value={data.vehicleDescription}
              onChange={(e) => handleChange('vehicleDescription', e.target.value)}
              style={formFieldStyles.input}
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Date Placed in Service</label>
            <input
              type="date"
              value={data.datePlacedInService}
              onChange={(e) => handleChange('datePlacedInService', e.target.value)}
              style={formFieldStyles.input}
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Business Use Percentage</label>
            <input
              type="number"
              value={data.businessUsePercentage}
              onChange={(e) => handleChange('businessUsePercentage', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              max="100"
              step="1"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Total Business Miles</label>
            <input
              type="number"
              value={data.mileage}
              onChange={(e) => handleChange('mileage', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="1"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.checkbox.container}>
              <input
                type="checkbox"
                checked={useActualExpenses}
                onChange={(e) => setUseActualExpenses(e.target.checked)}
                style={formFieldStyles.checkbox.input}
              />
              Use Actual Expenses Instead of Standard Mileage Rate
            </label>
          </div>
        </div>

        {useActualExpenses && (
          <div style={formFieldStyles.group}>
            <h5>Actual Expenses</h5>
            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Gas and Oil</label>
                <input
                  type="number"
                  value={data.actualExpenses?.gas || 0}
                  onChange={(e) => handleActualExpenseChange('gas', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Maintenance and Repairs</label>
                <input
                  type="number"
                  value={data.actualExpenses?.maintenance || 0}
                  onChange={(e) => handleActualExpenseChange('maintenance', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
            </div>

            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Vehicle Insurance</label>
                <input
                  type="number"
                  value={data.actualExpenses?.insurance || 0}
                  onChange={(e) => handleActualExpenseChange('insurance', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Depreciation</label>
                <input
                  type="number"
                  value={data.actualExpenses?.depreciation || 0}
                  onChange={(e) => handleActualExpenseChange('depreciation', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
            </div>
          </div>
        )}

        <div style={formFieldStyles.total}>
          <label>Total Vehicle Expenses</label>
          <span>${calculateTotalExpense().toFixed(2)}</span>
        </div>
      </div>
    </section>
  );
};
