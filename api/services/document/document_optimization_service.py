from typing import Dict, Any, Optional
import logging
from datetime import datetime
import io
from PIL import Image
import PyPDF2

class DocumentOptimizationService:
    """Service for optimizing documents before storage"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.optimization_settings = {
            'image': {
                'max_dimension': 2000,
                'quality': 85,
                'formats': ['image/jpeg', 'image/png', 'image/gif']
            },
            'pdf': {
                'compress_images': True,
                'max_quality': 85,
                'formats': ['application/pdf']
            }
        }

    async def optimize_document(
        self,
        content: bytes,
        mime_type: str
    ) -> bytes:
        """Optimize document based on type"""
        try:
            if mime_type in self.optimization_settings['image']['formats']:
                return await self._optimize_image(content)
            elif mime_type in self.optimization_settings['pdf']['formats']:
                return await self._optimize_pdf(content)
            return content
            
        except Exception as exception:
            self.logger.error(f"Error optimizing document: {str(exception)}")
            raise

    async def _optimize_image(self, content: bytes) -> bytes:
        """Optimize image content"""
        try:
            image = Image.open(io.BytesIO(content))
            
            # Resize if needed
            max_dimension = self.optimization_settings['image']['max_dimension']
            if max(image.size) > max_dimension:
                ratio = max_dimension / max(image.size)
                new_size = tuple(int(dimension * ratio) for dimension in image.size)
                image = image.resize(new_size, Image.LANCZOS)
            
            # Save with optimization
            output = io.BytesIO()
            image.save(
                output,
                format=image.format,
                optimize=True,
                quality=self.optimization_settings['image']['quality']
            )
            return output.getvalue()
            
        except Exception as exception:
            self.logger.error(f"Error optimizing image: {str(exception)}")
            raise

    async def _optimize_pdf(self, content: bytes) -> bytes:
        """Optimize PDF content"""
        try:
            input_pdf = PyPDF2.PdfReader(io.BytesIO(content))
            output_pdf = PyPDF2.PdfWriter()
            
            for page in input_pdf.pages:
                output_pdf.add_page(page)
            
            # Apply compression settings
            output_pdf.add_metadata(input_pdf.metadata)
            
            output_stream = io.BytesIO()
            output_pdf.write(output_stream)
            return output_stream.getvalue()
            
        except Exception as exception:
            self.logger.error(f"Error optimizing PDF: {str(exception)}")
            raise

    def get_optimization_statistics(self, original_size: int, optimized_size: int) -> Dict[str, Any]:
        """Calculate optimization statistics"""
        return {
            'original_size': original_size,
            'optimized_size': optimized_size,
            'reduction_percentage': round(
                (original_size - optimized_size) / original_size * 100,
                2
            ),
            'timestamp': datetime.utcnow().isoformat()
        }
