import React from 'react';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';
import { ScheduleCTotals } from '../../../types/scheduleC.types';

interface Props {
  totals: ScheduleCTotals;
}

export const SummarySection: React.FC<Props> = ({ totals }) => {
  return (
    <section style={formSectionStyles.section}>
      <h4>Schedule C Summary</h4>
      <div style={formFieldStyles.group}>
        <div style={formFieldStyles.summaryRow}>
          <label>Gross Income</label>
          <span>${totals.grossIncome.toFixed(2)}</span>
        </div>
        
        <div style={formFieldStyles.summaryRow}>
          <label>Total Expenses</label>
          <span>${totals.totalExpenses.toFixed(2)}</span>
        </div>
        
        {totals.vehicleExpenses > 0 && (
          <div style={formFieldStyles.summaryRow}>
            <label>Vehicle Expenses</label>
            <span>${totals.vehicleExpenses.toFixed(2)}</span>
          </div>
        )}
        
        {totals.homeOfficeDeduction > 0 && (
          <div style={formFieldStyles.summaryRow}>
            <label>Home Office Deduction</label>
            <span>${totals.homeOfficeDeduction.toFixed(2)}</span>
          </div>
        )}
        
        <div style={formFieldStyles.summaryRow}>
          <label>Net Profit/Loss</label>
          <span style={{
            color: totals.netProfit >= 0 ? '#2e7d32' : '#c62828',
            fontWeight: 'bold'
          }}>
            ${totals.netProfit.toFixed(2)}
          </span>
        </div>
        
        <div style={formFieldStyles.summaryRow}>
          <label>Self-Employment Tax</label>
          <span>${totals.selfEmploymentTax.toFixed(2)}</span>
        </div>
      </div>
    </section>
  );
};
