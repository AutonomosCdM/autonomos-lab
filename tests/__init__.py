# Pytest configuration and test utilities
import pytest

def pytest_configure(config):
    """
    Configure pytest settings for the project
    """
    config.addinivalue_line(
        "markers", 
        "unit: mark a test as a unit test for the HackathonAgents project"
    )
    config.addinivalue_line(
        "markers", 
        "integration: mark a test as an integration test for the HackathonAgents project"
    )
