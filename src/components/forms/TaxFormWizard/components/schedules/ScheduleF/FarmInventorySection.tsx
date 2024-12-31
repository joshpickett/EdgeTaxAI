import React from 'react';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';

interface FarmInventory {
  livestock: {
    beginning: number;
    ending: number;
  };
  crops: {
    beginning: number;
    ending: number;
  };
  supplies: {
    beginning: number;
    ending: number;
  };
}

interface Props {
  data: FarmInventory;
  onChange: (data: FarmInventory) => void;
}

export const FarmInventorySection: React.FC<Props> = ({
  data,
  onChange
}) => {
  const handleChange = (category: keyof FarmInventory, type: 'beginning' | 'ending', value: number) => {
    onChange({
      ...data,
      [category]: {
        ...data[category],
        [type]: value
      }
    });
  };

  return (
    <section style={formSectionStyles.section}>
      <h4>Farm Inventory</h4>
      <div style={formFieldStyles.group}>
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <h5>Livestock Inventory</h5>
            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Beginning of Year</label>
                <input
                  type="number"
                  value={data.livestock.beginning}
                  onChange={(e) => handleChange('livestock', 'beginning', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>End of Year</label>
                <input
                  type="number"
                  value={data.livestock.ending}
                  onChange={(e) => handleChange('livestock', 'ending', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
            </div>
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <h5>Crops Inventory</h5>
            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Beginning of Year</label>
                <input
                  type="number"
                  value={data.crops.beginning}
                  onChange={(e) => handleChange('crops', 'beginning', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>End of Year</label>
                <input
                  type="number"
                  value={data.crops.ending}
                  onChange={(e) => handleChange('crops', 'ending', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
            </div>
          </div>
        </div>

        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <h5>Supplies Inventory</h5>
            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>Beginning of Year</label>
                <input
                  type="number"
                  value={data.supplies.beginning}
                  onChange={(e) => handleChange('supplies', 'beginning', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>End of Year</label>
                <input
                  type="number"
                  value={data.supplies.ending}
                  onChange={(e) => handleChange('supplies', 'ending', parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
