from PyQt5 import QtGui
from PyQt5.QtCore import Qt

import Constants as consts
from TransactionModel import TransactionModel


class SectorModel(TransactionModel):
    def __init__(self, data, hlabels, vlabels=[]):
        super(SectorModel, self).__init__(data, hlabels, vlabels)

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        d = self._data[row]
        col = index.column()
        if role == Qt.BackgroundRole:
            if "Total" in str(d[0]):
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
        if col == 2:
            alloc = "{m:0.0f} %".format(m=d[col])
            return alloc
        return d[col]
