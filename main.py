import sys
from PyQt5 import QtCore, QtGui, QtWidgets

from model import CsvTableModel
from view import TableView, TextEditDelegate

# Default columns tailored to your workflow
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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Requirement Editor")
        # Fits well on 1920x1080 monitors while leaving room for OS chrome
        self.resize(1700, 980)

        # Core widgets
        self.view = TableView(self)
        self.setCentralWidget(self.view)

        self.model = CsvTableModel([], DEFAULT_HEADERS[:])
        self.view.setModel(self.model)

        # Multi-line editor delegate (Enter=newline, Shift+Enter=move down)
        self.delegate = TextEditDelegate(self.view)
        self.view.setItemDelegate(self.delegate)
        self.delegate.commitAndClose.connect(self.on_delegate_commit_move_down)

        # State
        self._wrap_enabled = True
        self._current_path = None
        self._dirty = False

        # UI setup
        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._create_status_bar()
        self._apply_dark_mode()
        self._connect_signals()

        # Start with a clean sheet
        self._new_sheet_with_defaults()

    # ---------- UI plumbing ----------
    def _create_actions(self):
        self.act_new = QtWidgets.QAction("New", self, shortcut="Ctrl+N", triggered=self.new_file)
        self.act_open = QtWidgets.QAction("Open...", self, shortcut="Ctrl+O", triggered=self.open_file)
        self.act_save = QtWidgets.QAction("Save", self, shortcut="Ctrl+S", triggered=self.save_file)
        self.act_save_as = QtWidgets.QAction("Save As...", self, triggered=self.save_file_as)

        self.act_toggle_wrap = QtWidgets.QAction("Toggle Wrap", self, shortcut="Ctrl+W", triggered=self.toggle_wrap)
        self.act_insert_row = QtWidgets.QAction("Insert Row Below", self, shortcut="Ctrl+Enter", triggered=self.insert_row_below)
        self.act_insert_col = QtWidgets.QAction("Insert Column Right", self, shortcut="Ctrl+Shift+=", triggered=self.insert_col_right)
        self.act_autosize_cols = QtWidgets.QAction("Autosize All Columns", self, triggered=self.autosize_all_columns)
        self.act_autosize_rows = QtWidgets.QAction("Autosize All Rows", self, triggered=self.autosize_all_rows)

    def _create_menu(self):
        m_file = self.menuBar().addMenu("&File")
        m_file.addAction(self.act_new)
        m_file.addAction(self.act_open)
        m_file.addSeparator()
        m_file.addAction(self.act_save)
        m_file.addAction(self.act_save_as)

        m_edit = self.menuBar().addMenu("&Edit")
        m_edit.addAction(self.act_toggle_wrap)
        m_edit.addSeparator()
        m_edit.addAction(self.act_insert_row)
        m_edit.addAction(self.act_insert_col)
        m_edit.addSeparator()
        m_edit.addAction(self.act_autosize_cols)
        m_edit.addAction(self.act_autosize_rows)

    def _create_toolbar(self):
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        tb.addAction(self.act_new)
        tb.addAction(self.act_open)
        tb.addAction(self.act_save)
        tb.addSeparator()
        tb.addAction(self.act_toggle_wrap)
        tb.addSeparator()
        tb.addAction(self.act_autosize_cols)
        tb.addAction(self.act_autosize_rows)

    def _create_status_bar(self):
        self.statusBar().showMessage("Ready")

    def _apply_dark_mode(self):
        QtWidgets.QApplication.setStyle("Fusion")
        palette = QtGui.QPalette()
        base = QtGui.QColor(45, 45, 45)
        alt = QtGui.QColor(53, 53, 53)
        text = QtGui.QColor(220, 220, 220)
        disabled = QtGui.QColor(127, 127, 127)
        highlight = QtGui.QColor(90, 130, 200)

        palette.setColor(QtGui.QPalette.Window, alt)
        palette.setColor(QtGui.QPalette.WindowText, text)
        palette.setColor(QtGui.QPalette.Base, base)
        palette.setColor(QtGui.QPalette.AlternateBase, alt)
        palette.setColor(QtGui.QPalette.ToolTipBase, text)
        palette.setColor(QtGui.QPalette.ToolTipText, text)
        palette.setColor(QtGui.QPalette.Text, text)
        palette.setColor(QtGui.QPalette.Button, alt)
        palette.setColor(QtGui.QPalette.ButtonText, text)
        palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        palette.setColor(QtGui.QPalette.Highlight, highlight)
        palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)

        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, disabled)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, disabled)
        QtWidgets.QApplication.setPalette(palette)

    def _connect_signals(self):
        # Table context menu actions
        self.view.requestInsertRowAbove.connect(self.insert_row_above)
        self.view.requestInsertRowBelow.connect(self.insert_row_below_at)
        self.view.requestDeleteRow.connect(self.delete_row)
        self.view.requestInsertColLeft.connect(self.insert_col_left)
        self.view.requestInsertColRight.connect(self.insert_col_right_at)
        self.view.requestDeleteCol.connect(self.delete_col)  # requires delete_col implementation
        self.view.requestClearCell.connect(self.clear_cell)
        self.view.requestAutosizeRow.connect(self.view.autosize_row)
        self.view.requestAutosizeCol.connect(self.view.autosize_col)
        self.view.requestToggleWrap.connect(self.toggle_wrap)

        # Track edits to set dirty flag
        self.model.dataChanged.connect(self._mark_dirty)
        self.model.rowsInserted.connect(self._mark_dirty)
        self.model.rowsRemoved.connect(self._mark_dirty)
        self.model.columnsInserted.connect(self._mark_dirty)
        self.model.columnsRemoved.connect(self._mark_dirty)
        self.model.headerDataChanged.connect(self._mark_dirty)

        # Allow header double-click rename
        header = self.view.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionDoubleClicked.connect(self.rename_header)

    # ---------- Slot helpers ----------
    def _mark_dirty(self, *args, **kwargs):
        if not self._dirty:
            self._dirty = True
            self._update_title()

    def _update_title(self):
        name = self._current_path if self._current_path else "Untitled.csv"
        mark = " *" if self._dirty else ""
        self.setWindowTitle(f"CSV Requirement Editor - {name}{mark}")

    def _prompt_unsaved(self):
        if not self._dirty:
            return True
        ret = QtWidgets.QMessageBox.question(
            self,
            "Unsaved changes",
            "You have unsaved changes. Save them now?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.Yes,
        )
        if ret == QtWidgets.QMessageBox.Cancel:
            return False
        if ret == QtWidgets.QMessageBox.Yes:
            return self.save_file()
        return True

    def _new_sheet_with_defaults(self):
        self.model.beginResetModel()
        self.model._headers = DEFAULT_HEADERS[:]
        self.model._data = []
        self.model.endResetModel()
        # Add an initial empty row for convenience
        self.model.insertRows(0, 1)
        self._current_path = None
        self._dirty = False
        self._update_title()
        self.statusBar().showMessage("New sheet created", 2000)

    # ---------- File operations ----------
    def new_file(self):
        if not self._prompt_unsaved():
            return
        self._new_sheet_with_defaults()

    def open_file(self):
        if not self._prompt_unsaved():
            return
        dlg = QtWidgets.QFileDialog(self, "Open CSV", "", "CSV Files (*.csv);;All Files (*)")
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return
        path = dlg.selectedFiles()[0]
        try:
            self.model.load_from_csv(path)
            self._current_path = path
            self._dirty = False
            self._update_title()
            self.statusBar().showMessage(f"Loaded: {path}", 2000)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to open file:\n{e}")

    def save_file(self):
        if not self._current_path:
            return self.save_file_as()
        try:
            order = self.view.visual_column_order()
            self.model.save_to_csv(self._current_path, order=order)
            self._dirty = False
            self._update_title()
            self.statusBar().showMessage(f"Saved: {self._current_path}", 2000)
            return True
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")
            return False

    def save_file_as(self):
        dlg = QtWidgets.QFileDialog(self, "Save CSV As", "", "CSV Files (*.csv);;All Files (*)")
        dlg.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dlg.setDefaultSuffix("csv")
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return False
        path = dlg.selectedFiles()[0]
        self._current_path = path
        return self.save_file()

    # ---------- Edit actions ----------
    def rename_header(self, section):
        current = self.model.headerData(section, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole) or ""
        new, ok = QtWidgets.QInputDialog.getText(self, "Rename Column", "Header:", QtWidgets.QLineEdit.Normal, current)
        if ok:
            self.model.setHeaderData(section, QtCore.Qt.Horizontal, new, QtCore.Qt.EditRole)

    def toggle_wrap(self):
        self._wrap_enabled = not self._wrap_enabled
        self.view.setWordWrap(self._wrap_enabled)
        self.statusBar().showMessage(f"Wrap {'enabled' if self._wrap_enabled else 'disabled'}", 1500)

    def insert_row_above(self, row):
        self.model.insertRows(row, 1)

    def insert_row_below_at(self, row):
        self.model.insertRows(row + 1, 1)

    def delete_row(self, row):
        self.model.removeRows(row, 1)

    def insert_col_left(self, col):
        self.model.insertColumns(col, 1)

    def insert_col_right(self):
        idx = self.view.currentIndex()
        col = idx.column() if idx.isValid() else (self.model.columnCount() - 1)
        self.insert_col_right_at(col)

    def insert_col_right_at(self, col):
        self.model.insertColumns(col + 1, 1)

    def delete_col(self, col):
        # Missing before: remove the selected column
        self.model.removeColumns(col, 1)

    def clear_cell(self, row, col):
        idx = self.model.index(row, col)
        self.model.setData(idx, "", QtCore.Qt.EditRole)

    def autosize_all_columns(self):
        for c in range(self.model.columnCount()):
            self.view.resizeColumnToContents(c)

    def autosize_all_rows(self):
        for r in range(self.model.rowCount()):
            self.view.resizeRowToContents(r)

    # ---------- Delegate behavior ----------
    def on_delegate_commit_move_down(self, editor_widget):
        # Commit current editor's data, then move to next row same column
        idx = self.view.currentIndex()
        if not idx.isValid():
            return
        # Commit edit before closing so the text is saved
        self.view.commitData(editor_widget)
        self.view.closePersistentEditor(idx)
        # Move down
        model = self.view.model()
        next_row = min(idx.row() + 1, model.rowCount() - 1) if model.rowCount() > 0 else 0
        next_idx = model.index(next_row, idx.column())
        self.view.setCurrentIndex(next_idx)
        self.view.edit(next_idx)

    # Convenience for toolbar action
    def insert_row_below(self):
        idx = self.view.currentIndex()
        row = idx.row() if idx.isValid() else self.model.rowCount() - 1
        self.model.insertRows(max(row, 0) + 1, 1)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()