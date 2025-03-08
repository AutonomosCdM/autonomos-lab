# Autonomos Lab Agent Testing

## Testing Philosophy

### No Mocks Policy

This project strictly prohibits the use of mocks in testing. All tests must:
- Use real service connections
- Test actual API interactions
- Validate real-world scenarios

### Key Testing Principles

1. **Real Service Integration**
   - Every test connects to actual services
   - No simulated or fake responses
   - Validates real-world functionality

2. **Comprehensive Coverage**
   - Test agent initialization
   - Validate API connections
   - Check context handling
   - Verify response quality

## Running Tests

### Prerequisites

- All required environment variables must be set
- Active internet connection
- Valid API credentials for Groq, Slack

### Environment Variables

Required environment variables:
- `SLACK_AGENT_GROQ_API_KEY`
- `RESEARCH_AGENT_GROQ_API_KEY`
- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`

### Test Execution

```bash
# Install dependencies
poetry install

# Run all tests
poetry run pytest tests/

# Run specific agent tests
poetry run pytest tests/test_slack_agent.py
poetry run pytest tests/test_research_agent.py
```

## Test Categories

### Slack Agent Tests

- Agent initialization
- Slack adapter configuration
- API connection verification
- Interaction response validation

### Research Agent Tests

- Agent initialization
- Research-oriented interaction
- Context preservation
- API connection verification

## Troubleshooting

- Ensure all API credentials are valid
- Check network connectivity
- Verify environment variable configuration

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Main branch commits
- Scheduled intervals

## Reporting Issues

If a test fails:
1. Check API credentials
2. Verify network connection
3. Review error logs
4. Report detailed information to development team
