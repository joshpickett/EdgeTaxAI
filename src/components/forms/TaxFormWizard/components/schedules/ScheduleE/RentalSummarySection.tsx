import React from 'react';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';

interface RentalSummary {
  totalRents: number;
  totalExpenses: number;
  netIncome: number;
  depreciation: number;
  propertyCount: number;
  totalDays: number;
}

interface Props {
  data: RentalSummary;
}

export const RentalSummarySection: React.FC<Props> = ({ data }) => {
  return (
    <section style={formSectionStyles.section}>
      <h4>Rental Income Summary</h4>
      <div style={formFieldStyles.group}>
        <div style={formFieldStyles.summaryRow}>
          <label>Total Rental Income</label>
          <span>${data.totalRents.toFixed(2)}</span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Total Expenses</label>
          <span>${data.totalExpenses.toFixed(2)}</span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Depreciation</label>
          <span>${data.depreciation.toFixed(2)}</span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Net Rental Income/Loss</label>
          <span style={{
            color: data.netIncome >= 0 ? '#2e7d32' : '#c62828',
            fontWeight: 'bold'
          }}>
            ${data.netIncome.toFixed(2)}
          </span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Total Properties</label>
          <span>{data.propertyCount}</span>
        </div>

        <div style={formFieldStyles.summaryRow}>
          <label>Total Rental Days</label>
          <span>{data.totalDays}</span>
        </div>
      </div>
    </section>
  );
};
