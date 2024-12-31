import React, { useState, useEffect } from 'react';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';
import { DocumentCapture } from '../../../DocumentCapture';
import { ValidationFeedback } from '../../../ValidationFeedback';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { FarmInfoSection } from './FarmInfoSection';
import { FarmIncomeSection } from './FarmIncomeSection';
import { FarmExpenseSection } from './FarmExpenseSection';
import { FarmSummarySection } from './FarmSummarySection';
import { taxService } from '../../../services/taxService';

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
  beginningInventory: number;
  endingInventory: number;
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

export const ScheduleF: React.FC<Props> = ({
  data,
  onUpdate
}) => {
  const [calculatedTotals, setCalculatedTotals] = useState(null);
  const [validationResults, setValidationResults] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    validateSchedule();
  }, [data]);

  useEffect(() => {
    const calculateTotals = async () => {
      try {
        const result = await taxService.calculateScheduleFTotals(data);
        setCalculatedTotals(result);
        onUpdate({
          ...data,
          ...result
        });
      } catch (error) {
        console.error('Error calculating totals:', error);
      }
    };
    calculateTotals();
  }, [data.income, data.expenses]);

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
      <FarmInfoSection
        data={data.farmInfo}
        onChange={handleFarmInfoChange}
      />
      <FarmIncomeSection
        data={data.income}
        onChange={handleIncomeChange}
      />
      <FarmExpenseSection
        data={data.expenses}
        onChange={handleExpenseChange}
      />
      <FarmSummarySection
        data={calculatedTotals}
      />
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
