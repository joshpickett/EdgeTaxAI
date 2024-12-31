import React from 'react';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { FormIntegrationService } from 'api/services/integration/form_integration_service';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';

interface Totals {
  proceeds: number;
  costBasis: number;
  gainLoss: number;
}

interface Props {
  shortTermTotals: Totals;
  longTermTotals: Totals;
}

export const GainLossCalculator: React.FC<Props> = ({
  shortTermTotals,
  longTermTotals
}) => {
  const formValidationService = new FormValidationService();
  const formIntegrationService = new FormIntegrationService();

  const calculateNetGainLoss = async () => {
    try {
      const result = await formIntegrationService.calculateNetGainLoss({
        shortTermTotals,
        longTermTotals
      });
      return result.netGainLoss;
    } catch (error) {
      console.error('Error calculating net gain/loss:', error);
      return 0;
    }
  };

  return (
    <section style={formSectionStyles.section}>
      <h4>Summary of Capital Gains and Losses</h4>
      
      <div style={formFieldStyles.group}>
        <h5>Short-term Totals</h5>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Total Proceeds</label>
            <input
              type="number"
              value={shortTermTotals.proceeds}
              disabled
              style={{ ...formFieldStyles.input, backgroundColor: '#f0f0f0' }}
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Total Cost Basis</label>
            <input
              type="number"
              value={shortTermTotals.costBasis}
              disabled
              style={{ ...formFieldStyles.input, backgroundColor: '#f0f0f0' }}
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Net Short-term Gain/Loss</label>
            <input
              type="number"
              value={shortTermTotals.gainLoss}
              disabled
              style={{ 
                ...formFieldStyles.input, 
                backgroundColor: '#f0f0f0',
                color: shortTermTotals.gainLoss >= 0 ? 'green' : 'red'
              }}
            />
          </div>
        </div>

        <h5>Long-term Totals</h5>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Total Proceeds</label>
            <input
              type="number"
              value={longTermTotals.proceeds}
              disabled
              style={{ ...formFieldStyles.input, backgroundColor: '#f0f0f0' }}
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Total Cost Basis</label>
            <input
              type="number"
              value={longTermTotals.costBasis}
              disabled
              style={{ ...formFieldStyles.input, backgroundColor: '#f0f0f0' }}
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Net Long-term Gain/Loss</label>
            <input
              type="number"
              value={longTermTotals.gainLoss}
              disabled
              style={{ 
                ...formFieldStyles.input, 
                backgroundColor: '#f0f0f0',
                color: longTermTotals.gainLoss >= 0 ? 'green' : 'red'
              }}
            />
          </div>
        </div>

        <div style={formFieldStyles.total}>
          <label>Total Net Gain/Loss</label>
          <span style={{
            color: await calculateNetGainLoss() >= 0 ? 'green' : 'red',
            fontWeight: 'bold'
          }}>
            ${await calculateNetGainLoss().toFixed(2)}
          </span>
        </div>
      </div>
    </section>
  );
};
