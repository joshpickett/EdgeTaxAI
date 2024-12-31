import React, { useState, useEffect } from 'react';
import { FormValidationService } from 'api/services/form/form_validation_service';
import { formFieldStyles } from '../../../styles/FormFieldStyles';
import { formSectionStyles } from '../../../styles/FormSectionStyles';
import { DocumentCapture } from '../../../DocumentCapture';
import { ExpenseCategory, ValidationResult } from '../../../types/scheduleC.types';

interface Props {
  data: ExpenseCategory[];
  onChange: (data: ExpenseCategory[]) => void;
  onValidate?: (result: ValidationResult) => void;
}

export const ExpenseSection: React.FC<Props> = ({
  data,
  onChange,
  onValidate
}) => {
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const formValidationService = new FormValidationService();

  useEffect(() => {
    const validateExpenses = async () => {
      try {
        const validation = await formValidationService.validate_section(
          'ScheduleC',
          'expenses',
          data
        );
        onValidate?.(validation);
      } catch (error) {
        console.error('Error validating expenses:', error);
      }
    };
    
    validateExpenses();
  }, [data]);

  const handleExpenseChange = (categoryId: string, amount: number) => {
    const updatedCategories = data.map(category => 
      category.id === categoryId ? { ...category, amount } : category
    );

    onChange(updatedCategories);
    onValidate?.({
      isValid: true,
      errors: [],
      warnings: []
    });
  };

  const handleDocumentUpload = async (categoryId: string, documentId: string) => {
    const updatedCategories = data.map(category => {
      if (category.id === categoryId) {
        return {
          ...category,
          documentIds: [...(category.documentIds || []), documentId]
        };
      }
      return category;
    });

    onChange({
      ...data,
      categories: updatedCategories
    });
  };

  return (
    <section style={formSectionStyles.section}>
      <h4>Business Expenses</h4>
      <div style={formFieldStyles.group}>
        {data.map(category => (
          <div key={category.id} style={formFieldStyles.expenseCategory}>
            <div style={formFieldStyles.row}>
              <div style={formFieldStyles.column}>
                <label style={formFieldStyles.label}>{category.name}</label>
                <input
                  type="number"
                  value={category.amount}
                  onChange={(e) => handleExpenseChange(category.id, parseFloat(e.target.value))}
                  style={formFieldStyles.input}
                  min="0"
                  step="0.01"
                />
              </div>
              <div style={formFieldStyles.column}>
                <button
                  onClick={() => setActiveCategory(category.id)}
                  style={formFieldStyles.button.secondary}
                >
                  Add Receipt
                </button>
              </div>
            </div>

            {category.documentIds && category.documentIds.length > 0 && (
              <div style={formFieldStyles.documents}>
                <span>{category.documentIds.length} document(s) attached</span>
              </div>
            )}

            {activeCategory === category.id && (
              <DocumentCapture
                onCapture={async (file) => {
                  // Handle document upload
                  const documentId = 'temp_id'; // Replace with actual upload logic
                  await handleDocumentUpload(category.id, documentId);
                  setActiveCategory(null);
                }}
                onError={(error) => console.error('Document capture error:', error)}
              />
            )}
          </div>
        ))}

        <div style={formFieldStyles.total}>
          <label>Total Expenses</label>
          <span>${data.reduce((sum, cat) => sum + cat.amount, 0).toFixed(2)}</span>
        </div>
      </div>
    </section>
  );
};

// Default expense categories
export const defaultExpenseCategories: ExpenseCategory[] = [
  {
    id: 'advertising',
    name: 'Advertising',
    description: 'Advertising and promotional expenses',
    amount: 0
  },
  {
    id: 'car',
    name: 'Car and Truck Expenses',
    description: 'Vehicle expenses for business use',
    amount: 0
  },
  {
    id: 'commissions',
    name: 'Commissions and Fees',
    description: 'Commissions and fees paid',
    amount: 0
  },
  {
    id: 'contract_labor',
    name: 'Contract Labor',
    description: 'Payments to contractors',
    amount: 0
  },
  {
    id: 'depletion',
    name: 'Depletion',
    description: 'Natural resource depletion',
    amount: 0
  },
  {
    id: 'depreciation',
    name: 'Depreciation',
    description: 'Asset depreciation expenses',
    amount: 0
  },
  {
    id: 'insurance',
    name: 'Insurance',
    description: 'Business insurance premiums',
    amount: 0
  },
  {
    id: 'interest',
    name: 'Interest',
    description: 'Interest paid on business loans',
    amount: 0
  },
  {
    id: 'legal',
    name: 'Legal and Professional Services',
    description: 'Legal and professional fees',
    amount: 0
  },
  {
    id: 'office',
    name: 'Office Expense',
    description: 'Office supplies and expenses',
    amount: 0
  },
  {
    id: 'pension',
    name: 'Pension and Profit-Sharing Plans',
    description: 'Contributions to employee benefit plans',
    amount: 0
  },
  {
    id: 'rent_vehicles',
    name: 'Rent or Lease - Vehicles',
    description: 'Vehicle rental or lease expenses',
    amount: 0
  },
  {
    id: 'rent_other',
    name: 'Rent or Lease - Other',
    description: 'Other business property rental',
    amount: 0
  },
  {
    id: 'repairs',
    name: 'Repairs and Maintenance',
    description: 'Equipment and property maintenance',
    amount: 0
  },
  {
    id: 'supplies',
    name: 'Supplies',
    description: 'Business supplies purchased',
    amount: 0
  },
  {
    id: 'taxes',
    name: 'Taxes and Licenses',
    description: 'Business taxes and license fees',
    amount: 0
  },
  {
    id: 'travel',
    name: 'Travel',
    description: 'Business travel expenses',
    amount: 0
  },
  {
    id: 'meals',
    name: 'Meals',
    description: 'Business meals (50% deductible)',
    amount: 0
  },
  {
    id: 'utilities',
    name: 'Utilities',
    description: 'Business utility expenses',
    amount: 0
  },
  {
    id: 'wages',
    name: 'Wages',
    description: 'Employee wages paid',
    amount: 0
  },
  {
    id: 'other',
    name: 'Other Expenses',
    description: 'Other business expenses',
    amount: 0
  }
];
