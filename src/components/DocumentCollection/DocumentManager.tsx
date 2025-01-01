import React, { useState } from 'react';
import { DocumentUploader } from './DocumentUploader';
import { DocumentList } from './DocumentList';

interface DocumentManagerProps {
  userId: string;
  requiredDocuments: Array<{
    id: string;
    name: string;
    description: string;
    required: boolean;
    status: DocumentStatus;
    category: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  onDocumentProcessed?: (result: any) => void;
  onComplete: () => void;
}

export const DocumentManager: React.FC<DocumentManagerProps> = ({
  userId,
  requiredDocuments,
  onDocumentProcessed,
  onComplete
}) => {
  const [uploadedDocs, setUploadedDocs] = useState<Array<any>>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<string>('');

  const handleDocumentUpload = async (file: File) => {
    try {
      setIsProcessing(true);
      setProcessingStatus('Uploading document...');
      
      // Enhanced document processing
      const formData = new FormData();
      formData.append('receipt', file);
      formData.append('userId', userId);

      // Process document with Optical Character Recognition
      setProcessingStatus('Processing with Optical Character Recognition...');
      const ocrResponse = await fetch('/api/ocr/process-receipt', {
        method: 'POST',
        body: formData,
        headers: {
          'X-User-ID': userId
        }
      });

      if (!ocrResponse.ok) {
        throw new Error('Optical Character Recognition processing failed');
      }

      const ocrResult = await ocrResponse.json();
      
      // Validate document against requirements
      const validationResult = await fetch('/api/documents/validate', {
        method: 'POST',
        body: JSON.stringify({
          documentId: ocrResult.document_id,
          requirements: requiredDocuments
        }),
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId
        }
      });

      // Update document status based on Optical Character Recognition results
      setProcessingStatus('Updating document status...');
      const updatedDocs = uploadedDocs.map(doc => {
        if (doc.id === ocrResult.document_id) {
          return {
            ...doc,
            status: DocumentStatus.PROCESSED,
            metadata: ocrResult.extracted_data
          };
        }
        return doc;
      });

      setUploadedDocs(updatedDocs);
      onDocumentProcessed?.(ocrResult);

    } catch (error) {
      console.error('Error uploading document:', error);
    } finally {
      setIsProcessing(false);
      setProcessingStatus('');
    }
  };

  return (
    <div>
      <DocumentUploader
        onUpload={handleDocumentUpload}
        isProcessing={isProcessing}
        processingStatus={processingStatus}
        uploadedFiles={uploadedDocs}
      />

      <DocumentList
        documents={uploadedDocs}
        requiredDocuments={requiredDocuments}
        showMetadata={true}
      />
    </div>
  );
};
