from TransactionModel import TransactionModel
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import columnNames as consts


class DividendModel(TransactionModel):
    def __init__(self, data, hlabels, vlabels=[]):
        super(DividendModel, self).__init__(data, hlabels, vlabels)

    def data(self, index, role):
        if not index.isValid():
            return None
        d = self._data[index.row()]
        col = index.column()
        if role == Qt.BackgroundRole:
            if "Total" in str(d[0]):
                return QtGui.QColor(consts.TOTAL_COLOR)
            if "Next" in str(d[0]):
                return QtGui.QColor(consts.NEXT_COLOR)
            if col == consts.DIV_AFTER or col == consts.DIV_YOC_A:
                return QtGui.QColor(consts.AFTER_TAX_COLOR)
            if col == consts.DIV_BEFORE or col == consts.DIV_YOC_B:
                return QtGui.QColor(consts.BEFORE_TAX_COLOR)
            return QtGui.QColor("#ffffff")

        if role == Qt.ForegroundRole:
            if "*" in str(d[1]):
                return QtGui.QColor("#ff0000")
        if role == Qt.TextAlignmentRole:
            # colNum = index.column()
            return Qt.AlignRight | Qt.AlignVCenter
        if role != Qt.ItemDataRole.DisplayRole:
            # for all roles you're not interested in return python's None
            # which is interpreted as an invalid QVariant value
            return None
        col = index.column()
        if col == 4:
            d = self._data[index.row()][index.column()]
            if isinstance(d, float):
                return "{:.3f}".format(d)
            return d
        if col == 5 or col == 7:
            # print(self._data[index.row()][index.column()])
            return "{:.2f}".format(self._data[index.row()][index.column()])
        return self._data[index.row()][index.column()]
