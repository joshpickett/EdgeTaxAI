import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from api.services.mef_service import MeFService
from api.services.mef.xml_optimizer import XMLOptimizer
from api.services.mef.schema_manager import SchemaManager

class TestMeFPerformance:
    
    @pytest.fixture
    def large_xml_content(self):
        """Generate large XML content for testing"""
        return '''
            <?xml version="1.0" encoding="UTF-8"?>
            <Form1099NEC>
                <!-- Large XML content here -->
            </Form1099NEC>
        ''' * 1000  # Multiply to create large content

    def test_xml_optimization_performance(self, large_xml_content):
        optimizer = XMLOptimizer()
        
        # Measure optimization time
        start_time = time.time()
        optimized = optimizer.optimize(large_xml_content)
        end_time = time.time()
        
        optimization_time = end_time - start_time
        
        # Assertions
        assert optimization_time < 2.0  # Should optimize within 2 seconds
        assert len(optimized) < len(large_xml_content)  # Should be smaller

    def test_schema_validation_performance(self, large_xml_content):
        schema_manager = SchemaManager()
        
        # Measure validation time
        start_time = time.time()
        result = schema_manager.validate_schema(large_xml_content, '1099_NEC')
        end_time = time.time()
        
        validation_time = end_time - start_time
        
        # Assertions
        assert validation_time < 1.0  # Should validate within 1 second
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_concurrent_submissions(self):
        mef_service = MeFService()
        num_concurrent = 10
        
        async def submit_test_form():
            test_data = {
                'user_id': 1,
                'payer': {'name': 'Test Corp'},
                'recipient': {'name': 'John Doe'},
                'payments': {'nonemployee_compensation': 5000.00}
            }
            return await mef_service.submit_1099_nec(test_data)
        
        # Execute concurrent submissions
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [submit_test_form() for _ in range(num_concurrent)]
            results = await asyncio.gather(*futures)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / num_concurrent
        
        # Assertions
        assert avg_time < 2.0  # Average time per submission
        assert all(r['success'] for r in results)

    def test_memory_usage(self, large_xml_content):
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform memory-intensive operations
        optimizer = XMLOptimizer()
        schema_manager = SchemaManager()
        
        for _ in range(100):
            optimized = optimizer.optimize(large_xml_content)
            schema_manager.validate_schema(optimized, '1099_NEC')
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Assertions
        assert memory_increase < 100 * 1024 * 1024  # Less than 100MB increase

    @pytest.mark.asyncio
    async def test_batch_processing_performance(self):
        optimizer = XMLOptimizer()
        
        # Generate batch of documents
        documents = [
            f'<Form1099NEC><PayerName>Test{i}</PayerName></Form1099NEC>'
            for i in range(1000)
        ]
        
        # Measure batch processing time
        start_time = time.time()
        batches = optimizer.batch_process(documents)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Assertions
        assert processing_time < 5.0  # Should process within 5 seconds
        assert len(batches) > 0
