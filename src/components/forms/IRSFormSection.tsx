import React from 'react';
import { IRSFormSection } from '../../shared/types/irs-forms';
import { formSectionStyles } from './TaxFormWizard/styles/FormSectionStyles';
import { useFormContext } from 'react-hook-form';

interface Props {
  section: IRSFormSection;
  errors?: Record<string, string>;
}

export const IRSFormSectionComponent: React.FC<Props> = ({
  section,
  errors = {}
}) => {
  const { watch, setValue } = useFormContext();

  return (
    <div style={formSectionStyles.container}>
      <div style={formSectionStyles.header}>
        <h3 style={formSectionStyles.title}>
          {section.title}
        </h3>
      {section.description && (
        <p style={formSectionStyles.description}>
          {section.description}
        </p>
      )}
      </div>
    </div>
  );
};
