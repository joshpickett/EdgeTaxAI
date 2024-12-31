import React from 'react';
import { formSectionStyles } from '../styles/FormSectionStyles';

interface FormSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  isValid?: boolean;
  errors?: string[];
}

export const FormSection: React.FC<FormSectionProps> = ({
  title,
  description,
  children,
  isValid = true,
  errors = []
}) => {
  return (
    <section style={formSectionStyles.section}>
      <div style={formSectionStyles.header}>
        <h3 style={formSectionStyles.title}>{title}</h3>
        {description && (
          <p style={formSectionStyles.description}>{description}</p>
        )}
      </div>
      
      <div style={formSectionStyles.content}>
        {children}
      </div>
      
      {!isValid && errors.length > 0 && (
        <div style={formSectionStyles.errors}>
          {errors.map((error, index) => (
            <p key={index} style={formSectionStyles.error}>{error}</p>
          ))}
        </div>
      )}
    </section>
  );
};
