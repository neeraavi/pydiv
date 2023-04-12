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
        d = self._data[index.row()]
        if role == Qt.BackgroundRole:
            if "Total" in str(d[0]):
                return QtGui.QColor(consts.TOTAL_COLOR)
        # if index.row() == 12:
        #    return QtGui.QColor('#ffe4c4')
        # if index.row() == 13:
        #    return QtGui.QColor('#ffffff')
        # if index.row() == 13:
        #    return QtGui.QColor('#e9edc9')
        if role == Qt.ForegroundRole:
            if "*" in str(d[1]):
                return QtGui.QColor("#ff0000")
        if role == Qt.TextAlignmentRole:
            colNum = index.column()
            return Qt.AlignRight
        if role != Qt.ItemDataRole.DisplayRole:
            # for all roles you're not interested in return python's None
            # which is interpreted as an invalid QVariant value
            return None
        return self._data[index.row()][index.column()]
