import React, { useCallback } from 'react';
import { DocumentType } from '../../types/documents';

interface DocumentUploaderProps {
  onUpload: (file: File, type: DocumentType) => Promise<void>;
  isProcessing: boolean;
}

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({
  onUpload,
  isProcessing
}) => {
  const handleDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach(file => {
      // Determine document type based on file type/name
      const documentType = determineDocumentType(file);
      onUpload(file, documentType);
    });
  }, [onUpload]);

  const determineDocumentType = (file: File): DocumentType => {
    // Logic to determine document type based on file
    if (file.name.toLowerCase().includes('1099')) {
      return DocumentType.FORM_1099;
    }
    return DocumentType.OTHER;
  };

  return (
    <div className="document-uploader">
      <div className="dropzone" {...getRootProps()}>
        <input {...getInputProps()} />
        <p>Drag & drop files here, or click to select files</p>
      </div>
      {isProcessing && (
        <div className="processing-indicator">
          Processing documents...
        </div>
      )}
    </div>
  );
};
