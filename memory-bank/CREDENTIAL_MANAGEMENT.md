# Credential Management System

## Overview

This document outlines the credential management system for the Autonomos Lab agents, focusing on secure storage, access, and usage of API keys and tokens.

## Credential Types

The system manages several types of credentials:

1. **Slack Credentials**
   - `SLACK_BOT_TOKEN`: Used for authenticating the bot with Slack API
   - `SLACK_APP_TOKEN`: Used for Socket Mode connections
   - Alternative tokens: `ALT_SLACK_BOT_TOKEN`, `ALT_SLACK_APP_TOKEN`

2. **LLM API Credentials**
   - `SLACK_AGENT_GROQ_API_KEY`: Groq API key for the Slack agent
   - `RESEARCH_AGENT_GROQ_API_KEY`: Groq API key for the Research agent
   - Other LLM providers: `CLAUDE_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`

## Storage Location

All credentials are stored in the `.env` file at the project root. This file is:
- Excluded from version control via `.gitignore`
- Loaded automatically at runtime using `python-dotenv`
- Accessible only to authorized developers

## Credential Access

### Environment Variable Loading

Credentials are loaded into the environment using the `load_dotenv()` function:

```python
from dotenv import load_dotenv
load_dotenv()  # Loads variables from .env file
```

For explicit path loading:

```python
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(os.getcwd()) / '.env'
load_dotenv(dotenv_path=env_path)
```

### Fallback Mechanism

The system implements a fallback mechanism for credentials:

1. Primary credentials are checked first
2. If not available, alternative credentials are used
3. Clear error messages are provided if no credentials are available

Example implementation:

```python
# Attempt to get API key from multiple sources
api_key_sources = [
    os.environ.get("SLACK_AGENT_GROQ_API_KEY"),
    os.environ.get("RESEARCH_AGENT_GROQ_API_KEY"),
    os.environ.get("GROQ_API_KEY")
]

# Find the first non-None API key
api_key = next((key for key in api_key_sources if key), None)

if not api_key:
    raise ValueError("No Groq API key found")
```

## Running Agents with Credentials

### Slack Agent

To run the Slack agent:

```bash
poetry run python slack_main.py
```

The Slack agent:
- Loads credentials from `.env`
- Connects to Slack using Socket Mode
- Runs in a background thread to prevent blocking
- Logs connection details and errors to `slack_bot.log`

### Research Agent

To run the Research agent:

```bash
poetry run python research_main.py
```

## Testing with Credentials

Tests use a modified credential loading system:

1. `conftest.py` loads and validates critical environment variables
2. Tests can skip if required credentials are not available
3. Alternative credentials are used as fallbacks

## Security Best Practices

1. Never commit credentials to version control
2. Rotate credentials periodically
3. Use different credentials for development and production
4. Implement least-privilege access for all tokens
5. Log access to credentials but never log the credentials themselves

## Troubleshooting

If experiencing credential issues:

1. Verify `.env` file exists and contains required variables
2. Check log files for specific error messages
3. Ensure proper environment variable loading in the code
4. Validate tokens with respective service providers
5. Check for token expiration or revocation

## Centralized Credential Management

All credential management is centralized through:

1. The `.env` file for storage
2. The `dotenv` library for loading
3. Fallback mechanisms in code
4. Clear error handling for missing credentials

This approach ensures consistent, secure access to all required credentials across the system.
