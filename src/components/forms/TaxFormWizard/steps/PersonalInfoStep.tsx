import React from 'react';
import { Form1040Data } from 'shared/types/form1040';
import { formFieldStyles } from '../styles/FormFieldStyles';
import { formSectionStyles } from '../styles/FormSectionStyles';

interface PersonalInfoStepProps {
  formData: Partial<Form1040Data>;
  onUpdate: (data: Partial<Form1040Data>) => void;
}

export const PersonalInfoStep: React.FC<PersonalInfoStepProps> = ({
  formData,
  onUpdate
}) => {
  const handleInputChange = (field: string, value: string) => {
    onUpdate({
      ...formData,
      taxpayerInfo: {
        ...formData.taxpayerInfo,
        [field]: value
      }
    });
  };

  const handleAddressChange = (field: string, value: string) => {
    onUpdate({
      ...formData,
      taxpayerInfo: {
        ...formData.taxpayerInfo,
        address: {
          ...formData.taxpayerInfo?.address,
          [field]: value
        }
      }
    });
  };

  return (
    <div style={formSectionStyles.container}>
      <section>
        <h3 style={formSectionStyles.title}>Taxpayer Information</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>First Name</label>
          <input
            type="text"
            value={formData.taxpayerInfo?.firstName || ''}
            onChange={(e) => handleInputChange('firstName', e.target.value)}
            style={formFieldStyles.input}
            required
          />
        </div>

        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Last Name</label>
          <input
            type="text"
            value={formData.taxpayerInfo?.lastName || ''}
            onChange={(e) => handleInputChange('lastName', e.target.value)}
            style={formFieldStyles.input}
            required
          />
        </div>

        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Social Security Number</label>
          <input
            type="text"
            value={formData.taxpayerInfo?.ssn || ''}
            onChange={(e) => handleInputChange('ssn', e.target.value)}
            style={formFieldStyles.input}
            required
            pattern="\d{3}-?\d{2}-?\d{4}"
            placeholder="XXX-XX-XXXX"
          />
        </div>
      </section>

      {formData.taxpayerInfo?.filingStatus === 'married_joint' && (
        <section style={formSectionStyles.container}>
          <h3 style={formSectionStyles.title}>Spouse Information</h3>
          <div style={formFieldStyles.container}>
            <label style={formFieldStyles.label}>Spouse First Name</label>
            <input
              type="text"
              value={formData.taxpayerInfo?.spouseFirstName || ''}
              onChange={(e) => handleInputChange('spouseFirstName', e.target.value)}
              style={formFieldStyles.input}
              required
            />
          </div>

          <div style={formFieldStyles.container}>
            <label style={formFieldStyles.label}>Spouse Last Name</label>
            <input
              type="text"
              value={formData.taxpayerInfo?.spouseLastName || ''}
              onChange={(e) => handleInputChange('spouseLastName', e.target.value)}
              style={formFieldStyles.input}
              required
            />
          </div>

          <div style={formFieldStyles.container}>
            <label style={formFieldStyles.label}>Spouse Social Security Number</label>
            <input
              type="text"
              value={formData.taxpayerInfo?.spouseSSN || ''}
              onChange={(e) => handleInputChange('spouseSSN', e.target.value)}
              style={formFieldStyles.input}
              required
              pattern="\d{3}-?\d{2}-?\d{4}"
              placeholder="XXX-XX-XXXX"
            />
          </div>
        </section>
      )}

      <section style={formSectionStyles.container}>
        <h3 style={formSectionStyles.title}>Address Information</h3>
        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>Street Address</label>
          <input
            type="text"
            value={formData.taxpayerInfo?.address?.street || ''}
            onChange={(e) => handleAddressChange('street', e.target.value)}
            style={formFieldStyles.input}
            required
          />
        </div>

        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>City</label>
          <input
            type="text"
            value={formData.taxpayerInfo?.address?.city || ''}
            onChange={(e) => handleAddressChange('city', e.target.value)}
            style={formFieldStyles.input}
            required
          />
        </div>

        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>State</label>
          <input
            type="text"
            value={formData.taxpayerInfo?.address?.state || ''}
            onChange={(e) => handleAddressChange('state', e.target.value)}
            style={formFieldStyles.input}
            required
            maxLength={2}
          />
        </div>

        <div style={formFieldStyles.container}>
          <label style={formFieldStyles.label}>ZIP Code</label>
          <input
            type="text"
            value={formData.taxpayerInfo?.address?.zipCode || ''}
            onChange={(e) => handleAddressChange('zipCode', e.target.value)}
            style={formFieldStyles.input}
            required
            pattern="\d{5}(-\d{4})?"
            placeholder="XXXXX"
          />
        </div>
      </section>
    </div>
  );
};
