import React from 'react';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';
import { BusinessInfo, ValidationResult } from '../../../types/scheduleC.types';

interface Props {
  data: BusinessInfo;
  onChange: (data: BusinessInfo) => void;
  onValidate?: (result: ValidationResult) => void;
}

export const BusinessInfoSection: React.FC<Props> = ({
  data,
  onChange,
  onValidate
}) => {
  const handleChange = (field: keyof BusinessInfo, value: string) => {
    const updatedData = {
      ...data,
      [field]: value
    };
    
    onChange(updatedData);
    onValidate?.({ isValid: true, errors: [], warnings: [] });
  };

  return (
    <section style={formSectionStyles.section}>
      <h4>Business Information</h4>
      <div style={formFieldStyles.group}>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Business Name</label>
            <input
              type="text"
              value={data.name}
              onChange={(e) => handleChange('name', e.target.value)}
              style={formFieldStyles.input}
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>EIN</label>
            <input
              type="text"
              value={data.ein}
              onChange={(e) => handleChange('ein', e.target.value)}
              style={formFieldStyles.input}
              placeholder="XX-XXXXXXX"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Business Address</label>
            <input
              type="text"
              value={data.address}
              onChange={(e) => handleChange('address', e.target.value)}
              style={formFieldStyles.input}
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Business Type</label>
            <select
              value={data.businessType}
              onChange={(e) => handleChange('businessType', e.target.value)}
              style={formFieldStyles.select}
            >
              <option value="">Select Business Type</option>
              <option value="sole_proprietorship">Sole Proprietorship</option>
              <option value="single_member_llc">Single Member LLC</option>
              <option value="independent_contractor">Independent Contractor</option>
            </select>
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Start Date</label>
            <input
              type="date"
              value={data.startDate}
              onChange={(e) => handleChange('startDate', e.target.value)}
              style={formFieldStyles.input}
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Accounting Method</label>
            <select
              value={data.accountingMethod}
              onChange={(e) => handleChange('accountingMethod', e.target.value as 'cash' | 'accrual')}
              style={formFieldStyles.select}
            >
              <option value="cash">Cash</option>
              <option value="accrual">Accrual</option>
            </select>
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Business Code</label>
            <input
              type="text"
              value={data.businessCode}
              onChange={(e) => handleChange('businessCode', e.target.value)}
              style={formFieldStyles.input}
              placeholder="6-digit code"
            />
          </div>
        </div>
      </div>
    </section>
  );
};
