# CLI CSV Editor

A command-line interface for editing CSV files using only Python standard library modules. This tool provides comprehensive CSV editing functionality without requiring any GUI dependencies.

## Features

- **Load and save CSV files** with proper encoding support
- **View data** in formatted table layout 
- **Edit individual cells** with validation
- **Insert and delete rows and columns** at any position
- **Manage headers** including renaming and adding new columns
- **Clear cells** to remove unwanted data
- **Create new sheets** with default headers
- **Standard library only** - no external dependencies required

## Installation

No installation required! Just run the Python scripts directly since they only use standard library modules.

## Usage

### Basic Commands

Run `python main.py --help` to see all available commands:

```bash
python main.py <command> [arguments]
```

### Commands Overview

| Command | Description | Example |
|---------|-------------|---------|
| `load` | Load CSV file | `python main.py load data.csv` |
| `save` | Save to CSV file | `python main.py save output.csv` |
| `view` | View current data | `python main.py view --rows 10` |
| `edit` | Edit cell value | `python main.py edit 0 1 "New Value"` |
| `insert-row` | Insert new row | `python main.py insert-row 5` |
| `delete-row` | Delete row | `python main.py delete-row 3` |
| `insert-col` | Insert new column | `python main.py insert-col 2 "Header"` |
| `delete-col` | Delete column | `python main.py delete-col 4` |
| `header` | Set column header | `python main.py header 1 "New Header"` |
| `clear` | Clear cell | `python main.py clear 2 3` |
| `new` | Create new sheet | `python main.py new` |

### Detailed Examples

#### Loading and Viewing Data
```bash
# Load a CSV file
python main.py load sample.csv

# View data (shows first 20 rows by default)
python main.py view

# View more rows and adjust column width
python main.py view --rows 50 --width 30
```

#### Editing Data
```bash
# Edit cell at row 0, column 1
python main.py edit 0 1 "Updated Value"

# Clear a cell
python main.py clear 2 3

# Set header for column 0
python main.py header 0 "Customer Name"
```

#### Adding and Removing Data
```bash
# Insert a new row at position 5
python main.py insert-row 5

# Delete row 3
python main.py delete-row 3

# Insert new column at position 2 with header
python main.py insert-col 2 "New Column"

# Delete column 4
python main.py delete-col 4
```

#### Working with Files
```bash
# Create a new sheet with default headers
python main.py new

# Save current data to a file
python main.py save output.csv
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
# 1. Create a new sheet
python main.py new

# 2. Load existing data  
python main.py load requirements.csv

# 3. View the data
python main.py view

# 4. Edit a specific cell
python main.py edit 0 2 "Updated Requirement Name"

# 5. Add a new column for priority
python main.py insert-col 7 "Priority"

# 6. Add some data to the new column
python main.py edit 0 7 "High"
python main.py edit 1 7 "Medium"

# 7. Save the changes
python main.py save requirements_updated.csv
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
- `main.py` - Main CLI entry point
- `cli.py` - Command-line interface implementation
- `csv_editor.py` - Core CSV editing functionality

## Migration from GUI Version

This tool is a complete refactor from the original PyQt5-based GUI application. The CLI version provides the same core functionality:

- ✅ Load/save CSV files
- ✅ Edit cells and headers  
- ✅ Insert/delete rows and columns
- ✅ View data in formatted output
- ✅ Create new sheets with defaults
- ❌ GUI interface (removed)
- ❌ Visual table editing (replaced with commands)
- ❌ Mouse interactions (replaced with CLI commands)

## License

This project uses only standard library modules and has no external dependencies.
