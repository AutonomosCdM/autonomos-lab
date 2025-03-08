#!/bin/bash

# Pre-deployment cleanup script for Autonomos_AiLab

# Remove log files
find . -maxdepth 1 -type f \( -name "*.log" -o -name "agent_interactions.log" \) -delete

# Remove test scripts
find . -maxdepth 1 -type f -name "test_*.py" -delete

# Remove Python bytecode cache
find . -type d -name "__pycache__" -exec rm -rf {} +

# Remove unnecessary directories
rm -rf logs/ scripts/ tools/

# Optional: Clean up temporary files
find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name "*.pyd" \) -delete

echo "Pre-deployment cleanup completed successfully."
