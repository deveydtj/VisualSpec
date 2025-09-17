"""
Tkinter GUI for CSV Editor - Provides a graphical interface for CSV editing.

This module provides a GUI wrapper around the CsvEditor class using tkinter,
maintaining compatibility with Python 3.6.5+ and using only standard library.
"""

import sys
from typing import Optional

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog, ttk
except ImportError:
    # For Python 2.x compatibility (though not needed for this project)
    try:
        import Tkinter as tk
        import tkFileDialog as filedialog
        import tkMessageBox as messagebox
        import tkSimpleDialog as simpledialog  # noqa: F401
        import ttk
    except ImportError:
        print("Error: Tkinter is not available.", file=sys.stderr)
        print("Please ensure Python is installed with Tkinter support.")
        sys.exit(1)

from csv_editor import CsvEditor


class CsvEditorGUI:
    """
    Tkinter-based GUI for CSV editing using the CsvEditor backend.

    Features:
    - File operations (New, Open, Save, Save As)
    - Data display in scrollable table
    - Cell editing with double-click
    - Row/column insertion and deletion
    - Header editing
    """

    def __init__(self, master: tk.Tk):
        """Initialize the GUI application."""
        self.master = master
        self.master.title("CSV Editor")
        self.master.geometry("800x600")

        # Configure dark mode theme
        self._configure_dark_theme()

        # CSV editor instance
        self.editor = CsvEditor()
        self.current_file: Optional[str] = None
        self.is_modified = False

        # Track last selected column for operations
        self.last_selected_column = 0

        # Set up GUI components
        self._create_menu()
        self._create_toolbar()
        self._create_main_area()
        self._create_status_bar()

        # Handle window close
        self.master.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Initialize with empty data
        self._refresh_display()

    def _configure_dark_theme(self):
        """Configure dark mode theme for the entire application."""
        # Dark mode color scheme
        dark_bg = "#2b2b2b"  # Dark background
        dark_fg = "#ffffff"  # White text
        dark_select_bg = "#404040"  # Selected item background
        dark_entry_bg = "#363636"  # Entry widget background
        dark_menu_bg = "#333333"  # Menu background
        dark_button_bg = "#404040"  # Button background

        # Configure root window
        self.master.configure(bg=dark_bg)

        # Configure ttk style for themed widgets
        style = ttk.Style()

        # Try to use a dark theme if available, fallback to default
        try:
            # Some systems have built-in dark themes
            available_themes = style.theme_names()
            if "equilux" in available_themes:
                style.theme_use("equilux")
            elif "black" in available_themes:
                style.theme_use("black")
            else:
                # Create custom dark theme
                style.theme_use("clam")  # Use clam as base
        except Exception:
            style.theme_use("clam")

        # Configure custom styles for dark mode
        style.configure(
            ".",
            background=dark_bg,
            foreground=dark_fg,
            fieldbackground=dark_entry_bg,
            selectbackground=dark_select_bg,
            selectforeground=dark_fg,
        )

        # Configure Treeview for dark mode
        style.configure(
            "Treeview",
            background=dark_bg,
            foreground=dark_fg,
            fieldbackground=dark_bg,
            selectbackground=dark_select_bg,
            selectforeground=dark_fg,
        )

        style.configure(
            "Treeview.Heading",
            background=dark_button_bg,
            foreground=dark_fg,
            relief="flat",
        )

        # Configure Button style
        style.configure(
            "TButton",
            background=dark_button_bg,
            foreground=dark_fg,
            focuscolor="none",
            relief="flat",
        )

        style.map(
            "TButton",
            background=[("active", dark_select_bg), ("pressed", dark_entry_bg)],
        )

        # Configure Frame style
        style.configure("TFrame", background=dark_bg)

        # Configure Label style
        style.configure("TLabel", background=dark_bg, foreground=dark_fg)

        # Configure Separator style
        style.configure("TSeparator", background=dark_select_bg)

        # Store colors for use in other widgets
        self.dark_colors = {
            "bg": dark_bg,
            "fg": dark_fg,
            "select_bg": dark_select_bg,
            "entry_bg": dark_entry_bg,
            "menu_bg": dark_menu_bg,
            "button_bg": dark_button_bg,
        }

    def _create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(
            self.master,
            bg=self.dark_colors["menu_bg"],
            fg=self.dark_colors["fg"],
            activebackground=self.dark_colors["select_bg"],
            activeforeground=self.dark_colors["fg"],
        )
        self.master.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=self.dark_colors["menu_bg"],
            fg=self.dark_colors["fg"],
            activebackground=self.dark_colors["select_bg"],
            activeforeground=self.dark_colors["fg"],
        )
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self._new_file, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(
            label="Open...", command=self._open_file, accelerator="Ctrl+O"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Save", command=self._save_file, accelerator="Ctrl+S"
        )
        file_menu.add_command(label="Save As...", command=self._save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)

        # Edit menu
        edit_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=self.dark_colors["menu_bg"],
            fg=self.dark_colors["fg"],
            activebackground=self.dark_colors["select_bg"],
            activeforeground=self.dark_colors["fg"],
        )
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Insert Row Above", command=self._insert_row_above)
        edit_menu.add_command(label="Insert Row Below", command=self._insert_row_below)
        edit_menu.add_command(label="Delete Row", command=self._delete_row)
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Insert Column Left", command=self._insert_column_left
        )
        edit_menu.add_command(
            label="Insert Column Right", command=self._insert_column_right
        )
        edit_menu.add_command(label="Delete Column", command=self._delete_column)
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Cell", command=self._clear_cell)

        # Keyboard shortcuts
        self.master.bind("<Control-n>", lambda e: self._new_file())
        self.master.bind("<Control-o>", lambda e: self._open_file())
        self.master.bind("<Control-s>", lambda e: self._save_file())

    def _create_toolbar(self):
        """Create toolbar with common actions."""
        toolbar = ttk.Frame(self.master)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)

        ttk.Button(toolbar, text="New", command=self._new_file).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="Open", command=self._open_file).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="Save", command=self._save_file).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        ttk.Button(toolbar, text="Insert Row", command=self._insert_row_below).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="Delete Row", command=self._delete_row).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            toolbar, text="Insert Column", command=self._insert_column_right
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete Column", command=self._delete_column).pack(
            side=tk.LEFT, padx=2
        )

    def _create_main_area(self):
        """Create the main data display area."""
        # Create frame for treeview and scrollbars
        tree_frame = ttk.Frame(self.master)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create treeview with scrollbars
        self.tree = ttk.Treeview(tree_frame)

        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=v_scrollbar.set)

        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(
            tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview
        )
        self.tree.configure(xscrollcommand=h_scrollbar.set)

        # Pack components
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure tree for cell editing
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Return>", self._on_return_key)
        self.tree.bind("<Button-1>", self._on_single_click)

        # Entry widget for editing (initially hidden)
        self.edit_entry = tk.Entry(
            self.tree,
            bg=self.dark_colors["entry_bg"],
            fg=self.dark_colors["fg"],
            selectbackground=self.dark_colors["select_bg"],
            selectforeground=self.dark_colors["fg"],
            insertbackground=self.dark_colors["fg"],
            relief="flat",
            borderwidth=1,
        )
        self.edit_entry.bind("<Return>", self._finish_edit)
        self.edit_entry.bind("<Escape>", self._cancel_edit)
        self.edit_entry.bind("<FocusOut>", self._finish_edit)

        # Track current edit state
        self.edit_item = None
        self.edit_column = None

    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = ttk.Label(self.master, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _refresh_display(self):
        """Refresh the treeview display with current editor data."""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Set up columns
        if self.editor.column_count() > 0:
            columns = [f"col_{i}" for i in range(self.editor.column_count())]
            self.tree["columns"] = columns
            self.tree["show"] = "tree headings"  # Show both tree and headings

            # Configure column 0 (tree column)
            self.tree.column("#0", width=50, minwidth=50)
            self.tree.heading("#0", text="Row")

            # Configure data columns
            for i, col in enumerate(columns):
                header = self.editor.get_header(i)
                self.tree.column(col, width=120, minwidth=80)
                self.tree.heading(
                    col, text=header, command=lambda c=i: self._edit_header(c)
                )
        else:
            # No data case
            self.tree["columns"] = ()
            self.tree["show"] = "tree"

        # Populate rows
        for row in range(self.editor.row_count()):
            values = []
            for col in range(self.editor.column_count()):
                values.append(self.editor.get_cell(row, col))
            self.tree.insert("", "end", text=str(row), values=values)

        # Update status
        self._update_status()

    def _update_status(self):
        """Update the status bar."""
        rows = self.editor.row_count()
        cols = self.editor.column_count()
        file_info = f" - {self.current_file}" if self.current_file else ""
        modified = " [Modified]" if self.is_modified else ""
        status = f"Rows: {rows}, Columns: {cols}{file_info}{modified}"
        self.status_bar.config(text=status)

    def _mark_modified(self):
        """Mark the document as modified."""
        self.is_modified = True
        self._update_status()

    def _mark_saved(self):
        """Mark the document as saved."""
        self.is_modified = False
        self._update_status()

    def _new_file(self):
        """Create a new CSV file."""
        if self._check_unsaved_changes():
            return

        # Use default headers from CLI
        default_headers = [
            "Type Parent Requirement",
            "ID",
            "Name",
            "Text",
            "Traced To",
            "Verified By",
            "Class",
            "Story",
        ]

        self.editor.new_sheet_with_defaults(default_headers)
        self.current_file = None
        self.is_modified = False
        self._refresh_display()

    def _open_file(self):
        """Open a CSV file."""
        if self._check_unsaved_changes():
            return

        filename = filedialog.askopenfilename(
            title="Open CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if filename:
            try:
                self.editor.load_from_csv(filename)
                self.current_file = filename
                self.is_modified = False
                self._refresh_display()
                self.status_bar.config(text=f"Opened: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def _save_file(self):
        """Save the current file."""
        if self.current_file:
            try:
                self.editor.save_to_csv(self.current_file)
                self._mark_saved()
                self.status_bar.config(text=f"Saved: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self._save_as_file()

    def _save_as_file(self):
        """Save the file with a new name."""
        filename = filedialog.asksaveasfilename(
            title="Save CSV File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if filename:
            try:
                self.editor.save_to_csv(filename)
                self.current_file = filename
                self._mark_saved()
                self.status_bar.config(text=f"Saved: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def _check_unsaved_changes(self) -> bool:
        """Check for unsaved changes and prompt user.

        Returns True if action should be cancelled.
        """
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them first?",
            )
            if result is True:  # Yes - save first
                self._save_file()
                return self.is_modified  # Still modified if save failed
            elif result is None:  # Cancel
                return True
            # No - discard changes, continue
        return False

    def _on_closing(self):
        """Handle window close event."""
        if not self._check_unsaved_changes():
            self.master.destroy()

    def _get_selected_row_col(self):
        """Get the selected row and column indices."""
        selection = self.tree.selection()
        if not selection:
            return None, None

        item = selection[0]
        # Get row index
        row_idx = None
        for i, child in enumerate(self.tree.get_children()):
            if child == item:
                row_idx = i
                break

        # Return the tracked column instead of always 0
        return row_idx, self.last_selected_column

    def _insert_row_above(self):
        """Insert a row above the selected row."""
        row, _ = self._get_selected_row_col()
        if row is None:
            row = 0

        if self.editor.insert_row(row):
            self._mark_modified()
            self._refresh_display()

    def _insert_row_below(self):
        """Insert a row below the selected row."""
        row, _ = self._get_selected_row_col()
        if row is None:
            row = self.editor.row_count()
        else:
            row += 1

        if self.editor.insert_row(row):
            self._mark_modified()
            self._refresh_display()

    def _delete_row(self):
        """Delete the selected row."""
        row, _ = self._get_selected_row_col()
        if row is not None:
            if messagebox.askyesno("Delete Row", f"Delete row {row}?"):
                if self.editor.remove_row(row):
                    self._mark_modified()
                    self._refresh_display()

    def _insert_column_left(self):
        """Insert a column to the left of the current selection."""
        _, col = self._get_selected_row_col()
        if col is None:
            col = 0

        if self.editor.insert_column(col):
            self._mark_modified()
            self._refresh_display()

    def _insert_column_right(self):
        """Insert a column to the right of the current selection."""
        _, col = self._get_selected_row_col()
        if col is None:
            col = self.editor.column_count()
        else:
            col += 1

        if self.editor.insert_column(col):
            self._mark_modified()
            self._refresh_display()

    def _delete_column(self):
        """Delete the selected column."""
        _, col = self._get_selected_row_col()
        if col is not None:
            header = self.editor.get_header(col)
            if messagebox.askyesno("Delete Column", f"Delete column '{header}'?"):
                if self.editor.remove_column(col):
                    self._mark_modified()
                    self._refresh_display()

    def _clear_cell(self):
        """Clear the selected cell."""
        row, col = self._get_selected_row_col()
        if row is not None and col is not None:
            if self.editor.clear_cell(row, col):
                self._mark_modified()
                self._refresh_display()

    def _edit_header(self, col: int):
        """Edit a column header."""
        current_header = self.editor.get_header(col)
        new_header = tk.simpledialog.askstring(
            "Edit Header",
            f"Enter new header for column {col}:",
            initialvalue=current_header,
        )

        if new_header is not None:  # User didn't cancel
            self.editor.set_header(col, new_header)
            self._mark_modified()
            self._refresh_display()

    def _on_single_click(self, event):
        """Handle single-click to track column selection."""
        column = self.tree.identify_column(event.x)

        if column == "#0":  # Tree column (row numbers)
            self.last_selected_column = 0
        else:
            # Convert column identifier to index
            col_idx = int(column.replace("#", "")) - 1
            if col_idx >= 0:
                self.last_selected_column = col_idx

    def _on_double_click(self, event):
        """Handle double-click for cell editing."""
        item = self.tree.selection()[0]
        column = self.tree.identify_column(event.x)

        if column == "#0":  # Tree column (row numbers)
            return

        # Convert column identifier to index
        col_idx = int(column.replace("#", "")) - 1

        # Update tracked column
        self.last_selected_column = col_idx

        # Get row index
        row_idx = None
        for i, child in enumerate(self.tree.get_children()):
            if child == item:
                row_idx = i
                break

        if row_idx is not None:
            self._start_edit(item, col_idx, row_idx)

    def _on_return_key(self, event):
        """Handle Return key for cell editing."""
        selection = self.tree.selection()
        if selection:
            self._on_double_click(event)

    def _start_edit(self, item, col_idx: int, row_idx: int):
        """Start editing a cell."""
        # Get current cell value
        current_value = self.editor.get_cell(row_idx, col_idx)

        # Position the entry widget over the cell
        bbox = self.tree.bbox(item, f"#{col_idx + 1}")
        if bbox:
            x, y, width, height = bbox
            self.edit_entry.place(x=x, y=y, width=width, height=height)
            self.edit_entry.delete(0, tk.END)
            self.edit_entry.insert(0, current_value)
            self.edit_entry.focus()
            self.edit_entry.select_range(0, tk.END)

            # Store edit context
            self.edit_item = item
            self.edit_column = col_idx
            self.edit_row = row_idx

    def _finish_edit(self, event=None):
        """Finish editing and save the value."""
        if self.edit_item is not None:
            new_value = self.edit_entry.get()

            # Update the editor
            if self.editor.set_cell(self.edit_row, self.edit_column, new_value):
                self._mark_modified()
                # Update just this item instead of full refresh for better performance
                values = list(self.tree.item(self.edit_item)["values"])
                if self.edit_column < len(values):
                    values[self.edit_column] = new_value
                self.tree.item(self.edit_item, values=values)

            self._cancel_edit()

    def _cancel_edit(self, event=None):
        """Cancel editing."""
        self.edit_entry.place_forget()
        self.edit_item = None
        self.edit_column = None
        self.edit_row = None
        self.tree.focus()


def launch_gui():
    """Launch the CSV Editor GUI application."""
    try:
        root = tk.Tk()
        CsvEditorGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error launching GUI: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(launch_gui())
