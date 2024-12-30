import React, { useState } from 'react';
import { Document, Page } from 'react-pdf';
import { LoadingOverlay } from './LoadingOverlay';

interface DocumentPreviewProps {
  file: File | string;
  onLoadSuccess?: () => void;
  onLoadError?: (error: Error) => void;
}

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  file,
  onLoadSuccess,
  onLoadError
}) => {
  const [numPages, setNumPages] = useState<number>(1);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const handleLoadSuccess = ({ numPages }: { numPages: number }) => {
    setIsLoading(false);
    setNumPages(numPages);
    onLoadSuccess?.();
  };

  const handleLoadError = (error: Error) => {
    setIsLoading(false);
    onLoadError?.(error);
  };

  return (
    <div className="document-preview">
      {isLoading && <LoadingOverlay />}
      
      <Document
        file={file}
        onLoadSuccess={handleLoadSuccess}
        onLoadError={handleLoadError}
      >
        <Page 
          pageNumber={pageNumber}
          renderTextLayer={false}
          renderAnnotationLayer={false}
        />
      </Document>

      {numPages > 1 && (
        <div className="pagination-controls">
          <button
            onClick={() => setPageNumber(Math.max(1, pageNumber - 1))}
            disabled={pageNumber <= 1}
          >
            Previous
          </button>
          <span>
            Page {pageNumber} of {numPages}
          </span>
          <button
            onClick={() => setPageNumber(Math.min(numPages, pageNumber + 1))}
            disabled={pageNumber >= numPages}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};
