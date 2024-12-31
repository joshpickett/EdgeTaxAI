import React, { useState, useCallback, useEffect } from 'react';
import { BusinessInfoSection } from './ScheduleC/BusinessInfoSection';
import { IncomeSection } from './ScheduleC/IncomeSection';
import { ExpenseSection } from './ScheduleC/ExpenseSection';
import { VehicleExpenseCalculator } from './ScheduleC/VehicleExpenseCalculator';
import { HomeOfficeCalculator } from './ScheduleC/HomeOfficeCalculator';
import { ScheduleCCalculator } from '../services/scheduleC.calculator';
import { ScheduleCValidator } from '../services/scheduleC.validator';
import { ScheduleCData, ValidationResult, CalculationResult } from '../types/scheduleC.types';

interface Props {
  data: ScheduleCData;
  onUpdate: (data: any) => void;
  onValidate?: (result: ValidationResult) => void;
  onCalculate?: (result: CalculationResult) => void;
}

const ScheduleC: React.FC<Props> = ({ 
  data, 
  onUpdate,
  onValidate,
  onCalculate 
}) => {
  const [validationResult, setValidationResult] = useState<ValidationResult>({
    isValid: true,
    errors: [],
    warnings: []
  });

  const calculator = new ScheduleCCalculator();
  const validator = new ScheduleCValidator();

  useEffect(() => {
    // Recalculate totals whenever data changes
    const totals = calculator.calculateTotals(data);
    onUpdate({
      ...data,
      totals
    });
    
    // Validate data
    const validationResult = validator.validateComplete(data);
    setValidationResult(validationResult);
    onValidate?.(validationResult);
    
    // Calculate and notify parent
    const calculations = {
      grossIncome: totals.grossIncome,
      totalExpenses: totals.totalExpenses,
      netProfit: totals.netProfit,
      selfEmploymentTax: totals.selfEmploymentTax,
      estimatedTax: calculator.calculateEstimatedTax(totals.netProfit)
    };
    onCalculate?.(calculations);
  }, [data]);

  const handleIncomeChange = (incomeData: any) => {
    onUpdate({
      ...data,
      income: incomeData
    });
  };

  const handleExpenseChange = (expenseData: any) => {
    onUpdate({
      ...data,
      expenses: expenseData.categories,
      totalExpenses: expenseData.totalExpenses
    });
  };

  return (
    <div>
      <BusinessInfoSection 
        data={data.businessInfo} 
        onChange={handleBusinessInfoChange}
        onValidate={handleValidation} 
      />
      <IncomeSection 
        data={data.income} 
        onChange={handleIncomeChange}
        onValidate={handleValidation}
      />
      
      <ExpenseSection
        data={data.expenses}
        onChange={handleExpenseChange}
        onValidate={handleValidation}
      />
      
      {data.vehicleExpense && (
        <VehicleExpenseCalculator
          data={data.vehicleExpense}
          onChange={handleVehicleExpenseChange}
          onValidate={handleValidation}
        />
      )}
      
      {data.homeOffice && (
        <HomeOfficeCalculator
          data={data.homeOffice}
          onChange={handleHomeOfficeChange}
          onValidate={handleValidation}
        />
      )}
    </div>
  );
};

export default ScheduleC;
