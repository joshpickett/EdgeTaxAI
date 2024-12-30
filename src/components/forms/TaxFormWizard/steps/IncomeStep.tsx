import React, { useState, useEffect } from 'react';
import { Form1040Data } from 'shared/types/form1040';
import { formFieldStyles } from '../styles/FormFieldStyles';
import { formSectionStyles } from '../styles/FormSectionStyles';
import { platformService } from 'shared/services/platformService';

interface IncomeStepProps {
  formData: Partial<Form1040Data>;
  onUpdate: (data: Partial<Form1040Data>) => void;
}

export const IncomeStep: React.FC<IncomeStepProps> = ({
  formData,
  onUpdate
}) => {
  const [platformIncome, setPlatformIncome] = useState<any>(null);
  const [showW2Section, setShowW2Section] = useState(false);
  const [show1099Section, setShow1099Section] = useState(false);

  useEffect(() => {
    const fetchPlatformIncome = async () => {
      if (formData.includePlatformData) {
        try {
          const income = await platformService.getPlatformIncome();
          setPlatformIncome(income);
        } catch (error) {
          console.error('Error fetching platform income:', error);
        }
      }
    };

    fetchPlatformIncome();
  }, [formData.includePlatformData]);

  const handleIncomeChange = (field: string, value: string) => {
    onUpdate({
      ...formData,
      income: {
        ...formData.income,
        [field]: parseFloat(value) || 0
      }
    });
  };

  const calculateTotalIncome = () => {
    const income = formData.income || {};
    return Object.values(income).reduce((sum, val) => sum + (val || 0), 0);
  };

  return (
    <div style={formSectionStyles.container}>
      <section>
        <h3 style={formSectionStyles.title}>Income Sources</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.checkbox.container}>
            <input
              type="checkbox"
              checked={showW2Section}
              onChange={(e) => setShowW2Section(e.target.checked)}
              style={formFieldStyles.checkbox.input}
            />
            I have W-2 income from an employer
          </label>

          <label style={formFieldStyles.checkbox.container}>
            <input
              type="checkbox"
              checked={show1099Section}
              onChange={(e) => setShow1099Section(e.target.checked)}
              style={formFieldStyles.checkbox.input}
            />
            I have 1099 income
          </label>
        </div>
      </section>

      {showW2Section && (
        <section style={formSectionStyles.container}>
          <h3 style={formSectionStyles.title}>W-2 Income</h3>
          <div style={formFieldStyles.container}>
            <label style={formFieldStyles.label}>Wages (Box 1)</label>
            <input
              type="number"
              value={formData.income?.wages || ''}
              onChange={(e) => handleIncomeChange('wages', e.target.value)}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </section>
      )}

      {show1099Section && (
        <section style={formSectionStyles.container}>
          <h3 style={formSectionStyles.title}>1099 Income</h3>
          
          {platformIncome && (
            <div style={formSectionStyles.helpText}>
              <p>We found the following income from your connected platforms:</p>
              {Object.entries(platformIncome).map(([platform, amount]) => (
                <div key={platform} style={formFieldStyles.container}>
                  <label style={formFieldStyles.label}>{platform}</label>
                  <input
                    type="number"
                    value={amount}
                    onChange={(e) => handleIncomeChange(`platform_${platform}`, e.target.value)}
                    style={formFieldStyles.input}
                    min="0"
                    step="0.01"
                  />
                </div>
              ))}
            </div>
          )}

          <div style={formFieldStyles.container}>
            <label style={formFieldStyles.label}>Other 1099-NEC Income</label>
            <input
              type="number"
              value={formData.income?.business || ''}
              onChange={(e) => handleIncomeChange('business', e.target.value)}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </section>
      )}

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Additional Income</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Interest Income</label>
          <input
            type="number"
            value={formData.income?.interest || ''}
            onChange={(e) => handleIncomeChange('interest', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>

        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Dividend Income</label>
          <input
            type="number"
            value={formData.income?.dividends || ''}
            onChange={(e) => handleIncomeChange('dividends', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>

        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Other Income</label>
          <input
            type="number"
            value={formData.income?.otherIncome || ''}
            onChange={(e) => handleIncomeChange('otherIncome', e.target.value)}
            style={formFieldStyles.input}
            min="0"
            step="0.01"
          />
        </div>
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Total Income</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Total Income for {new Date().getFullYear()}</label>
          <input
            type="number"
            value={calculateTotalIncome()}
            style={{ ...formFieldStyles.input, backgroundColor: '#f0f0f0' }}
            disabled
          />
        </div>
      </section>
    </div>
  );
};
