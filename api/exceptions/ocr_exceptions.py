class OCRBaseException(Exception):
    """Base exception for OCR-related errors"""
    pass

class OCRProcessingError(OCRBaseException):
    """Raised when OCR processing fails"""
    pass

class DocumentValidationError(OCRBaseException):
    """Raised when document validation fails"""
    pass

class BatchProcessingError(OCRBaseException):
    """Raised when batch processing fails"""
    pass

class DocumentClassificationError(OCRBaseException):
    """Raised when document classification fails"""
    pass

class OCRServiceError(OCRBaseException):
    """Raised when OCR service encounters an error"""
    pass
