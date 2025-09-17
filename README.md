# CSV Editor

A command-line and GUI interface for editing CSV files using only Python standard library modules. This tool provides comprehensive CSV editing functionality without requiring any external dependencies.

## Features

- **Load and save CSV files** with proper encoding support
- **View data** in formatted table layout (CLI) or interactive grid (GUI)
- **Edit individual cells** with validation
- **Insert and delete rows and columns** at any position
- **Manage headers** including renaming and adding new columns
- **Clear cells** to remove unwanted data
- **Create new sheets** with default headers
- **Standard library only** - no external dependencies required
- **GUI Mode** - Optional Tkinter-based graphical interface

## Installation

No installation required! Just run the Python scripts directly since they only use standard library modules.

## Usage

### GUI Mode

Launch the graphical interface:

```bash
python main.py --gui
```

The GUI provides:
- **File Menu**: New, Open, Save, Save As, Exit
- **Edit Menu**: Insert/delete rows and columns, clear cells
- **Interactive Grid**: Double-click cells to edit, click headers to rename
- **Toolbar**: Quick access to common operations
- **Keyboard Shortcuts**: Ctrl+N (New), Ctrl+O (Open), Ctrl+S (Save)

**GUI Requirements:**
- Python 3.6.5+ with Tkinter support (included in most Python installations)
- Tkinter is part of the Python standard library on most systems

### Command Line Mode

Run `python main.py --help` to see all available commands:

```bash
python main.py <command> [arguments]
```

### Commands Overview

| Command | Description | Example |
|---------|-------------|---------|
| `view` | View CSV file | `python main.py view data.csv` |
| `edit` | Edit cell and save | `python main.py edit data.csv 0 1 "New Value"` |
| `insert-row` | Insert row and save | `python main.py insert-row data.csv 5` |
| `delete-row` | Delete row and save | `python main.py delete-row data.csv 3` |
| `insert-col` | Insert column and save | `python main.py insert-col data.csv 2 "Header"` |
| `delete-col` | Delete column and save | `python main.py delete-col data.csv 4` |
| `header` | Set header and save | `python main.py header data.csv 1 "New Header"` |
| `clear` | Clear cell and save | `python main.py clear data.csv 2 3` |
| `new` | Create new CSV file | `python main.py new output.csv` |

### Detailed Examples

#### Loading and Viewing Data
```bash
# View a CSV file directly
python main.py view data.csv

# View more rows and adjust column width
python main.py view data.csv --rows 50 --width 30
```

#### Editing Data
```bash
# Edit cell at row 0, column 1 and save the file
python main.py edit data.csv 0 1 "Updated Value"

# Clear a cell and save the file
python main.py clear data.csv 2 3

# Set header for column 0 and save the file
python main.py header data.csv 0 "Customer Name"
```

#### Adding and Removing Data
```bash
# Insert a new row at position 5 and save
python main.py insert-row data.csv 5

# Delete row 3 and save
python main.py delete-row data.csv 3

# Insert new column at position 2 with header and save
python main.py insert-col data.csv 2 "New Column"

# Delete column 4 and save
python main.py delete-col data.csv 4
```

#### Working with Files
```bash
# Create a new CSV file with default headers
python main.py new requirements.csv
```

### Default Headers

When creating a new sheet, the following default headers are used:
- Type Parent Requirement
- ID
- Name  
- Text
- Traced To
- Verified By
- Class
- Story

These headers are tailored for requirement tracking workflows but can be modified using the `header` command.

### Data Format

- **CSV files** are loaded with UTF-8 encoding with BOM support
- **Row/column indices** are 0-based (first row is 0, first column is 0)
- **Empty cells** are represented as empty strings
- **Multi-line text** is supported in cells
- **Automatic normalization** ensures all rows have the same number of columns

### Examples Workflow

```bash
# 1. Create a new CSV file
python main.py new requirements.csv

# 2. View the file (shows headers only initially)
python main.py view requirements.csv

# 3. Add a row and edit specific cells
python main.py insert-row requirements.csv 0
python main.py edit requirements.csv 0 0 "REQ-001"
python main.py edit requirements.csv 0 1 "001"
python main.py edit requirements.csv 0 2 "User Login Requirement"
python main.py edit requirements.csv 0 3 "System shall allow users to login"

# 4. Add priority column
python main.py insert-col requirements.csv 8 "Priority"
python main.py edit requirements.csv 0 8 "High"

# 5. View final result
python main.py view requirements.csv
```

### Programming Interface

You can also use the CSV editor programmatically:

```python
from csv_editor import CsvEditor

# Create editor instance
editor = CsvEditor()

# Load data
editor.load_from_csv('data.csv')

# Edit data
editor.set_cell(0, 1, 'New Value')
editor.insert_row(5)
editor.insert_column(3, 'New Column')

# View data
print(editor.view_data())

# Save data
editor.save_to_csv('output.csv')
```

## Development

### Requirements
- Python 3.6+ (tested with Python 3.12)
- Standard library only - no external dependencies

### Code Quality
Before committing changes, run these commands:

```bash
black .          # Format code
flake8           # Lint code  
pytest           # Run tests (if any)
python main.py   # Test CLI functionality
```

### File Structure
- `main.py` - Main entry point (CLI and GUI modes)
- `cli.py` - Command-line interface implementation
- `csv_editor.py` - Core CSV editing functionality
- `gui.py` - Tkinter GUI implementation

## Migration from Original GUI Version

This tool is a complete refactor from the original PyQt5-based GUI application. The new version provides both CLI and GUI modes:

### CLI Mode Features:
- ✅ Load/save CSV files
- ✅ Edit cells and headers  
- ✅ Insert/delete rows and columns
- ✅ View data in formatted output
- ✅ Create new sheets with defaults
- ✅ Command-line automation support

### GUI Mode Features:
- ✅ Load/save CSV files with file dialogs
- ✅ Interactive data grid with scrolling
- ✅ Cell editing with double-click
- ✅ Visual row/column operations
- ✅ Menu and toolbar interface
- ✅ Keyboard shortcuts
- ✅ Unsaved changes detection

## License

This project uses only standard library modules and has no external dependencies.
