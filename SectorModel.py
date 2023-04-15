from TransactionModel import TransactionModel
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
import columnNames as consts


class SectorModel(TransactionModel):
    def __init__(self, data, hlabels, vlabels=[]):
        super(SectorModel, self).__init__(data, hlabels, vlabels)

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        d = self._data[row]
        n = str(d[0])
        col = index.column()
        if role == Qt.BackgroundRole:
            if "Total" in n :
                return QtGui.QColor(consts.TOTAL_COLOR)
        # if role == Qt.BackgroundRole:
        #    if row == 12:
        #        return QtGui.QColor(consts.TOTAL_COLOR)
        #    if row == 13:
        #        return QtGui.QColor(consts.AVG_ROW_COLOR)
        #    if row == 14:
        #        return QtGui.QColor(consts.NEXT_COLOR)
        # if role == Qt.ForegroundRole:
        #    if "*" in str(d[1]):
        #        return QtGui.QColor("#ff0000")
        if role == Qt.TextAlignmentRole:
            if col > 0:
                return Qt.AlignRight | Qt.AlignVCenter
            else:
                return Qt.AlignLeft | Qt.AlignVCenter
        if role != Qt.ItemDataRole.DisplayRole:
            # for all roles you're not interested in return python's None
            # which is interpreted as an invalid QVariant value
            return None
        if col == 2:
            alloc = "{m:0.0f} %".format(m=self._data[row][col])
            return alloc
        return self._data[row][col]