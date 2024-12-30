import React, { useState, useEffect } from 'react';
import { formFieldStyles } from '../../styles/FormFieldStyles';
import { formSectionStyles } from '../../styles/FormSectionStyles';
import { DocumentCapture } from '../DocumentCapture';
import { ValidationFeedback } from '../ValidationFeedback';
import { FormValidationService } from 'api/services/form/form_validation_service';

interface InterestPayerData {
  name: string;
  amount: number;
  foreignAccount?: boolean;
  foreignCountry?: string;
}

interface DividendPayerData {
  name: string;
  ordinaryDividends: number;
  qualifiedDividends: number;
  foreignTax?: number;
}

interface ScheduleBData {
  interest: {
    payers: InterestPayerData[];
    totalInterest: number;
    hasForeignAccounts: boolean;
    foreignAccountsDetails?: {
      countries: string[];
      maxValue: number;
    };
  };
  dividends: {
    payers: DividendPayerData[];
    totalOrdinaryDividends: number;
    totalQualifiedDividends: number;
    totalForeignTax: number;
  };
}

interface ScheduleBProps {
  data: ScheduleBData;
  onUpdate: (data: ScheduleBData) => void;
}

const formValidationService = new FormValidationService();

export const ScheduleB: React.FC<ScheduleBProps> = ({
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
        'ScheduleB',
        'interest_and_dividends',
        data
      );
      setValidationResults(validation);
    } catch (error) {
      console.error('Error validating Schedule B:', error);
    }
  };

  const handleAddInterestPayer = () => {
    const newPayer: InterestPayerData = {
      name: '',
      amount: 0,
      foreignAccount: false
    };
    
    onUpdate({
      ...data,
      interest: {
        ...data.interest,
        payers: [...data.interest.payers, newPayer]
      }
    });
  };

  const handleAddDividendPayer = () => {
    const newPayer: DividendPayerData = {
      name: '',
      ordinaryDividends: 0,
      qualifiedDividends: 0,
      foreignTax: 0
    };
    
    onUpdate({
      ...data,
      dividends: {
        ...data.dividends,
        payers: [...data.dividends.payers, newPayer]
      }
    });
  };

  const handleInterestPayerChange = (index: number, field: keyof InterestPayerData, value: any) => {
    const updatedPayers = [...data.interest.payers];
    updatedPayers[index] = {
      ...updatedPayers[index],
      [field]: value
    };

    const totalInterest = updatedPayers.reduce((sum, payer) => sum + payer.amount, 0);

    onUpdate({
      ...data,
      interest: {
        ...data.interest,
        payers: updatedPayers,
        totalInterest
      }
    });
  };

  const handleDividendPayerChange = (index: number, field: keyof DividendPayerData, value: any) => {
    const updatedPayers = [...data.dividends.payers];
    updatedPayers[index] = {
      ...updatedPayers[index],
      [field]: value
    };

    const totalOrdinaryDividends = updatedPayers.reduce((sum, payer) => sum + payer.ordinaryDividends, 0);
    const totalQualifiedDividends = updatedPayers.reduce((sum, payer) => sum + payer.qualifiedDividends, 0);
    const totalForeignTax = updatedPayers.reduce((sum, payer) => sum + (payer.foreignTax || 0), 0);

    onUpdate({
      ...data,
      dividends: {
        ...data.dividends,
        payers: updatedPayers,
        totalOrdinaryDividends,
        totalQualifiedDividends,
        totalForeignTax
      }
    });
  };

  return (
    <div style={formSectionStyles.container}>
      <h3>Schedule B - Interest and Dividends</h3>

      <section style={formSectionStyles.section}>
        <h4>Part I - Interest</h4>
        {data.interest.payers.map((payer, index) => (
          <div key={index} style={formFieldStyles.group}>
            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Payer Name</label>
                <input
                  type="text"
                  value={payer.name}
                  onChange={(e) => handleInterestPayerChange(index, 'name', e.target.value)}
                  style={formFieldStyles.input}
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Amount</label>
                <input
                  type="number"
                  value={payer.amount}
                  onChange={(e) => handleInterestPayerChange(index, 'amount', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
            </div>

            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.checkbox.container}>
                  <input
                    type="checkbox"
                    checked={payer.foreignAccount}
                    onChange={(e) => handleInterestPayerChange(index, 'foreignAccount', e.target.checked)}
                    style={formFieldStyles.checkbox.input}
                  />
                  Foreign Account
                </label>
              </div>
              {payer.foreignAccount && (
                <div style={formFieldStyles.column}>
                  <label style={formFieldStyles.label}>Foreign Country</label>
                  <input
                    type="text"
                    value={payer.foreignCountry}
                    onChange={(e) => handleInterestPayerChange(index, 'foreignCountry', e.target.value)}
                    style={formFieldStyles.input}
                  />
                </div>
              )}
            </div>
          </div>
        ))}

        <button
          onClick={handleAddInterestPayer}
          style={formFieldStyles.button.secondary}
        >
          Add Interest Payer
        </button>

        <div style={formFieldStyles.total}>
          <label>Total Interest</label>
          <span>{data.interest.totalInterest.toFixed(2)}</span>
        </div>
      </section>

      <section style={formSectionStyles.section}>
        <h4>Part II - Dividends</h4>
        {data.dividends.payers.map((payer, index) => (
          <div key={index} style={formFieldStyles.group}>
            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Payer Name</label>
                <input
                  type="text"
                  value={payer.name}
                  onChange={(e) => handleDividendPayerChange(index, 'name', e.target.value)}
                  style={formFieldStyles.input}
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Ordinary Dividends</label>
                <input
                  type="number"
                  value={payer.ordinaryDividends}
                  onChange={(e) => handleDividendPayerChange(index, 'ordinaryDividends', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Qualified Dividends</label>
                <input
                  type="number"
                  value={payer.qualifiedDividends}
                  onChange={(e) => handleDividendPayerChange(index, 'qualifiedDividends', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
            </div>

            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Foreign Tax Paid</label>
                <input
                  type="number"
                  value={payer.foreignTax}
                  onChange={(e) => handleDividendPayerChange(index, 'foreignTax', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
            </div>
          </div>
        ))}

        <button
          onClick={handleAddDividendPayer}
          style={formFieldStyles.button.secondary}
        >
          Add Dividend Payer
        </button>

        <div style={formFieldStyles.totals}>
          <div style={formFieldStyles.total}>
            <label>Total Ordinary Dividends</label>
            <span>{data.dividends.totalOrdinaryDividends.toFixed(2)}</span>
          </div>
          <div style={formFieldStyles.total}>
            <label>Total Qualified Dividends</label>
            <span>{data.dividends.totalQualifiedDividends.toFixed(2)}</span>
          </div>
          <div style={formFieldStyles.total}>
            <label>Total Foreign Tax Paid</label>
            <span>{data.dividends.totalForeignTax.toFixed(2)}</span>
          </div>
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
