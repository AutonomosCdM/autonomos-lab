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
