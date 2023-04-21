from PyQt5 import QtGui
from PyQt5.QtCore import Qt

import Constants as consts
from TransactionModel import TransactionModel


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
            elif row == 13:
                return QtGui.QColor(consts.AVG_ROW_COLOR)
            elif row == 14:
                return QtGui.QColor(consts.NEXT_COLOR)
            rem = row % 3
            if rem == 0:
                return QtGui.QColor('white')
            if rem == 1:
                return QtGui.QColor('#e9f5db')
            if rem == 2:
                return QtGui.QColor('#cfe1b9')
        if role == Qt.ForegroundRole:
            if "*" in str(d[1]):
                return QtGui.QColor("#ff0000")
        if role == Qt.TextAlignmentRole:
            return Qt.AlignRight | Qt.AlignVCenter
        if role != Qt.ItemDataRole.DisplayRole:
            # for all roles you're not interested in return python's None
            # which is interpreted as an invalid QVariant value
            return None
        col = index.column()
        return d[col]
