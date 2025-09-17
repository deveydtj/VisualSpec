"""
CLI CSV Editor - Command-line interface for CSV editing.
Each command operates on a file directly - no state maintained between
invocations. This fixes the issue where commands couldn't access data
from previous invocations.
"""

import argparse
import sys

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


def load_and_edit(filepath: str, operation_func, *args) -> bool:
    """Load a CSV file, perform an operation, and save it back."""
    try:
        editor = CsvEditor()
        editor.load_from_csv(filepath)

        # Perform the operation
        if not operation_func(editor, *args):
            return False

        # Save the file back
        editor.save_to_csv(filepath)
        print(f"File '{filepath}' updated successfully")
        return True

    except Exception as e:
        print(f"Error processing file '{filepath}': {e}", file=sys.stderr)
        return False


def view_file(filepath: str, max_rows: int = 20, max_col_width: int = 20) -> bool:
    """Load and display a CSV file."""
    try:
        editor = CsvEditor()
        editor.load_from_csv(filepath)
        print(f"File: {filepath}")
        print(editor.view_data(max_rows, max_col_width))
        return True
    except Exception as e:
        print(f"Error viewing file '{filepath}': {e}", file=sys.stderr)
        return False


def create_new_file(filepath: str) -> bool:
    """Create a new CSV file with default headers."""
    try:
        editor = CsvEditor()
        editor.new_sheet_with_defaults(DEFAULT_HEADERS)
        editor.save_to_csv(filepath)
        print(f"Created new file '{filepath}' with default headers")
        print(f"Headers: {', '.join(DEFAULT_HEADERS)}")
        return True
    except Exception as e:
        print(f"Error creating file '{filepath}': {e}", file=sys.stderr)
        return False


# Operation functions for load_and_edit
def edit_cell_op(editor: CsvEditor, row: int, col: int, value: str) -> bool:
    """Edit a cell operation."""
    if editor.set_cell(row, col, value):
        print(f"Set cell ({row}, {col}) = '{value}'")
        return True
    else:
        print(f"Invalid cell position ({row}, {col})", file=sys.stderr)
        return False


def insert_row_op(editor: CsvEditor, row: int) -> bool:
    """Insert row operation."""
    if editor.insert_row(row):
        print(f"Inserted row at position {row}")
        return True
    else:
        print(f"Invalid row position {row}", file=sys.stderr)
        return False


def delete_row_op(editor: CsvEditor, row: int) -> bool:
    """Delete row operation."""
    if editor.remove_row(row):
        print(f"Deleted row at position {row}")
        return True
    else:
        print(f"Invalid row position {row}", file=sys.stderr)
        return False


def insert_column_op(editor: CsvEditor, col: int, header: str = "") -> bool:
    """Insert column operation."""
    if editor.insert_column(col):
        if header:
            editor.set_header(col, header)
        print(
            f"Inserted column at position {col}"
            + (f" with header '{header}'" if header else "")
        )
        return True
    else:
        print(f"Invalid column position {col}", file=sys.stderr)
        return False


def delete_column_op(editor: CsvEditor, col: int) -> bool:
    """Delete column operation."""
    if editor.remove_column(col):
        print(f"Deleted column at position {col}")
        return True
    else:
        print(f"Invalid column position {col}", file=sys.stderr)
        return False


def set_header_op(editor: CsvEditor, col: int, header: str) -> bool:
    """Set header operation."""
    if editor.set_header(col, header):
        print(f"Set header for column {col} = '{header}'")
        return True
    else:
        print(f"Invalid column position {col}", file=sys.stderr)
        return False


