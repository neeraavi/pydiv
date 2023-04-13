from TransactionModel import TransactionModel
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import columnNames as consts


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
        # if index.row() == 12:
        #    return QtGui.QColor('#ffe4c4')
        # if index.row() == 13:
        #    return QtGui.QColor('#ffffff')
        # if index.row() == 13:
        #    return QtGui.QColor('#e9edc9')
        if role == Qt.ForegroundRole:
            # if col == 0:
            if n.startswith('.'):
                return QtGui.QColor(consts.NEW_DIV_COLOR)
            if n.startswith('~'):
                return QtGui.QColor(consts.EXPECTED_DIV_COLOR)
        if role == Qt.TextAlignmentRole:
            # colNum = index.column()
            return Qt.AlignRight
        if role != Qt.ItemDataRole.DisplayRole:
            # for all roles you're not interested in return python's None
            # which is interpreted as an invalid QVariant value
            return None
        val = self._data[index.row()][col]
        if col == consts.DIV_AFTER or col == consts.DIV_BEFORE:
            return "{:.2f}".format(val)
        # if col == consts.DPS :
        #    print('xx', val)
        # return "{:.3f}".format(val)
        return val
