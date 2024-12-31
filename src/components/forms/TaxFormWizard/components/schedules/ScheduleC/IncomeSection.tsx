import React from 'react';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';
import { IncomeData, ValidationResult } from '../../../types/scheduleC.types';

interface Props {
  data: IncomeData;
  onChange: (data: IncomeData) => void;
  onValidate?: (result: ValidationResult) => void;
}

export const IncomeSection: React.FC<Props> = ({
  data,
  onChange,
  onValidate
}) => {
  const handleChange = (field: keyof IncomeData, value: number) => {
    const updatedData = {
      ...data,
      [field]: value
    };
    
    onChange(updatedData);
    onValidate?.({
      isValid: true,
      errors: [],
      warnings: []
    });
  };

  const handleCostOfGoodsChange = (field: keyof typeof data.costOfGoods, value: number) => {
    onChange({
      ...data,
      costOfGoods: {
        ...data.costOfGoods,
        [field]: value
      }
    });
  };

  const calculateGrossProfit = () => {
    const totalIncome = data.grossReceipts - data.returns + data.otherIncome;
    const totalCostOfGoodsSold = Object.values(data.costOfGoods).reduce((sum, val) => sum + val, 0);
    return totalIncome - totalCostOfGoodsSold;
  };

  return (
    <section style={formSectionStyles.section}>
      <h4>Income</h4>
      <div style={formFieldStyles.group}>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Gross Receipts or Sales</label>
            <input
              type="number"
              value={data.grossReceipts}
              onChange={(e) => handleChange('grossReceipts', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Returns and Allowances</label>
            <input
              type="number"
              value={data.returns}
              onChange={(e) => handleChange('returns', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Other Income</label>
            <input
              type="number"
              value={data.otherIncome}
              onChange={(e) => handleChange('otherIncome', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <h5>Cost of Goods Sold</h5>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Beginning Inventory</label>
            <input
              type="number"
              value={data.costOfGoods.inventory}
              onChange={(e) => handleCostOfGoodsChange('inventory', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Purchases</label>
            <input
              type="number"
              value={data.costOfGoods.purchases}
              onChange={(e) => handleCostOfGoodsChange('purchases', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Materials and Supplies</label>
            <input
              type="number"
              value={data.costOfGoods.materials}
              onChange={(e) => handleCostOfGoodsChange('materials', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Labor</label>
            <input
              type="number"
              value={data.costOfGoods.labor}
              onChange={(e) => handleCostOfGoodsChange('labor', parseFloat(e.target.value))}
              style={formFieldStyles.input}
              min="0"
              step="0.01"
            />
          </div>
        </div>

        <div style={formFieldStyles.total}>
          <label>Gross Profit</label>
          <span>${calculateGrossProfit().toFixed(2)}</span>
        </div>
      </div>
    </section>
  );
};
