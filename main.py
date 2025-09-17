"""
CSV Editor - Main entry point for CSV editing with CLI and GUI modes.

This is a complete refactor from the original PyQt5 GUI application to a
command-line interface using only standard library modules. Now includes
an optional Tkinter GUI mode.
"""

import sys
from cli import main

if __name__ == "__main__":
    # Check for GUI flag
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        try:
            from gui import launch_gui

            sys.exit(launch_gui())
        except ImportError as e:
            print(f"Error: Could not import GUI module: {e}", file=sys.stderr)
            print(
                "Tkinter may not be available on this system.", file=sys.stderr
            )
            sys.exit(1)
    else:
        sys.exit(main())
