class TestTemplates:
    PYTEST_TEMPLATE = """
    \"\"\"
    {feature_description}
    
    Generated on: {generation_date}
    Source file: {source_file}
    \"\"\"
    
    import pytest
    {imports}
    
    {test_content}
    
    ### Summary of Tests
    {test_summary}
    """
    
    UNITTEST_TEMPLATE = """
    \"\"\"
    {feature_description}
    
    Generated on: {generation_date}
    Source file: {source_file}
    \"\"\"
    
    import unittest
    {imports}
    
    {test_content}
    
    ### Summary of Tests
    {test_summary}
    """
    
    @classmethod
    def get_template(cls, framework: str) -> str:
        return cls.PYTEST_TEMPLATE if framework == "pytest" else cls.UNITTEST_TEMPLATE
