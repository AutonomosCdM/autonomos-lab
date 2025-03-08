#!/bin/bash
set -e

# Function to retry the main application
run_app() {
    max_retries=5
    retry_count=0

    while [ $retry_count -lt $max_retries ]; do
        poetry run python slack_main.py
        exit_code=$?

        # Check if exit was due to a known reconnection issue
        if [ $exit_code -eq 0 ] || [ $exit_code -eq 137 ]; then
            echo "Application exited cleanly or due to memory pressure. Restarting..."
            retry_count=$((retry_count + 1))
            sleep 10
        else
            echo "Application crashed with exit code $exit_code. Attempting restart..."
            retry_count=$((retry_count + 1))
            sleep 30
        fi
    done

    echo "Max retries reached. Exiting."
    exit 1
}

# Run the application with retry mechanism
run_app
