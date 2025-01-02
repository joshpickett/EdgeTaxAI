import pytest
from unittest.mock import Mock, patch
from api.services.mef.amendment_tracker import AmendmentTracker
from api.models.mef_submissions import MeFSubmission, SubmissionStatus
from api.utils.document_manager import DocumentManager


@pytest.fixture
def amendment_tracker():
    return AmendmentTracker()


@pytest.fixture
def mock_document_manager():
    return Mock(spec=DocumentManager)


class TestAmendmentTracker:

    @pytest.mark.asyncio
    async def test_create_amendment(self, amendment_tracker, mock_document_manager):
        # Test data
        original_submission_id = "test123"
        amendment_data = {"changes": {"nonemployee_compensation": 6000.00}}

        # Mock original submission
        mock_submission = MeFSubmission(
            id=1,
            submission_id=original_submission_id,
            form_type="1099_NEC",
            status=SubmissionStatus.ACCEPTED,
            xml_content="<original>test</original>",
        )

        # Configure mocks
        with patch.object(amendment_tracker, "document_manager", mock_document_manager):
            mock_document_manager.store_document.return_value = "doc123"

            # Execute test
            result = await amendment_tracker.create_amendment(
                original_submission_id, amendment_data
            )

            # Assertions
            assert result["success"] is True
            assert "amendment_id" in result
            mock_document_manager.store_document.assert_called_once()

    def test_generate_diff(self, amendment_tracker):
        # Test data
        original_xml = """
            <Form1099NEC>
                <NonemployeeCompensation>5000.00</NonemployeeCompensation>
            </Form1099NEC>
        """
        amended_xml = """
            <Form1099NEC>
                <NonemployeeCompensation>6000.00</NonemployeeCompensation>
            </Form1099NEC>
        """

        # Execute test
        diff_result = amendment_tracker.generate_diff(original_xml, amended_xml)

        # Assertions
        assert "changes" in diff_result
        assert "summary" in diff_result
        assert diff_result["summary"]["total_changes"] > 0
        assert "NonemployeeCompensation" in str(diff_result["changes"])

    def test_xml_diff_calculation(self, amendment_tracker):
        # Test data
        original_xml = "<test><value>5000</value></test>"
        amended_xml = "<test><value>6000</value></test>"

        # Execute test
        diff_result = amendment_tracker._calculate_xml_diff(original_xml, amended_xml)

        # Assertions
        assert len(diff_result["changes"]) == 1
        assert diff_result["changes"][0]["type"] == "value_change"
        assert diff_result["changes"][0]["original"] == "5000"
        assert diff_result["changes"][0]["amended"] == "6000"

    def test_diff_summary_generation(self, amendment_tracker):
        # Test data
        changes = [
            {
                "type": "value_change",
                "path": "/test/value",
                "original": "5000",
                "amended": "6000",
            },
            {
                "type": "tag_change",
                "path": "/test/newfield",
                "original": "old",
                "amended": "new",
            },
        ]

        # Execute test
        summary = amendment_tracker._generate_diff_summary(changes)

        # Assertions
        assert summary["total_changes"] == 2
        assert summary["value_changes"] == 1
        assert summary["structure_changes"] == 1
        assert len(summary["modified_paths"]) == 2

    @pytest.mark.asyncio
    async def test_amendment_validation(self, amendment_tracker):
        # Test data with invalid changes
        invalid_amendment_data = {
            "changes": {"nonemployee_compensation": -1000}  # Invalid negative amount
        }

        # Execute test
        with pytest.raises(ValueError):
            await amendment_tracker.create_amendment("test123", invalid_amendment_data)

    @pytest.mark.asyncio
    async def test_store_amendment(self, amendment_tracker, mock_document_manager):
        # Test data
        amendment = MeFSubmission(
            id=1,
            form_type="1099_NEC",
            status=SubmissionStatus.PENDING,
            xml_content="<test>amended</test>",
        )

        # Configure mocks
        with patch.object(amendment_tracker, "document_manager", mock_document_manager):
            mock_document_manager.store_document.return_value = "doc123"

            # Execute test
            await amendment_tracker._store_amendment(amendment)

            # Assertions
            assert amendment.document_id == "doc123"
            mock_document_manager.store_document.assert_called_once_with(
                amendment.xml_content,
                f"amendment_{amendment.id}.xml",
                "application/xml",
            )
