# Commit Message Validation

## Purpose

This script validates commit messages to ensure consistency and clarity across the Autonomos Lab project.

## Validation Rules

### Commit Message Structure

```
<type>(<scope>): <short description>

[Optional body]

[Optional footer]
```

### Types

- `feat`: New feature or functionality
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting changes (no code logic)
- `refactor`: Code restructuring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: Continuous integration changes
- `build`: Build system changes
- `revert`: Reverting previous changes

### Scopes

- `agent`: Agent-related changes
- `slack`: Slack integration modifications
- `llm`: Language model changes
- `core`: Core system modifications
- `config`: Configuration updates
- `deps`: Dependency management

## Examples of Valid Commit Messages

### Feature Addition

```
feat(slack): Implement app_mention event handling

- Add support for Slack app_mention events
- Develop specific handler for mentions
- Improve conversation context management

Closes #123
```

### Bug Fix

```
fix(agent): Correct token management in response generation

- Optimize token consumption in LLM
- Implement context truncation strategy
- Improve response generation precision

Resolves #456
```

### Documentation Update

```
docs(memory-bank): Update agent implementation documentation

- Add details about Slack agent architecture
- Document Socket Mode implementation
- Include information about agent personalities
```

## Validation Checks

1. Commit message must follow the `<type>(<scope>): <description>` format
2. First line must be 72 characters or less
3. Second line must be blank if a body is present
4. Types and scopes are restricted to predefined lists

## Installation

1. Ensure Python 3.7+ is installed
2. Install pre-commit: `pip install pre-commit`
3. Run `pre-commit install --hook-type commit-msg`

## Troubleshooting

- If commit validation fails, review the error message
- Adjust your commit message to match the specified format
- Consult the `COMMIT_FORMAT.md` in the memory-bank directory for detailed guidelines

## Last Updated

**Date**: 3/7/2025
**Time**: 18:14 (America/Santiago)
