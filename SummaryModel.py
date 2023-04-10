from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
import columnNames as consts


class SummaryModel(QtCore.QAbstractTableModel):
    def __init__(self, data, hlabels, vlabels=None):
        super(SummaryModel, self).__init__()
        self._data = data
        self.horizontal_header_labels = hlabels
        self.vertical_header_labels = vlabels

    def data(self, index, role):
        if not index.isValid():
            return None
        d = self._data[index.row()]
        col = index.column()
        if role == Qt.BackgroundRole:
            if col == consts.SMRY_ALLOC:
                return QtGui.QColor(consts.ALLOC_COLOR)
            if col == consts.SMRY_ANN_DIV_A or col == consts.SMRY_YOC_A:
                return QtGui.QColor(consts.AFTER_TAX_COLOR)
            if col == consts.SMRY_ANN_DIV_B or col == consts.SMRY_YOC_B:
                return QtGui.QColor(consts.BEFORE_TAX_COLOR)
            if col == 1:
                div_change = d[1]
                if consts.SIGN_INCR == div_change:
                    return QtGui.QColor(consts.INCR_COLOR)
                elif consts.SIGN_SAME in div_change:
                    return QtGui.QColor(consts.SAME_COLOR)
                elif '' == div_change:
                    return QtGui.QColor(consts.UNKNOWN_COLOR)
                elif consts.SIGN_DECR in div_change:
                    return QtGui.QColor(consts.DECR_COLOR)

        if role == Qt.ForegroundRole:
            if '*' in str(d[1]):
                return QtGui.QColor(consts.CLOSED_POS_COLOR)
        if role == Qt.TextAlignmentRole:
            colNum = index.column()
            return Qt.AlignLeft if (colNum < 2 or colNum > 9) else Qt.AlignRight
        if role != Qt.ItemDataRole.DisplayRole:
            # for all roles you're not interested in return python's None
            # which is interpreted as an invalid QVariant value
            return None
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
