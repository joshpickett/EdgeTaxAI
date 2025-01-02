class TestTemplates:
    PYTEST_TEMPLATE = """
    from api.app import create_app
    import pytest
    # Test Summary:
    # {test_summary}
    
    {test_content}
    
    ### Summary of Tests
    {test_summary}
    """

    UNITTEST_TEMPLATE = """
    import unittest
    from api.app import create_app
    # Test Summary:
    # {test_summary}
    
    {test_content}
    
    ### Summary of Tests
    {test_summary}
    """

    # Add fixtures template
    PYTEST_FIXTURES = """
    @pytest.fixture
    def app():
        app = create_app()
        app.config['TESTING'] = True
        return app
        
    @pytest.fixture
    def client(app):
        return app.test_client()
    """

    @classmethod
    def get_template(cls, framework: str) -> str:
        return cls.PYTEST_TEMPLATE if framework == "pytest" else cls.UNITTEST_TEMPLATE
