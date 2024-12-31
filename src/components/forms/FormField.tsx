import React from 'react';
import { formFieldStyles } from '../styles/FormFieldStyles';

interface FormFieldProps {
  label: string;
  name: string;
  value: string | number;
  onChange: (value: string) => void;
  type?: 'text' | 'number' | 'date' | 'select';
  options?: Array<{ value: string; label: string }>;
  error?: string;
  required?: boolean;
  placeholder?: string;
  disabled?: boolean;
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  name,
  value,
  onChange,
  type = 'text',
  options = [],
  error,
  required = false,
  placeholder,
  disabled = false
}) => {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    onChange(event.target.value);
  };

  return (
    <div style={formFieldStyles.container}>
      <label 
        htmlFor={name}
        style={formFieldStyles.label}
      >
        {label}
        {required && <span style={formFieldStyles.required}>*</span>}
      </label>

      {type === 'select' ? (
        <select
          id={name}
          name={name}
          value={value}
          onChange={handleChange}
          style={formFieldStyles.select}
          disabled={disabled}
        >
          {options.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          id={name}
          name={name}
          type={type}
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          style={formFieldStyles.input}
          disabled={disabled}
          required={required}
        />
      )}

      {error && (
        <span style={formFieldStyles.error}>{error}</span>
      )}
    </div>
  );
};
