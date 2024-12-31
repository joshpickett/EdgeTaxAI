import React, { useState, useCallback, useEffect } from 'react';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { FormIntegrationService } from 'api/services/integration/form_integration_service';
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

  const formValidationService = new FormValidationService();
  const formIntegrationService = new FormIntegrationService();

  useEffect(() => {
    const calculateAndValidate = async () => {
      try {
        // Use backend calculation service
        const calculationResult = await formIntegrationService.calculateScheduleTotals(
          'ScheduleC',
          data
        );
        
        // Use backend validation service
        const validation = await formValidationService.validate_section(
          'ScheduleC',
          'complete',
          data
        );
        
        setValidationResult(validation);
        onValidate?.(validation);
        onCalculate?.(calculationResult);
      } catch (error) {
        console.error('Error in Schedule C calculations:', error);
      }
    };
    
    calculateAndValidate();
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
