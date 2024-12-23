class TestTemplates:
    PYTEST_TEMPLATE = """
    # Test Summary:
    # {test_summary}
    
    import pytest{imports}
    
    {test_content}
    
    ### Summary of Tests
    {test_summary}
    """
    
    UNITTEST_TEMPLATE = """
    # Test Summary:
    # {test_summary}
    
    import unittest{imports}
    
    {test_content}
    
    ### Summary of Tests
    {test_summary}
    """
    
    @classmethod
    def get_template(cls, framework: str) -> str:
        return cls.PYTEST_TEMPLATE if framework == "pytest" else cls.UNITTEST_TEMPLATE
