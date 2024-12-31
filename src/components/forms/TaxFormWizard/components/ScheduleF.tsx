import React, { useState, useEffect } from 'react';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';
import { DocumentCapture } from '../../../DocumentCapture';
import { ValidationFeedback } from '../../../ValidationFeedback';
import { FormValidationService } from 'api/services/form/form_validation_service';

interface FarmIncome {
  salesLivestock: number;
  salesProduce: number;
  cooperativeDistributions: number;
  agriculturalPayments: number;
  commodityPayments: number;
  cropInsurance: number;
  customHire: number;
  otherIncome: number;
  totalIncome: number;
}

interface FarmExpenses {
  carTruck: number;
  chemicals: number;
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
  totalExpenses: number;
}

interface ScheduleFData {
  farmInfo: {
    name: string;
    address: string;
    principalProduct: string;
    accountingMethod: 'Cash' | 'Accrual';
  };
  income: FarmIncome;
  expenses: FarmExpenses;
  netFarmProfit: number;
}

interface Props {
  data: ScheduleFData;
  onUpdate: (data: ScheduleFData) => void;
}

const formValidationService = new FormValidationService();

export const ScheduleF_Old: React.FC<Props> = ({
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
        'ScheduleF',
        'farm_income',
        data
      );
      setValidationResults(validation);
    } catch (error) {
      console.error('Error validating Schedule F:', error);
    }
  };

  const handleFarmInfoChange = (field: string, value: string) => {
    const updatedData = {
      ...data,
      farmInfo: {
        ...data.farmInfo,
        [field]: value
      }
    };
    onUpdate(updatedData);
  };

  const handleIncomeChange = (field: keyof FarmIncome, value: number) => {
    const updatedIncome = {
      ...data.income,
      [field]: value
    };

    // Calculate total income
    updatedIncome.totalIncome = Object.values(updatedIncome)
      .reduce((sum, val) => typeof val === 'number' ? sum + val : sum, 0);

    const updatedData = {
      ...data,
      income: updatedIncome,
      netFarmProfit: updatedIncome.totalIncome - data.expenses.totalExpenses
    };

    onUpdate(updatedData);
  };

  const handleExpenseChange = (field: keyof FarmExpenses, value: number) => {
    const updatedExpenses = {
      ...data.expenses,
      [field]: value
    };

    // Calculate total expenses
    updatedExpenses.totalExpenses = Object.values(updatedExpenses)
      .reduce((sum, val) => typeof val === 'number' ? sum + val : sum, 0);

    const updatedData = {
      ...data,
      expenses: updatedExpenses,
      netFarmProfit: data.income.totalIncome - updatedExpenses.totalExpenses
    };

    onUpdate(updatedData);
  };

  return (
    <div style={formSectionStyles.container}>
      <h3>Schedule F - Profit or Loss From Farming</h3>

      <section style={formSectionStyles.section}>
        <h4>Farm Information</h4>
        <div style={formFieldStyles.group}>
          <div style={formFieldStyles.row}>
            <div style={formFieldStyles.column}>
              <label style={formFieldStyles.label}>Farm Name</label>
              <input
                type="text"
                value={data.farmInfo.name}
                onChange={(e) => handleFarmInfoChange('name', e.target.value)}
                style={formFieldStyles.input}
              />
            </div>
            <div style={formFieldStyles.column}>
              <label style={formFieldStyles.label}>Principal Product</label>
              <input
                type="text"
                value={data.farmInfo.principalProduct}
                onChange={(e) => handleFarmInfoChange('principalProduct', e.target.value)}
                style={formFieldStyles.input}
              />
            </div>
          </div>

          <div style={formFieldStyles.row}>
            <div style={formFieldStyles.column}>
              <label style={formFieldStyles.label}>Farm Address</label>
              <input
                type="text"
                value={data.farmInfo.address}
                onChange={(e) => handleFarmInfoChange('address', e.target.value)}
                style={formFieldStyles.input}
              />
            </div>
            <div style={formFieldStyles.column}>
              <label style={formFieldStyles.label}>Accounting Method</label>
              <select
                value={data.farmInfo.accountingMethod}
                onChange={(e) => handleFarmInfoChange('accountingMethod', e.target.value as 'Cash' | 'Accrual')}
                style={formFieldStyles.select}
              >
                <option value="Cash">Cash</option>
                <option value="Accrual">Accrual</option>
              </select>
            </div>
          </div>
        </div>
      </section>

      <section style={formSectionStyles.section}>
        <h4>Farm Income</h4>
        <div style={formFieldStyles.group}>
          {Object.entries(data.income).map(([key, value]) => {
            if (key !== 'totalIncome') {
              return (
                <div key={key} style={formFieldStyles.row}>
                  <div style={formFieldStyles.column}>
                    <label style={formFieldStyles.label}>
                      {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                    </label>
                    <input
                      type="number"
                      value={value}
                      onChange={(e) => handleIncomeChange(key as keyof FarmIncome, parseFloat(e.target.value))}
                      style={formFieldStyles.input}
                      min="0"
                      step="0.01"
                    />
                  </div>
                </div>
              );
            }
            return null;
          })}
          <div style={formFieldStyles.total}>
            <label>Total Farm Income</label>
            <span>${data.income.totalIncome.toFixed(2)}</span>
          </div>
        </div>
      </section>

      <section style={formSectionStyles.section}>
        <h4>Farm Expenses</h4>
        <div style={formFieldStyles.group}>
          {Object.entries(data.expenses).map(([key, value]) => {
            if (key !== 'totalExpenses') {
              return (
                <div key={key} style={formFieldStyles.row}>
                  <div style={formFieldStyles.column}>
                    <label style={formFieldStyles.label}>
                      {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                    </label>
                    <input
                      type="number"
                      value={value}
                      onChange={(e) => handleExpenseChange(key as keyof FarmExpenses, parseFloat(e.target.value))}
                      style={formFieldStyles.input}
                      min="0"
                      step="0.01"
                    />
                  </div>
                </div>
              );
            }
            return null;
          })}
          <div style={formFieldStyles.total}>
            <label>Total Farm Expenses</label>
            <span>${data.expenses.totalExpenses.toFixed(2)}</span>
          </div>
        </div>
      </section>

      <section style={formSectionStyles.section}>
        <h4>Net Farm Profit or Loss</h4>
        <div style={formFieldStyles.total}>
          <label>Net Farm Profit/Loss</label>
          <span style={{
            color: data.netFarmProfit >= 0 ? '#2e7d32' : '#c62828'
          }}>
            ${data.netFarmProfit.toFixed(2)}
          </span>
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

export default ScheduleF;
