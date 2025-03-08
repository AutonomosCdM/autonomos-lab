#!/usr/bin/env python3
import re
import sys

def validate_commit_message(message):
    # Remove comments from commit message
    message = '\n'.join([line for line in message.splitlines() if not line.startswith('#')])
    
    # Commit message types
    types = ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'perf', 'ci', 'build', 'revert']
    
    # Scopes (can be extended as needed)
    scopes = ['agent', 'slack', 'llm', 'core', 'config', 'deps']
    
    # Regex pattern for commit message
    pattern = r'^({types})(\({scopes}\))?: .+$'.format(
        types='|'.join(types),
        scopes='|'.join(scopes)
    )
    
    # Split message into lines
    lines = message.splitlines()
    
    # Check first line
    if not lines:
        print("Error: Commit message is empty")
        return False
    
    # Validate first line format
    if not re.match(pattern, lines[0]):
        print("""Error: Invalid commit message format
        
Correct format: <type>(<scope>): <short description>

Types: {}
Scopes: {}

Examples:
- feat(slack): Implement app_mention event handling
- fix(agent): Correct token management in response generation
- docs(memory-bank): Update agent implementation documentation""".format(
            ', '.join(types),
            ', '.join(scopes)
        ))
        return False
    
    # Check first line length
    if len(lines[0]) > 72:
        print("Error: First line should be 72 characters or less")
        return False
    
    # Optional: Check body formatting if present
    if len(lines) > 1:
        # Ensure second line is blank if body exists
        if lines[1].strip():
            print("Error: Second line must be blank if body is present")
            return False
    
    return True

def main():
    # Read commit message from file
    commit_msg_filepath = sys.argv[1]
    with open(commit_msg_filepath, 'r') as f:
        message = f.read()
    
    # Validate message
    if not validate_commit_message(message):
        sys.exit(1)
    
    # If validation passes, exit successfully
    sys.exit(0)

if __name__ == "__main__":
    main()
