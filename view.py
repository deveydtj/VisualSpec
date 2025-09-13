from PyQt5 import QtCore, QtGui, QtWidgets


class TextEditDelegate(QtWidgets.QStyledItemDelegate):
    """
    Multi-line in-cell editor using QTextEdit.
    - Enter inserts a newline (default QTextEdit behavior).
    - Shift+Enter commits and moves to the next row (same column) via signal.
    """
    commitAndClose = QtCore.pyqtSignal(QtWidgets.QWidget)

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QTextEdit(parent)
        editor.setAcceptRichText(False)
        editor.setFrameShape(QtWidgets.QFrame.NoFrame)
        editor.installEventFilter(self)
        editor.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        editor.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        editor.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # inherit table font
        editor.setFont(parent.font())
        return editor

    def setEditorData(self, editor, index):
        text = index.model().data(index, QtCore.Qt.EditRole) or ""
        editor.setPlainText(text)
        # place cursor at end
        cursor = editor.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        editor.setTextCursor(cursor)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.toPlainText(), QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def eventFilter(self, editor, event):
        # Shift+Enter => commit-and-move (we emit to MainWindow)
        if isinstance(editor, QtWidgets.QTextEdit):
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                    if event.modifiers() & QtCore.Qt.ShiftModifier:
                        # Commit the editor data before emitting signal
                        view = self.parent()
                        if isinstance(view, QtWidgets.QAbstractItemView):
                            view.commitData(editor)
                        self.commitAndClose.emit(editor)
                        return True
        return super().eventFilter(editor, event)


class TableView(QtWidgets.QTableView):
    """
    Fast, user-friendly table view with:
    - Per-pixel scrolling
    - Interactive resize for rows/columns
    - Header reordering (drag to move columns)
    - Context menu for insert/delete rows/columns, clear cell, autosize, wrap toggle
    - Shift+Enter commits and moves to next row
    """
    requestInsertRowAbove = QtCore.pyqtSignal(int)
    requestInsertRowBelow = QtCore.pyqtSignal(int)
    requestDeleteRow = QtCore.pyqtSignal(int)
    requestInsertColLeft = QtCore.pyqtSignal(int)
    requestInsertColRight = QtCore.pyqtSignal(int)
    requestDeleteCol = QtCore.pyqtSignal(int)
    requestClearCell = QtCore.pyqtSignal(int, int)
    requestAutosizeRow = QtCore.pyqtSignal(int)
    requestAutosizeCol = QtCore.pyqtSignal(int)
    requestToggleWrap = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Visual behavior
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        self.setWordWrap(True)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.setTabKeyNavigation(False)

        # Defaults tuned for 1920x1080 without feeling cramped
        self.verticalHeader().setDefaultSectionSize(28)
        self.horizontalHeader().setDefaultSectionSize(160)

        # Resizing and moving
        h = self.horizontalHeader()
        v = self.verticalHeader()
        h.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        v.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        h.setStretchLastSection(False)
        h.setSectionsMovable(True)
        h.setDragEnabled(True)
        h.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        # Context menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_context_menu)

        # Sorting off (we want raw order)
        self.setSortingEnabled(False)

    def sizeHint(self):
        # Good default that fits on 1080p with toolbars/menus
        return QtCore.QSize(1600, 900)

    def keyPressEvent(self, event):
        # Shift+Enter: commit current edit and move to next row (same column)
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter) and (event.modifiers() & QtCore.Qt.ShiftModifier):
            self._commit_editor_and_move()
            return
        super().keyPressEvent(event)

    def _commit_editor_and_move(self):
        idx = self.currentIndex()
        if not idx.isValid():
            return
        # Commit any open editor before closing it
        self.commitData(self.focusWidget())
        self.closePersistentEditor(idx)
        model = self.model()
        if not model:
            return
        next_row = min(idx.row() + 1, model.rowCount() - 1) if model.rowCount() > 0 else 0
        next_idx = model.index(next_row, idx.column())
        self.setCurrentIndex(next_idx)
        self.edit(next_idx)

    def _open_context_menu(self, pos):
        idx = self.indexAt(pos)
        global_pos = self.viewport().mapToGlobal(pos)

        menu = QtWidgets.QMenu(self)
        insert_row_above = menu.addAction("Insert row above")
        insert_row_below = menu.addAction("Insert row below")
        delete_row = menu.addAction("Delete row")
        menu.addSeparator()
        insert_col_left = menu.addAction("Insert column left")
        insert_col_right = menu.addAction("Insert column right")
        delete_col = menu.addAction("Delete column")
        menu.addSeparator()
        clear_cell = menu.addAction("Clear cell")
        autosize_row = menu.addAction("Autosize row height")
        autosize_col = menu.addAction("Autosize column width")
        wrap_toggle = menu.addAction("Toggle wrap")

        action = menu.exec_(global_pos)

        if not idx.isValid():
            if action == wrap_toggle:
                self.requestToggleWrap.emit()
            return

        r, c = idx.row(), idx.column()
        if action == insert_row_above:
            self.requestInsertRowAbove.emit(r)
        elif action == insert_row_below:
            self.requestInsertRowBelow.emit(r)
        elif action == delete_row:
            self.requestDeleteRow.emit(r)
        elif action == insert_col_left:
            self.requestInsertColLeft.emit(c)
        elif action == insert_col_right:
            self.requestInsertColRight.emit(c)
        elif action == delete_col:
            self.requestDeleteCol.emit(c)
        elif action == clear_cell:
            self.requestClearCell.emit(r, c)
        elif action == autosize_row:
            self.requestAutosizeRow.emit(r)
        elif action == autosize_col:
            self.requestAutosizeCol.emit(c)
        elif action == wrap_toggle:
            self.requestToggleWrap.emit()

    def visual_column_order(self):
        """
        Returns a list of logical column indices in current visual order.
        Useful for saving CSV in the user-reordered order.
        """
        header = self.horizontalHeader()
        return [header.logicalIndex(i) for i in range(header.count())]

    # Convenience autosize helpers
    def autosize_row(self, row):
        if 0 <= row < self.model().rowCount():
            self.resizeRowToContents(row)

    def autosize_col(self, col):
        if 0 <= col < self.model().columnCount():
            self.resizeColumnToContents(col)