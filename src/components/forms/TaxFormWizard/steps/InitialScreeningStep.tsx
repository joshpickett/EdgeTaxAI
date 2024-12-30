import React, { useEffect, useState } from 'react';
import { Form1040Data } from 'shared/types/form1040';
import { expenseService } from 'shared/services/expenseService';
import { platformService } from 'shared/services/platformService';
import { formFieldStyles } from '../styles/FormFieldStyles';
import { formSectionStyles } from '../styles/FormSectionStyles';

interface InitialScreeningStepProps {
  formData: Partial<Form1040Data>;
  onUpdate: (data: Partial<Form1040Data>) => void;
}

export const InitialScreeningStep: React.FC<InitialScreeningStepProps> = ({
  formData,
  onUpdate
}) => {
  const [platformData, setPlatformData] = useState<any>(null);
  const [expenseData, setExpenseData] = useState<any>(null);

  useEffect(() => {
    const fetchExistingData = async () => {
      try {
        const platforms = await platformService.getConnectedPlatforms();
        const expenses = await expenseService.getExpenses();
        setPlatformData(platforms);
        setExpenseData(expenses);
      } catch (error) {
        console.error('Error fetching existing data:', error);
      }
    };

    fetchExistingData();
  }, []);

  const handleFilingStatusChange = (status: string) => {
    onUpdate({
      ...formData,
      taxpayerInfo: {
        ...formData.taxpayerInfo,
        filingStatus: status
      }
    });
  };

  return (
    <div style={formSectionStyles.container}>
      <section>
        <h3 style={formSectionStyles.title}>Filing Status</h3>
        <div style={formFieldStyles.container}>
          {['single', 'married_joint', 'married_separate', 'head_of_household'].map(status => (
            <label key={status} style={formFieldStyles.checkbox.container}>
              <input
                type="radio"
                name="filingStatus"
                value={status}
                checked={formData.taxpayerInfo?.filingStatus === status}
                onChange={() => handleFilingStatusChange(status)}
                style={formFieldStyles.checkbox.input}
              />
              {status.replace(/_/g, ' ').toUpperCase()}
            </label>
          ))}
        </div>
      </section>

      {platformData && platformData.length > 0 && (
        <section style={formSectionStyles.container}>
          <h3 style={formSectionStyles.title}>Connected Platforms</h3>
          <p style={formSectionStyles.description}>
            We found the following gig platforms connected to your account:
          </p>
          {platformData.map(platform => (
            <div key={platform.id} style={formFieldStyles.checkbox.container}>
              <input
                type="checkbox"
                checked={formData.includePlatformData?.[platform.id]}
                onChange={(e) => onUpdate({
                  ...formData,
                  includePlatformData: {
                    ...formData.includePlatformData,
                    [platform.id]: e.target.checked
                  }
                })}
                style={formFieldStyles.checkbox.input}
              />
              {platform.name} - Include this income data?
            </div>
          ))}
        </section>
      )}

      {expenseData && expenseData.length > 0 && (
        <section style={formSectionStyles.container}>
          <h3 style={formSectionStyles.title}>Tracked Expenses</h3>
          <p style={formSectionStyles.description}>
            We found tracked expenses for this tax year. Would you like to include them?
          </p>
          <label style={formFieldStyles.checkbox.container}>
            <input
              type="checkbox"
              checked={formData.includeTrackedExpenses}
              onChange={(e) => onUpdate({
                ...formData,
                includeTrackedExpenses: e.target.checked
              })}
              style={formFieldStyles.checkbox.input}
            />
            Include tracked expenses
          </label>
        </section>
      )}
    </div>
  );
};
