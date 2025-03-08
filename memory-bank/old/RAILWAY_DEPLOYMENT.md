# HackathonAgents Railway Deployment Guide

## Project Overview
HackathonAgents is a Slack-integrated AI agent system built with Python, leveraging LangChain and LlamaIndex for advanced conversational capabilities.

## Deployment Configuration

### 1. Dockerfile
The Dockerfile is configured to:
- Use Python 3.10 slim image
- Install Poetry and project dependencies
- Set up persistent storage directories
- Configure logging
- Expose port 8000 for health checks
- Use an entrypoint script for robust startup

### 2. Railway Configuration
- Uses Dockerfile for build process
- Implements automatic restart policy
- Provides a health check endpoint at `/health`

### 3. Environment Variables
Required environment variables:
- `SLACK_BOT_TOKEN`: Slack Bot OAuth Token
- `SLACK_APP_TOKEN`: Slack App-Level Token
- `GROQ_API_KEY`: API key for Groq (if used)

### 4. Deployment Workflow
- Continuous Integration via GitHub Actions
- Automatic deployment to Railway on push to main branch
- Runs tests before deployment
- Supports automatic restarts and reconnections

## Persistent Storage
- `/app/data/indices`: Vector index storage
- `/app/data/embeddings`: Embedding cache
- `/app/logs`: Application logs

## Health Checks
The application provides a `/health` endpoint that returns:
- Current status
- Agent version
- Slack connection status

## Recommended Railway Setup
1. Create a new Railway project
2. Link GitHub repository
3. Set environment variables in Railway dashboard
4. Configure deployment settings

## Troubleshooting
- Check logs in Railway dashboard
- Verify Slack tokens are correctly set
- Ensure all required dependencies are installed

## Local Development
```bash
# Install dependencies
poetry install

# Run the Slack bot
poetry run python slack_main.py
```

## Deployment Checklist
- [ ] Set Slack Bot and App tokens
- [ ] Configure environment variables
- [ ] Verify GitHub Actions workflow
- [ ] Check Railway deployment settings
