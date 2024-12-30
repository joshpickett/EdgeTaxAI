import React, { useState, useEffect } from 'react';
import { Form1040Data } from 'shared/types/form1040';
import { W2Form } from '../components/W2Form';
import { Form1099Section } from '../components/Form1099Section';
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
  const [w2Forms, setW2Forms] = useState([]);
  const [form1099s, setForm1099s] = useState([]);

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

  const handleAddW2 = () => {
    const newW2 = {
      id: `w2_${Date.now()}`,
      employerName: '',
      employerEIN: '',
      employerAddress: {
        street: '',
        city: '',
        state: '',
        zipCode: ''
      },
      wages: 0,
      federalTaxWithheld: 0,
      socialSecurityWages: 0,
      socialSecurityTax: 0,
      medicareWages: 0,
      medicareTax: 0
    };
    setW2Forms([...w2Forms, newW2]);
  };

  const handleAddForm1099 = () => {
    const new1099 = {
      id: `1099_${Date.now()}`,
      type: '1099-NEC',
      payerName: '',
      payerTIN: '',
      amount: 0,
      federalTaxWithheld: 0,
      stateTaxWithheld: 0
    };
    setForm1099s([...form1099s, new1099]);
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
          {w2Forms.map((w2, index) => (
            <W2Form
              key={w2.id}
              w2Data={w2}
              onUpdate={(updatedW2) => {
                const updatedForms = [...w2Forms];
                updatedForms[index] = updatedW2;
                setW2Forms(updatedForms);
                handleIncomeChange('wages', updatedForms.reduce((sum, form) => sum + form.wages, 0));
              }}
              onRemove={() => {
                const updatedForms = w2Forms.filter(form => form.id !== w2.id);
                setW2Forms(updatedForms);
                handleIncomeChange('wages', updatedForms.reduce((sum, form) => sum + form.wages, 0));
              }}
            />
          ))}
          <button
            onClick={handleAddW2}
            style={formFieldStyles.button.primary}
          >
            Add Another W-2
          </button>
        </section>
      )}

      {show1099Section && (
        <section style={formSectionStyles.container}>
          <h3 style={formSectionStyles.title}>1099 Income</h3>
          {form1099s.map((form1099, index) => (
            <Form1099Section
              key={form1099.id}
              form1099Data={form1099}
              onUpdate={(updated1099) => {
                const updatedForms = [...form1099s];
                updatedForms[index] = updated1099;
                setForm1099s(updatedForms);
                handleIncomeChange('business', updatedForms.reduce((sum, form) => sum + form.amount, 0));
              }}
              onRemove={() => {
                const updatedForms = form1099s.filter(form => form.id !== form1099.id);
                setForm1099s(updatedForms);
                handleIncomeChange('business', updatedForms.reduce((sum, form) => sum + form.amount, 0));
              }}
            />
          ))}
          <button
            onClick={handleAddForm1099}
            style={formFieldStyles.button.primary}
          >
            Add Another 1099
          </button>
          
          {platformIncome && (
            <div style={formSectionStyles.helpText}>
              <p>We found the following income from your connected platforms:</p>
              {Object.entries(platformIncome).map(([platform, amount]) => {
                const existing1099 = form1099s.find(f => f.platform === platform);
                if (!existing1099) {
                  return (
                    <div key={platform} style={formFieldStyles.container}>
                      <p>{platform}: {amount}</p>
                      <button
                        onClick={() => handleAddForm1099({
                          type: '1099-K',
                          platform,
                          amount,
                          payerName: platform,
                          payerTIN: '',
                          federalTaxWithheld: 0,
                          stateTaxWithheld: 0
                        })}
                        style={formFieldStyles.button.secondary}
                      >
                        Create 1099-K
                      </button>
                    </div>
                  );
                }
                return null;
              })}
            </div>
          )}
        </section>
      )}

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
