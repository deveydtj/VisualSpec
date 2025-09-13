# AGENTS Instructions

This repository contains a small Python application.

## General Guidelines
- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines.
- Use type hints for all function signatures.
- Include docstrings for all public modules, classes, and functions.
- Keep line lengths under 88 characters.

## Required Checks
Before committing any change, run the following commands:

```bash
black .
flake8
pytest
python main.py
```

Run them from the repository root.  If a command is missing or fails, make a
best effort to explain the issue in your PR message.
