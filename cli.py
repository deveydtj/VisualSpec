"""
CLI CSV Editor - Command-line interface for CSV editing.
Provides full CSV editing functionality through command line.
"""

import argparse
import sys
from typing import Optional

from csv_editor import CsvEditor


# Default columns tailored to the original workflow
DEFAULT_HEADERS = [
    "Type Parent Requirement",
    "ID",
    "Name",
    "Text",
    "Traced To",
    "Verified By",
    "Class",
    "Story",
]


class CsvCLI:
    """Command-line interface for CSV editing operations."""

    def __init__(self):
        self.editor = CsvEditor()
        self.current_file: Optional[str] = None

    def load_file(self, filepath: str) -> bool:
        """Load a CSV file."""
        try:
            self.editor.load_from_csv(filepath)
            self.current_file = filepath
            print(f"Loaded: {filepath}")
            print(
                f"Data: {self.editor.row_count()} rows, "
                f"{self.editor.column_count()} columns"
            )
            return True
        except Exception as e:
            print(f"Error loading file: {e}", file=sys.stderr)
            return False

    def save_file(self, filepath: Optional[str] = None) -> bool:
        """Save current data to CSV file."""
        target_file = filepath or self.current_file
        if not target_file:
            print("No file specified and no current file loaded.", file=sys.stderr)
            return False

        try:
            self.editor.save_to_csv(target_file)
            self.current_file = target_file
            print(f"Saved: {target_file}")
            return True
        except Exception as e:
            print(f"Error saving file: {e}", file=sys.stderr)
            return False

    def view_data(self, max_rows: int = 20, max_col_width: int = 20) -> None:
        """Display current data in tabular format."""
        print(self.editor.view_data(max_rows, max_col_width))

    def edit_cell(self, row: int, col: int, value: str) -> bool:
        """Edit a specific cell."""
        if self.editor.set_cell(row, col, value):
            print(f"Set cell ({row}, {col}) = '{value}'")
            return True
        else:
            print(f"Invalid cell position ({row}, {col})", file=sys.stderr)
            return False

    def insert_row(self, row: int) -> bool:
        """Insert a new row at specified position."""
        if self.editor.insert_row(row):
            print(f"Inserted row at position {row}")
            return True
        else:
            print(f"Invalid row position {row}", file=sys.stderr)
            return False

    def delete_row(self, row: int) -> bool:
        """Delete row at specified position."""
        if self.editor.remove_row(row):
            print(f"Deleted row at position {row}")
            return True
        else:
            print(f"Invalid row position {row}", file=sys.stderr)
            return False

    def insert_column(self, col: int, header: str = "") -> bool:
        """Insert a new column at specified position."""
        if self.editor.insert_column(col):
            if header:
                self.editor.set_header(col, header)
            print(
                f"Inserted column at position {col}"
                + (f" with header '{header}'" if header else "")
            )
            return True
        else:
            print(f"Invalid column position {col}", file=sys.stderr)
            return False

    def delete_column(self, col: int) -> bool:
        """Delete column at specified position."""
        if self.editor.remove_column(col):
            print(f"Deleted column at position {col}")
            return True
        else:
            print(f"Invalid column position {col}", file=sys.stderr)
            return False

    def set_header(self, col: int, header: str) -> bool:
        """Set header for specified column."""
        if self.editor.set_header(col, header):
            print(f"Set header for column {col} = '{header}'")
            return True
        else:
            print(f"Invalid column position {col}", file=sys.stderr)
            return False

    def clear_cell(self, row: int, col: int) -> bool:
        """Clear cell at specified position."""
        if self.editor.clear_cell(row, col):
            print(f"Cleared cell ({row}, {col})")
            return True
        else:
            print(f"Invalid cell position ({row}, {col})", file=sys.stderr)
            return False

    def new_sheet(self) -> None:
        """Create new sheet with default headers."""
        self.editor.new_sheet_with_defaults(DEFAULT_HEADERS)
        self.current_file = None
        print("Created new sheet with default headers")
        print(f"Headers: {', '.join(DEFAULT_HEADERS)}")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="CLI CSV Editor - Edit CSV files from command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s load data.csv                    # Load CSV file
  %(prog)s view                             # View loaded data
  %(prog)s edit 0 1 "New Value"             # Edit cell at row 0, col 1
  %(prog)s insert-row 5                     # Insert row at position 5
  %(prog)s delete-row 3                     # Delete row 3
  %(prog)s insert-col 2 "New Column"        # Insert column at position 2
  %(prog)s delete-col 4                     # Delete column 4
  %(prog)s header 1 "Updated Header"        # Set header for column 1
  %(prog)s clear 2 3                        # Clear cell at row 2, col 3
  %(prog)s save output.csv                  # Save to file
  %(prog)s new                              # Create new sheet
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Load command
    load_parser = subparsers.add_parser("load", help="Load CSV file")
    load_parser.add_argument("file", help="CSV file to load")

    # Save command
    save_parser = subparsers.add_parser("save", help="Save CSV file")
    save_parser.add_argument(
        "file",
        nargs="?",
        help="CSV file to save (uses current file if not specified)",
    )

    # View command
    view_parser = subparsers.add_parser("view", help="View current data")
    view_parser.add_argument(
        "--rows",
        type=int,
        default=20,
        help="Maximum rows to display (default: 20)",
    )
    view_parser.add_argument(
        "--width",
        type=int,
        default=20,
        help="Maximum column width (default: 20)",
    )

    # Edit command
    edit_parser = subparsers.add_parser("edit", help="Edit cell value")
    edit_parser.add_argument("row", type=int, help="Row index (0-based)")
    edit_parser.add_argument("col", type=int, help="Column index (0-based)")
    edit_parser.add_argument("value", help="New cell value")

    # Insert row command
    insert_row_parser = subparsers.add_parser("insert-row", help="Insert new row")
    insert_row_parser.add_argument(
        "row", type=int, help="Row position to insert at (0-based)"
    )

    # Delete row command
    delete_row_parser = subparsers.add_parser("delete-row", help="Delete row")
    delete_row_parser.add_argument(
        "row", type=int, help="Row index to delete (0-based)"
    )

    # Insert column command
    insert_col_parser = subparsers.add_parser("insert-col", help="Insert new column")
    insert_col_parser.add_argument(
        "col", type=int, help="Column position to insert at (0-based)"
    )
    insert_col_parser.add_argument(
        "header",
        nargs="?",
        default="",
        help="Optional header for new column",
    )

    # Delete column command
    delete_col_parser = subparsers.add_parser("delete-col", help="Delete column")
    delete_col_parser.add_argument(
        "col", type=int, help="Column index to delete (0-based)"
    )

    # Set header command
    header_parser = subparsers.add_parser("header", help="Set column header")
    header_parser.add_argument("col", type=int, help="Column index (0-based)")
    header_parser.add_argument("header", help="New header text")

    # Clear cell command
    clear_parser = subparsers.add_parser("clear", help="Clear cell")
    clear_parser.add_argument("row", type=int, help="Row index (0-based)")
    clear_parser.add_argument("col", type=int, help="Column index (0-based)")

    # New sheet command
    subparsers.add_parser("new", help="Create new sheet with default headers")

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    cli = CsvCLI()

    # Execute the requested command
    try:
        if args.command == "load":
            if not cli.load_file(args.file):
                return 1

        elif args.command == "save":
            if not cli.save_file(args.file):
                return 1

        elif args.command == "view":
            cli.view_data(args.rows, args.width)

        elif args.command == "edit":
            if not cli.edit_cell(args.row, args.col, args.value):
                return 1

        elif args.command == "insert-row":
            if not cli.insert_row(args.row):
                return 1

        elif args.command == "delete-row":
            if not cli.delete_row(args.row):
                return 1

        elif args.command == "insert-col":
            if not cli.insert_column(args.col, args.header):
                return 1

        elif args.command == "delete-col":
            if not cli.delete_column(args.col):
                return 1

        elif args.command == "header":
            if not cli.set_header(args.col, args.header):
                return 1

        elif args.command == "clear":
            if not cli.clear_cell(args.row, args.col):
                return 1

        elif args.command == "new":
            cli.new_sheet()

    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