def clear_cell_op(editor: CsvEditor, row: int, col: int) -> bool:
    """Clear cell operation."""
    if editor.clear_cell(row, col):
        print(f"Cleared cell ({row}, {col})")
        return True
    else:
        print(f"Invalid cell position ({row}, {col})", file=sys.stderr)
        return False


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="CLI CSV Editor - Edit CSV files from command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s view data.csv                       # View CSV file
  %(prog)s edit data.csv 0 1 "New Value"      # Edit cell and save
  %(prog)s insert-row data.csv 5              # Insert row and save
  %(prog)s delete-row data.csv 3              # Delete row and save
  %(prog)s insert-col data.csv 2 "New Column" # Insert column and save
  %(prog)s delete-col data.csv 4              # Delete column and save
  %(prog)s header data.csv 1 "Updated Header" # Set header and save
  %(prog)s clear data.csv 2 3                 # Clear cell and save
  %(prog)s new output.csv                     # Create new sheet
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )

    # View command
    view_parser = subparsers.add_parser("view", help="View CSV file")
    view_parser.add_argument("file", help="CSV file to view")
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
    edit_parser = subparsers.add_parser("edit", help="Edit cell value and save file")
    edit_parser.add_argument("file", help="CSV file to edit")
    edit_parser.add_argument("row", type=int, help="Row index (0-based)")
    edit_parser.add_argument("col", type=int, help="Column index (0-based)")
    edit_parser.add_argument("value", help="New cell value")

    # Insert row command
    insert_row_parser = subparsers.add_parser(
        "insert-row", help="Insert new row and save file"
    )
    insert_row_parser.add_argument("file", help="CSV file to modify")
    insert_row_parser.add_argument(
        "row", type=int, help="Row position to insert at (0-based)"
    )

    # Delete row command
    delete_row_parser = subparsers.add_parser(
        "delete-row", help="Delete row and save file"
    )
    delete_row_parser.add_argument("file", help="CSV file to modify")
    delete_row_parser.add_argument(
        "row", type=int, help="Row index to delete (0-based)"
    )

    # Insert column command
    insert_col_parser = subparsers.add_parser(
        "insert-col", help="Insert new column and save file"
    )
    insert_col_parser.add_argument("file", help="CSV file to modify")
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
    delete_col_parser = subparsers.add_parser(
        "delete-col", help="Delete column and save file"
    )
    delete_col_parser.add_argument("file", help="CSV file to modify")
    delete_col_parser.add_argument(
        "col", type=int, help="Column index to delete (0-based)"
    )

    # Set header command
    header_parser = subparsers.add_parser(
        "header", help="Set column header and save file"
    )
    header_parser.add_argument("file", help="CSV file to modify")
    header_parser.add_argument("col", type=int, help="Column index (0-based)")
    header_parser.add_argument("header", help="New header text")

    # Clear cell command
    clear_parser = subparsers.add_parser(
        "clear", help="Clear cell and save file"
    )
    clear_parser.add_argument("file", help="CSV file to modify")
    clear_parser.add_argument("row", type=int, help="Row index (0-based)")
    clear_parser.add_argument("col", type=int, help="Column index (0-based)")

    # New sheet command
    new_parser = subparsers.add_parser(
        "new", help="Create new CSV file with default headers"
    )
    new_parser.add_argument("file", help="CSV file to create")

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute the requested command
    try:
        if args.command == "view":
            if not view_file(args.file, args.rows, args.width):
                return 1

        elif args.command == "edit":
            if not load_and_edit(
                args.file, edit_cell_op, args.row, args.col, args.value
            ):
                return 1

        elif args.command == "insert-row":
            if not load_and_edit(args.file, insert_row_op, args.row):
                return 1

        elif args.command == "delete-row":
            if not load_and_edit(args.file, delete_row_op, args.row):
                return 1

        elif args.command == "insert-col":
            if not load_and_edit(args.file, insert_column_op, args.col, args.header):
                return 1

        elif args.command == "delete-col":
            if not load_and_edit(args.file, delete_column_op, args.col):
                return 1

        elif args.command == "header":
            if not load_and_edit(args.file, set_header_op, args.col, args.header):
                return 1

        elif args.command == "clear":
            if not load_and_edit(args.file, clear_cell_op, args.row, args.col):
                return 1

        elif args.command == "new":
            if not create_new_file(args.file):
                return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

