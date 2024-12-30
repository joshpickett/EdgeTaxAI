import React, { useState } from 'react';
import { ExpenseType, ExpenseStatus } from '../../types/expenses';
import { ExpenseUploader } from './ExpenseUploader';
import { ExpenseList } from './ExpenseList';
import { ImportOptions } from '../DocumentCollection/ImportOptions';

interface ExpenseCollectionViewProps {
  onExpenseUpload: (data: any, type: ExpenseType) => Promise<void>;
  onImportSelect: (source: string) => Promise<void>;
  expenses: Array<{
    id: string;
    type: ExpenseType;
    status: ExpenseStatus;
    amount: number;
    description: string;
  }>;
  isProcessing: boolean;
}

export const ExpenseCollectionView: React.FC<ExpenseCollectionViewProps> = ({
  onExpenseUpload,
  onImportSelect,
  expenses,
  isProcessing
}) => {
  const [selectedImportSource, setSelectedImportSource] = useState<string | null>(null);

  const handleImportSelect = async (source: string) => {
    setSelectedImportSource(source);
    await onImportSelect(source);
  };

  return (
    <div className="expense-collection-container">
      <section className="import-section">
        <h2>Import Expenses</h2>
        <ImportOptions
          onSelect={handleImportSelect}
          selectedSource={selectedImportSource}
        />
      </section>

      <section className="upload-section">
        <h2>Add Expenses</h2>
        <ExpenseUploader
          onUpload={onExpenseUpload}
          isProcessing={isProcessing}
        />
      </section>

      <section className="expenses-section">
        <h2>Expense List</h2>
        <ExpenseList expenses={expenses} />
      </section>
    </div>
  );
};
