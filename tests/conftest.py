import pytest
import os
from dotenv import load_dotenv

def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest file
    after command line options have been parsed.
    """
    # Load environment variables for all tests
    load_dotenv()

def pytest_runtest_setup(item):
    """
    Called before running a test to perform any necessary setup.
    Validates and sets critical environment variables before each test.
    """
    # Critical environment variables with fallback to alternative tokens
    critical_vars_mapping = {
        "SLACK_BOT_TOKEN": "ALT_SLACK_BOT_TOKEN",
        "SLACK_APP_TOKEN": "ALT_SLACK_APP_TOKEN",
        "SLACK_AGENT_GROQ_API_KEY": "RESEARCH_AGENT_GROQ_API_KEY",
        "RESEARCH_AGENT_GROQ_API_KEY": "SLACK_AGENT_GROQ_API_KEY"
    }
    
    for primary_var, fallback_var in critical_vars_mapping.items():
        # If primary variable is not set, try to use the fallback
        if not os.environ.get(primary_var):
            fallback_value = os.environ.get(fallback_var)
            if fallback_value:
                os.environ[primary_var] = fallback_value
            else:
                raise AssertionError(f"Critical environment variable {primary_var} is not set and no fallback available")

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Called after test run to provide additional summary information.
    """
    terminalreporter.write_line("\n--- Autonomos Lab Agent Testing Summary ---")
    terminalreporter.write_line("Tested Agents:")
    terminalreporter.write_line("1. Slack Agent")
    terminalreporter.write_line("2. Research Agent")
    terminalreporter.write_line("\nTesting Principles:")
    terminalreporter.write_line("- No mocks used")
    terminalreporter.write_line("- Real service integration")
    terminalreporter.write_line("- Comprehensive context testing")
