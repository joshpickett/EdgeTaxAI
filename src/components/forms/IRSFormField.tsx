import React from 'react';
import { TextField, Checkbox, Select, MenuItem, FormHelperText } from '@mui/material';
import { IRSFormField } from '../../shared/types/irs-forms';
import { useFormContext } from 'react-hook-form';

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
          <TextField
            {...register(field.name)}
            label={field.label}
            type={field.type}
            required={field.required}
            error={!!error}
            helperText={error || field.helpText}
            placeholder={field.placeholder}
            fullWidth
            InputLabelProps={{ shrink: true }}
            onChange={(e) => onChange(e.target.value)}
            value={value || ''}
          />
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
            <Checkbox
              {...register(field.name)}
              checked={!!value}
              onChange={(e) => onChange(e.target.checked)}
            />
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
