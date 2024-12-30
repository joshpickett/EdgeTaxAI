import React from 'react';

interface ImportOptionsProps {
  onSelect: (source: string) => void;
  selectedSource: string | null;
}

export const ImportOptions: React.FC<ImportOptionsProps> = ({
  onSelect,
  selectedSource
}) => {
  const importSources = [
    {
      id: 'app',
      title: 'From Application',
      description: 'Import expenses tracked within the application'
    },
    {
      id: 'bank',
      title: 'From Bank',
      description: 'Import transactions from connected bank accounts'
    }
  ];

  return (
    <div className="import-options">
      {importSources.map(source => (
        <div
          key={source.id}
          className={`import-option ${selectedSource === source.id ? 'selected' : ''}`}
          onClick={() => onSelect(source.id)}
        >
          <h3>{source.title}</h3>
          <p>{source.description}</p>
        </div>
      ))}
    </div>
  );
};
