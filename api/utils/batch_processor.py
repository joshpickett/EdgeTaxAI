import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import os
from .cache_utils import CacheManager
from .error_handler import handle_api_error
from .monitoring import monitor_api_calls

class BatchProcessor:
    def __init__(self):
        self.cache = CacheManager()
        self.status_cache = {}
        self.processing_queue = asyncio.Queue()
        
    async def process_batch(self, files: List[Dict[str, Any]], user_id: str) -> str:
        """Process a batch of files asynchronously"""
        batch_id = f"batch_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.status_cache[batch_id] = {
            'total': len(files),
            'processed': 0,
            'failed': 0,
            'status': 'processing',
            'results': [],
            'start_time': datetime.now().isoformat(),
            'completion_time': None
        }
        
        try:
            tasks = [self.process_single_file(file, batch_id) for file in files]
            results = await asyncio.gather(*tasks)
            
            self.status_cache[batch_id]['status'] = 'completed'
            self.status_cache[batch_id]['completion_time'] = datetime.now().isoformat()
            self.status_cache[batch_id]['results'].extend(results)
            
            # Cache the final results
            self.cache.set(f"batch_results_{batch_id}", self.status_cache[batch_id], timeout=86400)
            
        except Exception as e:
            logging.error(f"Batch processing error: {e}")
            self.status_cache[batch_id]['status'] = 'failed'
            self.status_cache[batch_id]['error'] = str(e)
            
        return batch_id
    
    async def process_single_file(self, file: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Process a single file in the batch"""
        try:
            start_time = datetime.now()
            
            # Process file and extract data
            result = await self.extract_receipt_data(file)
            
            # Calculate confidence score
            confidence_score = self.calculate_confidence_score(result)
            
            # Update status
            self.status_cache[batch_id]['processed'] += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            processed_result = {
                'filename': file['filename'],
                'data': result,
                'confidence_score': confidence_score,
                'processing_time': processing_time,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
            
            return processed_result
            
        except Exception as e:
            logging.error(f"File processing error: {e}")
            self.status_cache[batch_id]['failed'] += 1
            return {
                'filename': file['filename'],
                'error': str(e),
                'status': 'failed',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get the current status of a batch job"""
        # Try to get from cache first
        cached_results = self.cache.get(f"batch_results_{batch_id}")
        if cached_results:
            return cached_results
            
        return self.status_cache.get(batch_id, {
            'status': 'not_found',
            'processed': 0,
            'failed': 0,
            'total': 0,
            'results': []
        })
        
    def calculate_confidence_score(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score based on extracted data"""
        required_fields = ['total', 'date', 'vendor']
        field_scores = []
        
        for field in required_fields:
            if field in result and result[field]:
                field_scores.append(1.0)
            else:
                field_scores.append(0.0)
                
        return sum(field_scores) / len(field_scores) if field_scores else 0.0
