from TransactionModel import TransactionModel
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import Constants as consts


class CalendarDetailsModel(TransactionModel):
    def __init__(self, data, hlabels, vlabels):
        super(CalendarDetailsModel, self).__init__(data, hlabels, vlabels)

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        d = self._data[row]
        n = str(d[0])
        if role == Qt.BackgroundRole:
            if "Total" in n:
                return QtGui.QColor(consts.TOTAL_COLOR)
            if "##" in n:
                return QtGui.QColor(consts.EXPECTED_TOTAL_MDIV_COLOR)
            if "Expected" in n:
                return QtGui.QColor(consts.EXPECTED_DIV_COLOR_BG)

        if role == Qt.ForegroundRole:
            if n.startswith('.'):
                return QtGui.QColor(consts.NEW_DIV_COLOR)
            elif n.startswith('~'):
                return QtGui.QColor(consts.EXPECTED_DIV_COLOR)
        if role == Qt.TextAlignmentRole:
            return Qt.AlignRight | Qt.AlignVCenter
        if role != Qt.ItemDataRole.DisplayRole:
            # for all roles you're not interested in return python's None
            # which is interpreted as an invalid QVariant value
            return None
        val = d[col]
        if isinstance(val, float):
            return "{:.2f}".format(val)
        return val
