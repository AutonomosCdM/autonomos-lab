# Comprehensive Credential Management

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
# Comprehensive Credential Management

# Credential Recovery and Management Guide

## Overview

This document provides a comprehensive guide to recovering and managing credentials for Autonomos Lab agents.

## Credential Recovery Process

### 1. Identify Lost Credentials

If credentials have been lost or compromised:

1. Check the `.env` file in the project root
2. Verify alternative tokens in the environment
3. Use the `credential_manager.py` CLI tool to recover or set new credentials

### 2. Recovering Slack Tokens

#### Slack Bot Token
1. Go to https://api.slack.com/apps
2. Select your Slack App
3. Navigate to "OAuth & Permissions"
4. Copy the "Bot User OAuth Token"

#### Slack App Token
1. In the same Slack App settings
2. Go to "Socket Mode"
3. Generate or copy the App-Level Token

### 3. Recovering Groq API Keys

1. Visit the Groq Developer Console
2. Navigate to API Keys section
3. Generate a new API key
4. Replace the existing key in your credentials

## Using Credential Manager

### Setting Credentials

```bash
# Set Slack Bot Token
python cli/credential_manager.py set --service slack --key bot_token --value xoxb-your-token

# Set Groq API Key
python cli/credential_manager.py set --service groq --key slack_agent_key --value gsk_your_api_key
```

### Retrieving Credentials

```bash
# Get Slack Bot Token
python cli/credential_manager.py get --service slack --key bot_token

# Get Groq API Key
python cli/credential_manager.py get --service groq --key slack_agent_key
```

### Listing Stored Services

```bash
python cli/credential_manager.py list
```

### Backing Up Credentials

```bash
# Automatic backup to default location
python cli/credential_manager.py backup

# Custom backup path
python cli/credential_manager.py backup --backup-path /path/to/backup/credentials.json
```

## Best Practices

1. **Never Commit Credentials to Version Control**
   - Use `.gitignore` to exclude credential files
   - Use environment variables or secure credential management

2. **Rotate Credentials Regularly**
   - Change API keys and tokens periodically
   - Use the credential manager to update and track changes

3. **Secure Storage**
   - The credential manager stores tokens in a file with 600 permissions
   - Only the owner can read or write the credentials file

4. **Backup and Recovery**
   - Regularly backup your credentials
   - Store backups in a secure, encrypted location

## Troubleshooting

### Common Issues

1. **Missing Credentials**
   - Verify the `.env` file
   - Check alternative token sources
   - Use the credential manager to set new tokens

2. **Connection Errors**
   - Validate token permissions
   - Check network connectivity
   - Verify API endpoint status

3. **Unauthorized Access**
   - Regenerate tokens
   - Check token scopes and permissions
   - Ensure tokens are not revoked or expired

## Security Warnings

- Do not share credential files
- Use strong, unique tokens for each service
- Implement multi-factor authentication when possible
- Monitor and log credential usage

## Integration with Project

The credential manager integrates with:
- `.env` file
- Slack and Groq agent configurations
- Testing framework
- Deployment processes

By following these guidelines, you can effectively manage and recover credentials for the Autonomos Lab agent system.
