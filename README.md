# CSV Editor

A GUI application for editing CSV files using only Python standard library modules. This tool provides comprehensive CSV editing functionality without requiring any external dependencies.

## Features

- **Load and save CSV files** with proper encoding support
- **Interactive data grid** with scrolling and cell editing
- **Edit individual cells** with double-click activation
- **Insert and delete rows and columns** at any position
- **Manage headers** including renaming and adding new columns
- **Clear cells** to remove unwanted data
- **Create new sheets** with default headers
- **Standard library only** - no external dependencies required
- **File dialogs** for easy file management
- **Keyboard shortcuts** for common operations
- **Unsaved changes detection** with prompts

## Installation

No installation required! Just run the Python scripts directly since they only use standard library modules.

## Usage

Launch the graphical interface:

```bash
python main.py
```

The GUI provides:
- **File Menu**: New, Open, Save, Save As, Exit
- **Edit Menu**: Insert/delete rows and columns, clear cells
- **Interactive Grid**: Double-click cells to edit, click headers to rename
- **Toolbar**: Quick access to common operations
- **Keyboard Shortcuts**: Ctrl+N (New), Ctrl+O (Open), Ctrl+S (Save)

**Requirements:**
- Python 3.6.5+ with Tkinter support (included in most Python installations)
- Tkinter is part of the Python standard library on most systems

### Default Headers

When creating a new file, the following default headers are used:
- Type Parent Requirement
- ID
- Name  
- Text
- Traced To
- Verified By
- Class
- Story

These headers are tailored for requirement tracking workflows but can be modified using the GUI interface.

### Data Format

- **CSV files** are loaded with UTF-8 encoding with BOM support
- **Row/column indices** are 0-based (first row is 0, first column is 0)
- **Empty cells** are represented as empty strings
- **Multi-line text** is supported in cells
- **Automatic normalization** ensures all rows have the same number of columns

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
python main.py   # Test GUI functionality
```

### File Structure
- `main.py` - Main entry point (GUI application)
- `csv_editor.py` - Core CSV editing functionality
- `gui.py` - Tkinter GUI implementation

## Migration from Original GUI Version

This tool is a refactor from the original PyQt5-based GUI application to a Tkinter-based implementation using only standard library modules.

### GUI Features:
- ✅ Load/save CSV files with file dialogs
- ✅ Interactive data grid with scrolling
- ✅ Cell editing with double-click
- ✅ Visual row/column operations
- ✅ Menu and toolbar interface
- ✅ Keyboard shortcuts
- ✅ Unsaved changes detection

## License

This project uses only standard library modules and has no external dependencies.
