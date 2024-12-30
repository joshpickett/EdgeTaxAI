import React from 'react';
import { Container, Button, Box } from '@mui/material';
import { IRSFormTemplate, IRSFormData } from '../../shared/types/irs-forms';
import { IRSFormSectionComponent } from './IRSFormSection';
import { FormProvider, useForm } from 'react-hook-form';
import { irsValidationService } from '../../shared/services/irsValidationService';

interface Props {
  template: IRSFormTemplate;
  initialData?: IRSFormData;
  onSubmit: (data: IRSFormData) => void;
}

export const IRSForm: React.FC<Props> = ({
  template,
  initialData,
  onSubmit
}) => {
  const methods = useForm({
    defaultValues: initialData?.data || {}
  });

  const { handleSubmit, formState: { errors } } = methods;

  const validateForm = async (data: any) => {
    const validation = await irsValidationService.validateForm(
      template.sections.flatMap(s => s.fields),
      data
    );

    if (!validation.isValid) {
      validation.errors.forEach(error => {
        methods.setError(error.field, {
          type: 'manual',
          message: error.message
        });
      });
      return false;
    }

    return true;
  };

  const handleFormSubmit = async (data: any) => {
    const isValid = await validateForm(data);
    if (isValid) {
      onSubmit({
        templateId: template.id,
        status: 'draft',
        data
      });
    }
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <Container maxWidth="md">
          {template.sections.map((section) => (
            <IRSFormSectionComponent
              key={section.id}
              section={section}
              errors={errors}
            />
          ))}
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              size="large"
            >
              Save Form
            </Button>
          </Box>
        </Container>
      </form>
    </FormProvider>
  );
};
