# Agent Configuration Guide

## Overview

This document outlines the configuration and operation of the Autonomos Lab agent system, focusing on the Slack and Research agents.

## Agent Architecture

The agent system follows a modular architecture:

```
BaseAgent (core functionality)
  ↓
 / \
/   \
SlackAgent   ResearchAgent
    ↓             ↓
SlackAdapter  ResearchAdapter
```

## Base Agent Configuration

All agents inherit from the `BaseAgent` class, which provides:

1. **Core Functionality**
   - LLM interaction
   - Conversation history management
   - Error handling
   - Personality and objective definition

2. **Configuration Parameters**
   - `name`: Agent identifier
   - `personality`: Defines agent's tone and style
   - `primary_objective`: Main goal or purpose
   - `llm_model`: Language model to use (default: "llama-3.3-70b-versatile")
   - `temperature`: Creativity level (default: 0.7)

## Slack Agent

The Slack agent is configured to interact with users through Slack channels and direct messages.

### Configuration

```python
agent = BaseAgent(
    name="Slack Agent",
    personality="innovador, analítico y orientado a soluciones",
    primary_objective="Asistir al equipo de Autonomos Lab en el desarrollo de productos y servicios innovadores",
    llm_model="llama-3.3-70b-versatile",
    temperature=0.7
)

slack_adapter = SlackAdapter(
    agent=agent,
    mention_only=False,  # Respond to all messages, not just mentions
    bot_token=os.environ.get("SLACK_BOT_TOKEN"),
    app_token=os.environ.get("SLACK_APP_TOKEN")
)
```

### Running the Slack Agent

The Slack agent runs in a background thread to prevent blocking the main thread:

```python
# Start the Slack bot in a background thread
slack_adapter.start()
```

This implementation:
- Connects to Slack using Socket Mode
- Processes messages asynchronously
- Maintains conversation context
- Handles errors gracefully

## Research Agent

The Research agent is specialized for information gathering and synthesis.

### Configuration

```python
agent = BaseAgent(
    name="Research Agent",
    personality="metódico, detallado y orientado a la investigación",
    primary_objective="Recopilar y sintetizar información técnica relevante",
    llm_model="llama-3.3-70b-versatile",
    temperature=0.5  # Lower temperature for more focused responses
)
```

## Agent Interaction Flow

1. **Message Reception**
   - User sends message to agent
   - Message is processed by adapter
   - Context is maintained in conversation history

2. **Agent Processing**
   - Agent formulates response using LLM
   - Response is filtered and formatted
   - Error handling is applied if needed

3. **Response Delivery**
   - Response is sent back to user
   - Conversation history is updated
   - Interaction is logged for monitoring

## Testing Agents

Agents can be tested using the test suite:

```bash
poetry run pytest tests/
```

Tests validate:
- Agent initialization
- LLM API connections
- Response generation
- Error handling
- Conversation context preservation

## Troubleshooting

Common issues and solutions:

1. **Connection Issues**
   - Verify API credentials in `.env`
   - Check network connectivity
   - Review logs for specific errors

2. **Response Problems**
   - Adjust temperature for different response styles
   - Modify system prompt for better guidance
   - Check conversation history handling

3. **Performance Concerns**
   - Use threading for non-blocking operation
   - Implement caching for repeated queries
   - Monitor token usage and optimize prompts

## Best Practices

1. **Agent Design**
   - Define clear, focused objectives
   - Create distinctive personalities
   - Use appropriate temperature settings

2. **Prompt Engineering**
   - Be specific in system prompts
   - Provide sufficient context
   - Balance brevity and detail

3. **Error Handling**
   - Implement graceful fallbacks
   - Log errors comprehensively
   - Provide helpful error messages to users

4. **Security**
   - Validate all user inputs
   - Protect API credentials
   - Implement rate limiting

This configuration approach ensures consistent agent behavior while allowing for specialized functionality based on specific use cases.
