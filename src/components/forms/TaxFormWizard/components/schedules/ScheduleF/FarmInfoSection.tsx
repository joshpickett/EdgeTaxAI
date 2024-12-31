import React from 'react';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';

interface FarmInfo {
  name: string;
  address: string;
  principalProduct: string;
  accountingMethod: 'Cash' | 'Accrual';
  employerID: string;
}

interface Props {
  data: FarmInfo;
  onChange: (data: FarmInfo) => void;
}

export const FarmInfoSection: React.FC<Props> = ({
  data,
  onChange
}) => {
  const handleChange = (field: keyof FarmInfo, value: string) => {
    onChange({
      ...data,
      [field]: value
    });
  };

  return (
    <section style={formSectionStyles.section}>
      <h4>Farm Information</h4>
      <div style={formFieldStyles.group}>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Farm Name</label>
            <input
              type="text"
              value={data.name}
              onChange={(e) => handleChange('name', e.target.value)}
              style={formFieldStyles.input}
              required
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Principal Product</label>
            <input
              type="text"
              value={data.principalProduct}
              onChange={(e) => handleChange('principalProduct', e.target.value)}
              style={formFieldStyles.input}
              required
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Farm Address</label>
            <input
              type="text"
              value={data.address}
              onChange={(e) => handleChange('address', e.target.value)}
              style={formFieldStyles.input}
              required
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Employer Identification Number (EIN)</label>
            <input
              type="text"
              value={data.employerID}
              onChange={(e) => handleChange('employerID', e.target.value)}
              style={formFieldStyles.input}
              pattern="\d{2}-\d{7}"
              placeholder="XX-XXXXXXX"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Accounting Method</label>
            <select
              value={data.accountingMethod}
              onChange={(e) => handleChange('accountingMethod', e.target.value as 'Cash' | 'Accrual')}
              style={formFieldStyles.select}
              required
            >
              <option value="Cash">Cash</option>
              <option value="Accrual">Accrual</option>
            </select>
          </div>
        </div>
      </div>
    </section>
  );
};
