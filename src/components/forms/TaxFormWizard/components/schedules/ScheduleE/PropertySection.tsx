import React from 'react';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { FormIntegrationService } from 'api/services/integration/form_integration_service';
import { ValidationFeedback } from '../../../ValidationFeedback';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';

interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

interface RentalProperty {
  address: string;
  propertyType: string;
  daysRented: number;
  personalUse: number;
  fairRentalDays: number;
}

interface Props {
  property: RentalProperty;
  onChange: (property: RentalProperty) => void;
  onRemove: () => void;
  onValidate?: (result: ValidationResult) => void;
}

export const PropertySection: React.FC<Props> = ({
  property,
  onChange,
  onRemove,
  onValidate
}) => {
  const formValidationService = new FormValidationService();
  const formIntegrationService = new FormIntegrationService();
  const [validationResults, setValidationResults] = React.useState<ValidationResult | null>(null);

  const handlePropertyChange = async (field: keyof RentalProperty, value: any) => {
    try {
      const result = await formIntegrationService.calculatePropertyData({
        ...property,
        [field]: value
      });
      
      onChange(result);
      
      // Validate the property data
      const validation = await formValidationService.validate_property(result);
      setValidationResults(validation);
      onValidate?.(validation);
    } catch (error) {
      console.error('Error calculating property data:', error);
    }
  };

  return (
    <div style={formFieldStyles.group}>
      <div style={formFieldStyles.row}>
        <div style={formFieldStyles.column}>
          <label style={formFieldStyles.label}>Property Address</label>
          <input
            type="text"
            value={property.address}
            onChange={(e) => handlePropertyChange('address', e.target.value)}
            style={formFieldStyles.input}
            required
          />
        </div>
        <div style={formFieldStyles.column}>
          <label style={formFieldStyles.label}>Property Type</label>
          <select
            value={property.propertyType}
            onChange={(e) => handlePropertyChange('propertyType', e.target.value)}
            style={formFieldStyles.select}
            required
          >
            <option value="">Select Type</option>
            <option value="single_family">Single Family</option>
            <option value="multi_family">Multi Family</option>
            <option value="vacation">Vacation Property</option>
            <option value="commercial">Commercial</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>

      <div style={formFieldStyles.row}>
        <div style={formFieldStyles.column}>
          <label style={formFieldStyles.label}>Days Rented</label>
          <input
            type="number"
            value={property.daysRented}
            onChange={(e) => handlePropertyChange('daysRented', parseInt(e.target.value))}
            style={formFieldStyles.input}
            min="0"
            max="365"
          />
        </div>
        <div style={formFieldStyles.column}>
          <label style={formFieldStyles.label}>Personal Use Days</label>
          <input
            type="number"
            value={property.personalUse}
            onChange={(e) => handlePropertyChange('personalUse', parseInt(e.target.value))}
            style={formFieldStyles.input}
            min="0"
            max="365"
          />
        </div>
        <div style={formFieldStyles.column}>
          <label style={formFieldStyles.label}>Fair Rental Days</label>
          <input
            type="number"
            value={property.fairRentalDays}
            onChange={(e) => handlePropertyChange('fairRentalDays', parseInt(e.target.value))}
            style={formFieldStyles.input}
            min="0"
            max="365"
          />
        </div>
      </div>
      
      {validationResults && (
        <ValidationFeedback
          errors={validationResults.errors}
          warnings={validationResults.warnings}
          suggestions={[]}
        />
      )}

      <button
        onClick={onRemove}
        style={formFieldStyles.button.secondary}
      >
        Remove Property
      </button>
    </div>
  );
};
