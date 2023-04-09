from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView


class TransactionModel(QtCore.QAbstractTableModel):
    def __init__(self, data, hlabels, vlabels=None):
        super(TransactionModel, self).__init__()
        self._data = data
        self.horizontal_header_labels = hlabels
        self.vertical_header_labels = vlabels

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        d = self._data[row]
        if role == Qt.BackgroundRole:
            if 'Total' in str(d[0]):
                return QtGui.QColor('#ffe4c4')
        if role == Qt.ForegroundRole:
            if '*' in str(d[1]):
                return QtGui.QColor('#9c6644')
        if role == Qt.TextAlignmentRole:
            colNum = index.column()
            return Qt.AlignLeft if (colNum < 2) else Qt.AlignRight
        if role != Qt.ItemDataRole.DisplayRole:
            # for all roles you're not interested in return python's None
            # which is interpreted as an invalid QVariant value
            return None
        if col == 4:
            return "{:.2f}".format(self._data[index.row()][col])
        return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data) if self._data else 0

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0]) if self._data and len(self._data) > 0 else 0

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.horizontal_header_labels[section]
        if orientation == Qt.Vertical:
            return self.vertical_header_labels[section]
