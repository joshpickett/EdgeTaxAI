import React from 'react';
import { IRSFormField } from '../../shared/types/irs-forms';
import { useFormContext } from 'react-hook-form';
import { formFieldStyles } from './TaxFormWizard/styles/FormFieldStyles';
import classNames from 'classnames';

interface Props {
  field: IRSFormField;
  value: any;
  onChange: (value: any) => void;
  error?: string;
}

export const IRSFormFieldComponent: React.FC<Props> = ({
  field,
  value,
  onChange,
  error
}) => {
  const { register, watch } = useFormContext();
  const dependentValue = field.dependsOn ? watch(field.dependsOn) : null;
  const isVisible = !field.dependsOn || dependentValue;

  if (!isVisible) return null;

  const renderField = () => {
    switch (field.type) {
      case 'text':
      case 'number':
        return (
          <div style={formFieldStyles.container}>
            <label style={formFieldStyles.label}>{field.label}</label>
            <input
              {...register(field.name)}
              style={{
                ...formFieldStyles.input,
                ...(error && formFieldStyles.error)
              }}
              type={field.type}
              required={field.required}
              placeholder={field.placeholder}
              value={value || ''}
              onChange={(e) => onChange(e.target.value)}
            />
          </div>
        );

      case 'select':
        return (
          <>
            <Select
              {...register(field.name)}
              value={value || ''}
              onChange={(e) => onChange(e.target.value)}
              error={!!error}
              fullWidth
              displayEmpty
              style={formFieldStyles.select}
            >
              {field.options?.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
            {(error || field.helpText) && (
              <FormHelperText error={!!error}>
                {error || field.helpText}
              </FormHelperText>
            )}
          </>
        );

      case 'checkbox':
        return (
          <>
            <div style={formFieldStyles.checkbox.container}>
              <input
                type="checkbox"
                {...register(field.name)}
                checked={!!value}
                onChange={(e) => onChange(e.target.checked)}
                style={formFieldStyles.checkbox.input}
              />
              <label>{field.label}</label>
            </div>
            {(error || field.helpText) && (
              <FormHelperText error={!!error}>
                {error || field.helpText}
              </FormHelperText>
            )}
          </>
        );

      default:
        return null;
    }
  };

  return renderField();
};
