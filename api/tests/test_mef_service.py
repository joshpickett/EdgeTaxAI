import pytest
from unittest.mock import Mock, patch
from api.services.mef_service import MeFService
from api.services.mef.xml_signer import XMLSigner
from api.services.mef.schema_manager import SchemaManager
from api.models.mef_submissions import MeFSubmission, SubmissionStatus
from api.services.mef.amendment_tracker import AmendmentTracker

@pytest.fixture
def mef_service():
    return MeFService()

@pytest.fixture
def mock_xml_signer():
    return Mock(spec=XMLSigner)

@pytest.fixture
def mock_schema_manager():
    return Mock(spec=SchemaManager)

@pytest.fixture
def amendment_tracker():
    return AmendmentTracker()

class TestMeFService:
    
    @pytest.mark.asyncio
    async def test_submit_1099_nec(self, mef_service, mock_xml_signer):
        # Test data
        test_data = {
            'user_id': 1,
            'payer': {
                'name': 'Test Corp',
                'tin': '123456789'
            },
            'recipient': {
                'name': 'John Doe',
                'tin': '987654321'
            },
            'payments': {
                'nonemployee_compensation': 5000.00
            }
        }
        
        # Mock dependencies
        with patch.object(mef_service, 'xml_signer', mock_xml_signer):
            mock_xml_signer.sign_xml.return_value = '<signed>test</signed>'
            
            # Execute test
            result = await mef_service.submit_1099_nec(test_data)
            
            # Assertions
            assert result['success'] is True
            assert 'submission_id' in result
            mock_xml_signer.sign_xml.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_submission_status(self, mef_service):
        # Test data
        submission_id = 'test123'
        
        # Mock submission
        mock_submission = MeFSubmission(
            id=1,
            submission_id=submission_id,
            status=SubmissionStatus.ACCEPTED
        )
        
        # Mock database query
        with patch('api.models.mef_submissions.MeFSubmission.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_submission
            
            # Execute test
            result = await mef_service.check_submission_status(submission_id)
            
            # Assertions
            assert result['success'] is True
            assert result['status'] == SubmissionStatus.ACCEPTED.value

    @pytest.mark.asyncio
    async def test_validation_failure(self, mef_service, mock_schema_manager):
        # Test data with invalid values
        test_data = {
            'user_id': 1,
            'payer': {
                'name': '',  # Invalid: empty name
                'tin': '123'  # Invalid: short TIN
            }
        }
        
        # Mock schema validation
        with patch.object(mef_service, 'schema_manager', mock_schema_manager):
            mock_schema_manager.validate_schema.return_value = {
                'is_valid': False,
                'errors': ['Invalid payer information']
            }
            
            # Execute test
            result = await mef_service.submit_1099_nec(test_data)
            
            # Assertions
            assert result['success'] is False
            assert 'errors' in result

    def test_xml_generation(self, mef_service):
        # Test data
        test_data = {
            'user_id': 1,
            'tax_year': 2023,
            'form_type': '1099-NEC',
            'content': {
                'payer': {'name': 'Test Corp'},
                'recipient': {'name': 'John Doe'},
                'amount': 5000.00
            }
        }
        
        # Execute test
        xml_content = mef_service._generate_xml(test_data)
        
        # Assertions
        assert '<Form1099NEC>' in xml_content
        assert '<PayerName>Test Corp</PayerName>' in xml_content
        assert '<RecipientName>John Doe</RecipientName>' in xml_content

    @pytest.mark.asyncio
    async def test_create_amendment(self, amendment_tracker, mock_schema_manager):
        # Test data
        original_submission_id = 'test123'
        amendment_data = {
            'changes': {
                'nonemployee_compensation': 6000.00
            }
        }
        
        # Mock original submission
        mock_submission = MeFSubmission(
            id=1,
            submission_id=original_submission_id,
            form_type='1099_NEC',
            status=SubmissionStatus.ACCEPTED,
            xml_content='<original>test</original>'
        )
        
        # Configure mocks
        with patch.object(amendment_tracker, 'document_manager', mock_schema_manager):
            mock_schema_manager.store_document.return_value = 'doc123'
            
            # Execute test
            result = await amendment_tracker.create_amendment(
                original_submission_id,
                amendment_data
            )
            
            # Assertions
            assert result['success'] is True
            assert 'amendment_id' in result
            mock_schema_manager.store_document.assert_called_once()
