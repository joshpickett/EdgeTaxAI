import React, { useState, useEffect } from 'react';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { FormIntegrationService } from 'api/services/integration/form_integration_service';
import { TransactionSection } from './TransactionSection';
import { GainLossCalculator } from './GainLossCalculator';
import { DocumentCapture } from '../../../DocumentCapture';
import { ValidationFeedback } from '../../../ValidationFeedback';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';

interface Transaction {
  description: string;
  dateAcquired: string;
  dateSold: string;
  proceeds: number;
  costBasis: number;
  gainLoss: number;
}

interface ScheduleDData {
  shortTerm: {
    transactions: Transaction[];
    totals: {
      proceeds: number;
      costBasis: number;
      gainLoss: number;
    };
  };
  longTerm: {
    transactions: Transaction[];
    totals: {
      proceeds: number;
      costBasis: number;
      gainLoss: number;
    };
  };
}

interface Props {
  data: ScheduleDData;
  onUpdate: (data: ScheduleDData) => void;
}

const formValidationService = new FormValidationService();
const formIntegrationService = new FormIntegrationService();

export const ScheduleD: React.FC<Props> = ({
  data,
  onUpdate
}) => {
  const [validationResults, setValidationResults] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const validateAndCalculate = async () => {
      try {
        const validation = await formValidationService.validate_section(
          'ScheduleD',
          'capital_gains',
          data
        );
        setValidationResults(validation);

        const calculationResult = await formIntegrationService.calculateCapitalGains(data);
        onUpdate({
          ...data,
          ...calculationResult
        });
      } catch (error) {
        console.error('Error validating Schedule D:', error);
      }
    };
    validateAndCalculate();
  }, [data]);

  const handleTransactionChange = async (
    type: 'shortTerm' | 'longTerm',
    transactions: Transaction[]
  ) => {
    try {
      const result = await formIntegrationService.calculateCapitalGains({
        ...data,
        [type]: {
          ...data[type],
          transactions
        }
      });
      
      onUpdate(result);
    } catch (error) {
      console.error('Error calculating capital gains:', error);
    }
  };

  return (
    <div style={formSectionStyles.container}>
      <h3>Schedule D - Capital Gains and Losses</h3>

      <TransactionSection
        transactions={data.shortTerm.transactions}
        type="shortTerm"
        onChange={(transactions) => handleTransactionChange('shortTerm', transactions)}
      />

      <TransactionSection
        transactions={data.longTerm.transactions}
        type="longTerm"
        onChange={(transactions) => handleTransactionChange('longTerm', transactions)}
      />

      <GainLossCalculator
        shortTermTotals={data.shortTerm.totals}
        longTermTotals={data.longTerm.totals}
      />

      <DocumentCapture
        onCapture={async (file) => {
          setIsProcessing(true);
          try {
            // Handle document upload
            const result = await formIntegrationService.processDocument(file, 'ScheduleD');
            onUpdate({
              ...data,
              ...result
            });
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

export default ScheduleD;
