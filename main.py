"""
CLI CSV Editor - Main entry point for command-line CSV editing.

This is a complete refactor from the original PyQt5 GUI application to a
command-line interface using only standard library modules.
"""

import sys
from cli import main

if __name__ == "__main__":
    sys.exit(main())
