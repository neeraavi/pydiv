from TransactionModel import TransactionModel
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
import columnNames as consts


class CalendarModel(TransactionModel):
    def __init__(self, data, hlabels, vlabels=[]):
        super(CalendarModel, self).__init__(data, hlabels, vlabels)

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        d = self._data[row]
        col = index.column()
        if role == Qt.BackgroundRole:
            if row == 12:
                return QtGui.QColor(consts.TOTAL_COLOR)
            if row == 13:
                return QtGui.QColor(consts.NEXT_COLOR)
        if role == Qt.ForegroundRole:
            if '*' in str(d[1]):
                return QtGui.QColor('#ff0000')
        if role == Qt.TextAlignmentRole:
            return Qt.AlignRight | Qt.AlignVCenter
        if role != Qt.ItemDataRole.DisplayRole:
            # for all roles you're not interested in return python's None
            # which is interpreted as an invalid QVariant value
            return None
        col = index.column()
        return self._data[index.row()][index.column()]
