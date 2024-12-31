import React from 'react';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { FormIntegrationService } from 'api/services/integration/form_integration_service';
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

interface Props {
  transactions: Transaction[];
  type: 'shortTerm' | 'longTerm';
  onChange: (transactions: Transaction[]) => void;
}

export const TransactionSection: React.FC<Props> = ({
  transactions,
  type,
  onChange
}) => {
  const formValidationService = new FormValidationService();
  const formIntegrationService = new FormIntegrationService();

  const handleTransactionChange = async (index: number, field: keyof Transaction, value: any) => {
    try {
      const result = await formIntegrationService.calculateTransaction({
        transactions: transactions.map((t, i) => 
          i === index ? { ...t, [field]: value } : t
        ),
        type
      });
      
      onChange(result.transactions);
    } catch (error) {
      console.error('Error calculating transaction:', error);
    }
  };

  const addTransaction = () => {
    const newTransaction: Transaction = {
      description: '',
      dateAcquired: '',
      dateSold: '',
      proceeds: 0,
      costBasis: 0,
      gainLoss: 0
    };
    onChange([...transactions, newTransaction]);
  };

  return (
    <section style={formSectionStyles.section}>
      <h4>{type === 'shortTerm' ? 'Short-term' : 'Long-term'} Capital Gains and Losses</h4>
      {transactions.map((transaction, index) => (
        <div key={index} style={formFieldStyles.group}>
          <div style={formFieldStyles.row}>
            <div style={formFieldStyles.column}>
              <label style={formFieldStyles.label}>Description</label>
              <input
                type="text"
                value={transaction.description}
                onChange={(e) => handleTransactionChange(index, 'description', e.target.value)}
                style={formFieldStyles.input}
              />
            </div>
          </div>

          <div style={formFieldStyles.row}>
            <div style={formFieldStyles.column}>
              <label style={formFieldStyles.label}>Date Acquired</label>
              <input
                type="date"
                value={transaction.dateAcquired}
                onChange={(e) => handleTransactionChange(index, 'dateAcquired', e.target.value)}
                style={formFieldStyles.input}
              />
            </div>
            <div style={formFieldStyles.column}>
              <label style={formFieldStyles.label}>Date Sold</label>
              <input
                type="date"
                value={transaction.dateSold}
                onChange={(e) => handleTransactionChange(index, 'dateSold', e.target.value)}
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
                onChange={(e) => handleTransactionChange(index, 'proceeds', parseFloat(e.target.value))}
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
                onChange={(e) => handleTransactionChange(index, 'costBasis', parseFloat(e.target.value))}
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
        onClick={addTransaction}
        style={formFieldStyles.button.secondary}
      >
        Add Transaction
      </button>
    </section>
  );
};
