class OCRProcessingError(Exception):
    """Raised when Optical Character Recognition processing fails"""
    pass

class DocumentValidationError(Exception):
    """Raised when document validation fails"""
    pass

class BatchProcessingError(Exception):
    """Raised when batch processing fails"""
    pass

class DocumentClassificationError(Exception):
    """Raised when document classification fails"""
    pass
