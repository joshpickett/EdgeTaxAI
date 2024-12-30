import React from 'react';
import { Paper, Typography, Grid } from '@mui/material';
import { IRSFormSection } from '../../shared/types/irs-forms';
import { IRSFormFieldComponent } from './IRSFormField';
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
    <Paper sx={{ p: 3, mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        {section.title}
      </Typography>
      {section.description && (
        <Typography variant="body2" color="textSecondary" paragraph>
          {section.description}
        </Typography>
      )}
      <Grid container spacing={3}>
        {section.fields.map((field) => (
          <Grid item xs={12} sm={6} key={field.id}>
            <IRSFormFieldComponent
              field={field}
              value={watch(field.name)}
              onChange={(value) => setValue(field.name, value)}
              error={errors[field.name]}
            />
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};
