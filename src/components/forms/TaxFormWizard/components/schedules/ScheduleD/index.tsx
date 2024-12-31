import React, { useState, useEffect } from 'react';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';
import { DocumentCapture } from '../../../DocumentCapture';
import { ValidationFeedback } from '../../../ValidationFeedback';
import { FormValidationService } from 'api/services/form/form_validation_service';

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

export const ScheduleD: React.FC<Props> = ({
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
        'ScheduleD',
        'capital_gains',
        data
      );
      setValidationResults(validation);
    } catch (error) {
      console.error('Error validating Schedule D:', error);
    }
  };

  const handleTransactionChange = (
    type: 'shortTerm' | 'longTerm',
    index: number,
    field: keyof Transaction,
    value: string | number
  ) => {
    const updatedData = { ...data };
    updatedData[type].transactions[index][field] = value;

    // Recalculate gain/loss
    if (field === 'proceeds' || field === 'costBasis') {
      const transaction = updatedData[type].transactions[index];
      transaction.gainLoss = transaction.proceeds - transaction.costBasis;
    }

    // Update totals
    updatedData[type].totals = calculateTotals(updatedData[type].transactions);

    onUpdate(updatedData);
  };

  const calculateTotals = (transactions: Transaction[]) => {
    return transactions.reduce((totals, transaction) => ({
      proceeds: totals.proceeds + transaction.proceeds,
      costBasis: totals.costBasis + transaction.costBasis,
      gainLoss: totals.gainLoss + transaction.gainLoss
    }), { proceeds: 0, costBasis: 0, gainLoss: 0 });
  };

  const addTransaction = (type: 'shortTerm' | 'longTerm') => {
    const newTransaction: Transaction = {
      description: '',
      dateAcquired: '',
      dateSold: '',
      proceeds: 0,
      costBasis: 0,
      gainLoss: 0
    };

    const updatedData = {
      ...data,
      [type]: {
        ...data[type],
        transactions: [...data[type].transactions, newTransaction]
      }
    };

    onUpdate(updatedData);
  };

  return (
    <div style={formSectionStyles.container}>
      <h3>Schedule D - Capital Gains and Losses</h3>

      {/* Short-term Capital Gains Section */}
      <section style={formSectionStyles.section}>
        <h4>Part I - Short-term Capital Gains and Losses</h4>
        {data.shortTerm.transactions.map((transaction, index) => (
          <div key={index} style={formFieldStyles.group}>
            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Description</label>
                <input
                  type="text"
                  value={transaction.description}
                  onChange={(e) => handleTransactionChange('shortTerm', index, 'description', e.target.value)}
                  style={formFieldStyles.input}
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Date Acquired</label>
                <input
                  type="date"
                  value={transaction.dateAcquired}
                  onChange={(e) => handleTransactionChange('shortTerm', index, 'dateAcquired', e.target.value)}
                  style={formFieldStyles.input}
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Date Sold</label>
                <input
                  type="date"
                  value={transaction.dateSold}
                  onChange={(e) => handleTransactionChange('shortTerm', index, 'dateSold', e.target.value)}
                  style={formFieldStyles.input}
                />
              </div>
            </div>

            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Proceeds</label>
                <input
                  type="number"
                  value={transaction.proceeds}
                  onChange={(e) => handleTransactionChange('shortTerm', index, 'proceeds', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Cost Basis</label>
                <input
                  type="number"
                  value={transaction.costBasis}
                  onChange={(e) => handleTransactionChange('shortTerm', index, 'costBasis', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Gain/Loss</label>
                <input
                  type="number"
                  value={transaction.gainLoss}
                  disabled
                  style={{ ...formFieldStyles.input, backgroundColor: '#f0f0f0' }}
                />
              </div>
            </div>
          </div>
        ))}

        <button
          onClick={() => addTransaction('shortTerm')}
          style={formFieldStyles.button.secondary}
        >
          Add Short-term Transaction
        </button>

        <div style={formFieldStyles.total}>
          <label>Short-term Totals</label>
          <div>
            <span>Proceeds: ${data.shortTerm.totals.proceeds.toFixed(2)}</span>
            <span>Cost Basis: ${data.shortTerm.totals.costBasis.toFixed(2)}</span>
            <span>Gain/Loss: ${data.shortTerm.totals.gainLoss.toFixed(2)}</span>
          </div>
        </div>
      </section>

      {/* Long-term Capital Gains Section */}
      <section style={formSectionStyles.section}>
        <h4>Part II - Long-term Capital Gains and Losses</h4>
        {/* Similar structure as short-term section */}
        {/* ... Long-term transaction inputs ... */}
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

export default ScheduleD;
