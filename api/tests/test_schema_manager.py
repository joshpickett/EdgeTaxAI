import pytest
from unittest.mock import Mock, patch
from api.services.mef.schema_manager import SchemaManager
from lxml import etree


@pytest.fixture
def schema_manager():
    return SchemaManager()


class TestSchemaManager:

    def test_schema_loading(self, schema_manager):
        # Assert schemas were loaded
        assert len(schema_manager.schema_cache) > 0

        # Check specific schemas
        assert "1099_NEC" in schema_manager.schema_cache
        assert "1099_K" in schema_manager.schema_cache

    def test_schema_validation(self, schema_manager):
        # Test data
        valid_xml = """
            <?xml version="1.0" encoding="UTF-8"?>
            <Form1099NEC>
                <PayerName>Test Corp</PayerName>
                <RecipientName>John Doe</RecipientName>
                <NonemployeeCompensation>5000.00</NonemployeeCompensation>
            </Form1099NEC>
        """

        # Execute test
        result = schema_manager.validate_schema(valid_xml, "1099_NEC")

        # Assertions
        assert result["is_valid"] is True
        assert result["errors"] is None

    def test_invalid_schema(self, schema_manager):
        # Test data
        invalid_xml = """
            <?xml version="1.0" encoding="UTF-8"?>
            <Form1099NEC>
                <InvalidTag>Test</InvalidTag>
            </Form1099NEC>
        """

        # Execute test
        result = schema_manager.validate_schema(invalid_xml, "1099_NEC")

        # Assertions
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    def test_version_detection(self, schema_manager):
        # Test data
        test_xml = """
            <?xml version="1.0" encoding="UTF-8"?>
            <Form1099NEC xmlns="http://www.irs.gov/efile/1099nec/2023">
                <PayerName>Test Corp</PayerName>
            </Form1099NEC>
        """

        # Execute test
        version_info = schema_manager.detect_version(test_xml)
        # Assertions
        assert version_info["version"] == "2023"
        assert version_info["form_type"] == "1099NEC"

    def test_backward_compatibility(self, schema_manager):
        # Test data with older version
        old_version_xml = """
            <?xml version="1.0" encoding="UTF-8"?>
            <Form1099NEC xmlns="http://www.irs.gov/efile/1099nec/2022">
                <PayerName>Test Corp</PayerName>
                <RecipientName>John Doe</RecipientName>
            </Form1099NEC>
        """

        # Execute test
        result = schema_manager.validate_schema(
            old_version_xml, "1099_NEC", version="2022"
        )

        # Assertions
        assert result["is_valid"] is True

    def test_form_type_detection(self, schema_manager):
        # Test various form types
        test_cases = [
            ("<Form1099NEC>", "1099NEC"),
            ("<Form1099K>", "1099K"),
            ("<Form1040>", "1040"),
            ("<ScheduleC>", "SCHEDULE_C"),
            ("<UnknownForm>", "UNKNOWN"),
        ]

        for xml, expected_type in test_cases:
            root = etree.fromstring(xml)
            detected_type = schema_manager._detect_form_type(root)
            assert detected_type == expected_type
