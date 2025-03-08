#!/usr/bin/env python
"""
Wrapper script to run the main application with warnings suppressed.
This script sets up warning filters before importing any other modules.
"""
import os
import sys
import warnings

# Completely disable all warnings
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

# Monkey patch the warnings module to ensure no warnings are shown
original_warn = warnings.warn
warnings.warn = lambda *args, **kwargs: None

# Disable specific LangChain deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*langchain.*")
warnings.filterwarnings("ignore", message=".*pydantic.*")

# Run the main script
if __name__ == "__main__":
    # Import main only after setting up warning filters
    import main
    main.main()
