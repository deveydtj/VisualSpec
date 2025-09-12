import csv
from PyQt5 import QtCore, QtGui


class CsvTableModel(QtCore.QAbstractTableModel):
    """
    Lightweight, fast table model for CSV-like data.

    Features:
    - Editable cells (multi-line supported by delegate)
    - Insert/remove rows and columns
    - Column move support (for header drag/drop)
    - Simple "flash" highlight for newly inserted items
    - CSV load/save (optionally honoring a visual column order)
    """
    def __init__(self, data=None, headers=None, parent=None):
        super().__init__(parent)
        self._data = data if data is not None else []
        self._headers = headers if headers is not None else []
        self._flash_cells = set()  # for subtle insertion highlight

    # ---------------------
    # Qt model boilerplate
    # ---------------------
    def rowCount(self, parent=QtCore.QModelIndex()):
        return 0 if parent.isValid() else len(self._data)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        if self._headers:
            return len(self._headers)
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        r, c = index.row(), index.column()
        if r >= len(self._data) or c >= len(self._data[r]):
            return None

        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            return self._data[r][c]
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        if role == QtCore.Qt.BackgroundRole and (r, c) in self._flash_cells:
            return QtGui.QBrush(QtGui.QColor(90, 130, 200, 50))
        return None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid() or role != QtCore.Qt.EditRole:
            return False
        r, c = index.row(), index.column()
        # Ensure the row has enough columns
        while c >= len(self._data[r]):
            self._data[r].append("")
        self._data[r][c] = value
        self.dataChanged.emit(index, index, [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole])
        return True

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return (
            QtCore.Qt.ItemIsEnabled
            | QtCore.Qt.ItemIsSelectable
            | QtCore.Qt.ItemIsEditable
            | QtCore.Qt.ItemIsDragEnabled
            | QtCore.Qt.ItemIsDropEnabled
        )

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            if self._headers and section < len(self._headers):
                return self._headers[section]
            return f"Column {section+1}"
        return str(section + 1)

    def setHeaderData(self, section, orientation, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole and orientation == QtCore.Qt.Horizontal:
            # Grow headers list if needed
            if section >= len(self._headers):
                self._headers += [""] * (section - len(self._headers) + 1)
            self._headers[section] = value
            self.headerDataChanged.emit(orientation, section, section)
            return True
        return False

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction

    # ---------------------
    # Structure operations
    # ---------------------
    def insertRows(self, row, count=1, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        cols = self.columnCount()
        for _ in range(count):
            self._data.insert(row, [""] * cols)
        self.endInsertRows()
        self._flash_new_items([(row + i, c) for i in range(count) for c in range(cols)])
        return True

    def removeRows(self, row, count=1, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        for _ in range(count):
            if 0 <= row < len(self._data):
                self._data.pop(row)
        self.endRemoveRows()
        return True

    def insertColumns(self, column, count=1, parent=QtCore.QModelIndex()):
        self.beginInsertColumns(parent, column, column + count - 1)
        # Ensure headers exist
        if not self._headers:
            self._headers = [""] * self.columnCount()
        for _ in range(count):
            self._headers.insert(column, "")
        # Insert into each row
        for r in range(len(self._data)):
            for _ in range(count):
                self._data[r].insert(column, "")
        self.endInsertColumns()
        self._flash_new_items([(r, column + i) for r in range(len(self._data)) for i in range(count)])
        return True

    def removeColumns(self, column, count=1, parent=QtCore.QModelIndex()):
        self.beginRemoveColumns(parent, column, column + count - 1)
        for _ in range(count):
            if self._headers and 0 <= column < len(self._headers):
                self._headers.pop(column)
            for r in range(len(self._data)):
                if 0 <= column < len(self._data[r]):
                    self._data[r].pop(column)
        self.endRemoveColumns()
        return True

    def moveColumn(self, sourceColumn, destinationColumn):
        if sourceColumn == destinationColumn:
            return False
        self.beginMoveColumns(
            QtCore.QModelIndex(), sourceColumn, sourceColumn,
            QtCore.QModelIndex(),
            destinationColumn if destinationColumn < sourceColumn else destinationColumn + 1,
        )
        # Headers
        if self._headers:
            col = self._headers.pop(sourceColumn)
            insert_at = destinationColumn if destinationColumn < sourceColumn else destinationColumn
            self._headers.insert(insert_at, col)
        # Data
        for r in range(len(self._data)):
            val = self._data[r].pop(sourceColumn)
            insert_at = destinationColumn if destinationColumn < sourceColumn else destinationColumn
            self._data[r].insert(insert_at, val)
        self.endMoveColumns()
        return True

    # ---------------------
    # CSV I/O
    # ---------------------
    def load_from_csv(self, path):
        with open(path, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows:
            rows = [[]]
        headers = rows[0]
        data = rows[1:]

        # Normalize lengths
        max_cols = max([len(headers)] + [len(r) for r in data]) if data else len(headers)
        headers += [""] * (max_cols - len(headers))
        for i in range(len(data)):
            data[i] += [""] * (max_cols - len(data[i]))

        self.beginResetModel()
        self._headers = headers
        self._data = data
        self.endResetModel()

    def save_to_csv(self, path, order=None):
        """
        Save to CSV.
        - order: optional list mapping visual column order (e.g., [2, 0, 1, ...]).
        """
        max_cols = max([len(self._headers)] + [len(r) for r in self._data]) if self._data else len(self._headers)
        headers = self._headers + [""] * (max_cols - len(self._headers))
        rows = [r + [""] * (max_cols - len(r)) for r in self._data]

        if order:
            headers = [headers[i] for i in order]
            rows = [[row[i] for i in order] for row in rows]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

    # ---------------------
    # Visual nicety
    # ---------------------
    def _flash_new_items(self, coords, duration_ms=700):
        """Transient highlight for newly inserted cells."""
        if not coords:
            return
        self._flash_cells.update(coords)
        for (r, c) in coords:
            idx = self.index(r, c)
            self.dataChanged.emit(idx, idx, [QtCore.Qt.BackgroundRole])

        timer = QtCore.QTimer()
        timer.setSingleShot(True)

        def clear_flash():
            self._flash_cells.difference_update(coords)
            for (r, c) in coords:
                idx = self.index(r, c)
                self.dataChanged.emit(idx, idx, [QtCore.Qt.BackgroundRole])
            timer.deleteLater()

        timer.timeout.connect(clear_flash)
        timer.start(duration_ms)