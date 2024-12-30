import React, { useEffect, useState } from 'react';
import { Form1040Data } from 'shared/types/form1040';
import { FilingStatus } from 'shared/types/tax';
import { expenseService } from 'shared/services/expenseService';
import { platformService } from 'shared/services/platformService';
import { formFieldStyles } from '../styles/FormFieldStyles';
import { formSectionStyles } from '../styles/FormSectionStyles';
import { DependentsList } from '../components/DependentsList';

const FILING_STATUS_INFO = {
  single: {
    title: 'Single',
    description: 'Choose this if you are unmarried, divorced, or legally separated.'
  },
  married_joint: {
    title: 'Married Filing Jointly',
    description: 'For married couples who want to file together. Usually provides the most tax benefits.'
  },
  // ...more status definitions
};

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

  const handleDependentChange = (hasDependents: boolean) => {
    onUpdate({
      ...formData,
      hasDependents
    });
  };

  const handleDependentsUpdate = (dependents: any) => {
    onUpdate({
      ...formData,
      dependents
    });
  };

  const handleIncomeSourceChange = (id: string, checked: boolean) => {
    onUpdate({
      ...formData,
      incomeSources: {
        ...formData.incomeSources,
        [id]: checked
      }
    });
  };

  return (
    <div style={formSectionStyles.container}>
      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Filing Status</h3>
        {Object.entries(FILING_STATUS_INFO).map(([status, info]) => (
          <div key={status} style={formFieldStyles.radioGroup}>
            <label style={formFieldStyles.radio.container}>
              <input
                type="radio"
                name="filingStatus"
                value={status}
                checked={formData.taxpayerInfo?.filingStatus === status}
                onChange={() => handleFilingStatusChange(status)}
                style={formFieldStyles.radio.input}
              />
              <div style={formFieldStyles.radio.label}>
                <h4>{info.title}</h4>
                <p>{info.description}</p>
              </div>
            </label>
          </div>
        ))}
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Dependents</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.checkbox.container}>
            <input
              type="checkbox"
              checked={formData.hasDependents}
              onChange={(e) => handleDependentChange(e.target.checked)}
              style={formFieldStyles.checkbox.input}
            />
            Do you have any dependents?
          </label>
        </div>
        {formData.hasDependents && (
          <DependentsList
            dependents={formData.dependents || []}
            onUpdate={handleDependentsUpdate}
          />
        )}
      </section>

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Income Sources</h3>
        <div style={formFieldStyles.container}>
          {INCOME_SOURCES.map(source => (
            <label key={source.id} style={formFieldStyles.checkbox.container}>
              <input
                type="checkbox"
                checked={formData.incomeSources?.[source.id] || false}
                onChange={(e) => handleIncomeSourceChange(source.id, e.target.checked)}
                style={formFieldStyles.checkbox.input}
              />
              {source.label}
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
