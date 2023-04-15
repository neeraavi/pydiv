from PyQt5 import QtGui
from PyQt5.QtCore import Qt

import Constants as consts
from TransactionModel import TransactionModel


class SectorDetailsModel(TransactionModel):
    def __init__(self, data, hlabels, vlabels=[]):
        super(SectorDetailsModel, self).__init__(data, hlabels, vlabels)

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        d = self._data[row]
        n = str(d[0])
        col = index.column()
        if role == Qt.BackgroundRole:
            if "Total" in n:
                return QtGui.QColor(consts.TOTAL_COLOR)
        if role == Qt.TextAlignmentRole:
            if col > 0:
                return Qt.AlignRight | Qt.AlignVCenter
            else:
                return Qt.AlignLeft | Qt.AlignVCenter
        if role != Qt.ItemDataRole.DisplayRole:
            # for all roles you're not interested in return python's None
            # which is interpreted as an invalid QVariant value
            return None
        return d[col]
