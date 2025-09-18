"""
CSV Editor - GUI application for editing CSV files.

A Tkinter-based GUI application for comprehensive CSV editing functionality
using only Python standard library modules.
"""

import sys

if __name__ == "__main__":
    try:
        from gui import launch_gui

        sys.exit(launch_gui())
    except ImportError as e:
        print(f"Error: Could not import GUI module: {e}", file=sys.stderr)
        print(
            "Tkinter may not be available on this system.", file=sys.stderr
        )
        sys.exit(1)
