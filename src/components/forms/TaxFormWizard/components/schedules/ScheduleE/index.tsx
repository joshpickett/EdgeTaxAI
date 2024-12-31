import React, { useState, useEffect } from 'react';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';
import { DocumentCapture } from '../../../DocumentCapture';
import { ValidationFeedback } from '../../../ValidationFeedback';
import { FormValidationService } from 'api/services/form/form_validation_service';

interface RentalProperty {
  address: string;
  propertyType: string;
  income: {
    rents: number;
    other: number;
  };
  expenses: {
    advertising: number;
    auto: number;
    cleaning: number;
    insurance: number;
    legal: number;
    repairs: number;
    supplies: number;
    taxes: number;
    utilities: number;
    other: number;
  };
  totalIncome: number;
  totalExpenses: number;
  netIncome: number;
}

interface ScheduleEData {
  properties: RentalProperty[];
  totalRentalIncome: number;
  totalRentalExpenses: number;
  netRentalIncome: number;
}

interface Props {
  data: ScheduleEData;
  onUpdate: (data: ScheduleEData) => void;
}

const formValidationService = new FormValidationService();

export const ScheduleE: React.FC<Props> = ({
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
        'ScheduleE',
        'rental_income',
        data
      );
      setValidationResults(validation);
    } catch (error) {
      console.error('Error validating Schedule E:', error);
    }
  };

  const handlePropertyChange = (index: number, field: string, value: any) => {
    const updatedData = { ...data };
    const property = updatedData.properties[index];

    // Update nested property value
    if (field.includes('.')) {
      const [category, subfield] = field.split('.');
      property[category][subfield] = value;
    } else {
      property[field] = value;
    }

    // Recalculate totals
    property.totalIncome = property.income.rents + property.income.other;
    property.totalExpenses = Object.values(property.expenses).reduce((sum, val) => sum + val, 0);
    property.netIncome = property.totalIncome - property.totalExpenses;

    // Update overall totals
    updateTotals(updatedData);

    onUpdate(updatedData);
  };

  const updateTotals = (data: ScheduleEData) => {
    data.totalRentalIncome = data.properties.reduce((sum, prop) => sum + prop.totalIncome, 0);
    data.totalRentalExpenses = data.properties.reduce((sum, prop) => sum + prop.totalExpenses, 0);
    data.netRentalIncome = data.totalRentalIncome - data.totalRentalExpenses;
  };

  const addProperty = () => {
    const newProperty: RentalProperty = {
      address: '',
      propertyType: '',
      income: {
        rents: 0,
        other: 0
      },
      expenses: {
        advertising: 0,
        auto: 0,
        cleaning: 0,
        insurance: 0,
        legal: 0,
        repairs: 0,
        supplies: 0,
        taxes: 0,
        utilities: 0,
        other: 0
      },
      totalIncome: 0,
      totalExpenses: 0,
      netIncome: 0
    };

    const updatedData = {
      ...data,
      properties: [...data.properties, newProperty]
    };

    onUpdate(updatedData);
  };

  return (
    <div style={formSectionStyles.container}>
      <h3>Schedule E - Supplemental Income and Loss</h3>

      {data.properties.map((property, index) => (
        <section key={index} style={formSectionStyles.section}>
          <h4>Rental Property {index + 1}</h4>
          
          <div style={formFieldStyles.group}>
            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Property Address</label>
                <input
                  type="text"
                  value={property.address}
                  onChange={(e) => handlePropertyChange(index, 'address', e.target.value)}
                  style={formFieldStyles.input}
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Property Type</label>
                <select
                  value={property.propertyType}
                  onChange={(e) => handlePropertyChange(index, 'propertyType', e.target.value)}
                  style={formFieldStyles.select}
                >
                  <option value="">Select Type</option>
                  <option value="single_family">Single Family</option>
                  <option value="multi_family">Multi Family</option>
                  <option value="commercial">Commercial</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <h5>Income</h5>
            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Rents Received</label>
                <input
                  type="number"
                  value={property.income.rents}
                  onChange={(e) => handlePropertyChange(index, 'income.rents', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Other Income</label>
                <input
                  type="number"
                  value={property.income.other}
                  onChange={(e) => handlePropertyChange(index, 'income.other', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
            </div>

            <h5>Expenses</h5>
            {Object.entries(property.expenses).map(([key, value]) => (
              <div key={key} style={formFieldStyles.row}>
                <div style={formFieldStyles.column}>
                  <label style={formFieldStyles.label}>{key.charAt(0).toUpperCase() + key.slice(1)}</label>
                  <input
                    type="number"
                    value={value}
                    onChange={(e) => handlePropertyChange(index, `expenses.${key}`, parseFloat(e.target.value))}
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
                <span>${property.totalIncome.toFixed(2)}</span>
              </div>
              <div style={formFieldStyles.total}>
                <label>Total Expenses</label>
                <span>${property.totalExpenses.toFixed(2)}</span>
              </div>
              <div style={formFieldStyles.total}>
                <label>Net Income/Loss</label>
                <span style={{
                  color: property.netIncome >= 0 ? '#2e7d32' : '#c62828'
                }}>
                  ${property.netIncome.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </section>
      ))}

      <button
        onClick={addProperty}
        style={formFieldStyles.button.secondary}
      >
        Add Property
      </button>

      <section style={formSectionStyles.section}>
        <h4>Schedule E Summary</h4>
        <div style={formFieldStyles.totals}>
          <div style={formFieldStyles.total}>
            <label>Total Rental Income</label>
            <span>${data.totalRentalIncome.toFixed(2)}</span>
          </div>
          <div style={formFieldStyles.total}>
            <label>Total Rental Expenses</label>
            <span>${data.totalRentalExpenses.toFixed(2)}</span>
          </div>
          <div style={formFieldStyles.total}>
            <label>Net Rental Income/Loss</label>
            <span style={{
              color: data.netRentalIncome >= 0 ? '#2e7d32' : '#c62828'
            }}>
              ${data.netRentalIncome.toFixed(2)}
            </span>
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

export default ScheduleE;
