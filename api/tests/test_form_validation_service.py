import pytest
from api.services.form.form_validation_service import FormValidationService
from api.services.validation.real_time_validator import RealTimeValidator


class TestFormValidationService:
    @pytest.fixture
    def validation_service(self):
        return FormValidationService()

    async def test_validate_section(self, validation_service):
        # Test data
        form_type = "1040"
        section = "income"
        data = {"wages": 50000, "interest": 1000, "dividends": 500}

        result = await validation_service.validate_section(form_type, section, data)
        assert result["is_valid"] == True
        assert len(result["errors"]) == 0

    async def test_validate_field(self, validation_service):
        result = await validation_service.validate_field(
            "1040", "social_security_number", "123-45-6789"
        )
        assert result["is_valid"] == True
        assert len(result["errors"]) == 0

    async def test_validate_dependencies(self, validation_service):
        data = {"has_dependents": True, "dependent_count": 2}
        result = await validation_service.validate_dependencies("1040", data)
        assert result["is_valid"] == True
