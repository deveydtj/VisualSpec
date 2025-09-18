"""
CSV Editor - Core functionality for CSV manipulation.
Provides CSV editing functionality without external dependencies.
"""

import csv
from typing import List, Optional


class CsvEditor:
    """
    Pure Python CSV editor with core functionality:
    - Load/save CSV files
    - View data in tabular format
    - Edit cells, insert/delete rows and columns
    - Support for custom headers
    """

    def __init__(
        self,
        data: Optional[List[List[str]]] = None,
        headers: Optional[List[str]] = None,
    ):
        """Initialize CSV editor with optional data and headers."""
        self._data = data if data is not None else []
        self._headers = headers if headers is not None else []

    def row_count(self) -> int:
        """Return number of data rows."""
        return len(self._data)

    def column_count(self) -> int:
        """Return number of columns."""
        if self._headers:
            return len(self._headers)
        return len(self._data[0]) if self._data else 0

    def get_cell(self, row: int, col: int) -> str:
        """Get value at specified row and column."""
        if row < 0 or row >= len(self._data):
            return ""
        if col < 0 or col >= len(self._data[row]):
            return ""
        return self._data[row][col]

    def set_cell(self, row: int, col: int, value: str) -> bool:
        """Set value at specified row and column."""
        if row < 0 or row >= len(self._data):
            return False

        # Ensure the row has enough columns
        while col >= len(self._data[row]):
            self._data[row].append("")

        self._data[row][col] = value
        return True

    def get_header(self, col: int) -> str:
        """Get header for specified column."""
        if self._headers and col < len(self._headers):
            return self._headers[col]
        return f"Column {col + 1}"

    def set_header(self, col: int, value: str) -> bool:
        """Set header for specified column."""
        # Grow headers list if needed
        if col >= len(self._headers):
            self._headers += [""] * (col - len(self._headers) + 1)
        self._headers[col] = value
        return True

    def insert_row(self, row: int, count: int = 1) -> bool:
        """Insert empty rows at specified position."""
        if row < 0 or row > len(self._data):
            return False

        cols = self.column_count()
        for _ in range(count):
            self._data.insert(row, [""] * cols)
        return True

    def remove_row(self, row: int, count: int = 1) -> bool:
        """Remove rows at specified position."""
        if row < 0 or row >= len(self._data):
            return False

        for _ in range(count):
            if row < len(self._data):
                self._data.pop(row)
        return True

    def insert_column(self, col: int, count: int = 1) -> bool:
        """Insert empty columns at specified position."""
        if col < 0:
            return False

        # Ensure headers exist
        if not self._headers:
            self._headers = [""] * self.column_count()

        # Insert headers
        for _ in range(count):
            self._headers.insert(col, "")

        # Insert into each row
        for r in range(len(self._data)):
            for _ in range(count):
                self._data[r].insert(col, "")

        return True

    def remove_column(self, col: int, count: int = 1) -> bool:
        """Remove columns at specified position."""
        if col < 0:
            return False

        for _ in range(count):
            if self._headers and col < len(self._headers):
                self._headers.pop(col)
            for r in range(len(self._data)):
                if col < len(self._data[r]):
                    self._data[r].pop(col)
        return True

    def clear_cell(self, row: int, col: int) -> bool:
        """Clear cell at specified position."""
        return self.set_cell(row, col, "")

    def load_from_csv(self, path: str) -> None:
        """Load data from CSV file."""
        with open(path, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            rows = [[]]

        headers = rows[0]
        data = rows[1:]

        # Normalize lengths
        max_cols = (
            max([len(headers)] + [len(r) for r in data]) if data else len(headers)
        )
        headers += [""] * (max_cols - len(headers))
        for i in range(len(data)):
            data[i] += [""] * (max_cols - len(data[i]))

        self._headers = headers
        self._data = data

    def save_to_csv(self, path: str, column_order: Optional[List[int]] = None) -> None:
        """
        Save data to CSV file.

        Args:
            path: File path to save to
            column_order: Optional list of column indices for custom ordering
        """
        max_cols = (
            max([len(self._headers)] + [len(r) for r in self._data])
            if self._data
            else len(self._headers)
        )
        headers = self._headers + [""] * (max_cols - len(self._headers))
        rows = [r + [""] * (max_cols - len(r)) for r in self._data]

        if column_order:
            headers = [headers[i] for i in column_order]
            rows = [[row[i] for i in column_order] for row in rows]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

    def view_data(self, max_rows: int = 20, max_col_width: int = 20) -> str:
        """Return a formatted string view of the data."""
        if not self._data and not self._headers:
            return "No data loaded."

        # Prepare headers
        headers = []
        for i in range(self.column_count()):
            header = self.get_header(i)
            if len(header) > max_col_width:
                header = header[: max_col_width - 3] + "..."
            headers.append(header)

        # Prepare data rows
        display_rows = []
        row_limit = min(max_rows, self.row_count())

        for r in range(row_limit):
            row = []
            for c in range(self.column_count()):
                cell = self.get_cell(r, c)
                if len(cell) > max_col_width:
                    cell = cell[: max_col_width - 3] + "..."
                row.append(cell)
            display_rows.append(row)

        # Calculate column widths
        col_widths = []
        for c in range(self.column_count()):
            width = max(
                len(headers[c]) if c < len(headers) else 0,
                (
                    max(len(row[c]) for row in display_rows)
                    if display_rows and c < len(display_rows[0])
                    else 0
                ),
            )
            col_widths.append(min(width, max_col_width))

        # Format output
        lines = []

        # Header line
        header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
        lines.append(header_line)
        lines.append("-" * len(header_line))

        # Data lines
        for row in display_rows:
            data_line = " | ".join(
                cell.ljust(col_widths[i]) for i, cell in enumerate(row)
            )
            lines.append(data_line)

        # Add summary
        if self.row_count() > max_rows:
            lines.append(f"... ({self.row_count() - max_rows} more rows)")

        lines.append(f"\nTotal: {self.row_count()} rows, {self.column_count()} columns")

        return "\n".join(lines)

    def new_sheet_with_defaults(self, default_headers: List[str]) -> None:
        """Create a new sheet with default headers."""
        self._headers = default_headers[:]
        self._data = []
