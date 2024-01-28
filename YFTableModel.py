from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
import Constants as consts


class YFTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, hlabels, vlabels=None):
        import datetime as datetime
        super(YFTableModel, self).__init__()
        self._data = data
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.horizontal_header_labels = hlabels
        self.vertical_header_labels = vlabels

    def data(self, index, role):
        if not index.isValid():
            return None
        d = self._data[index.row()]
        col = index.column()
        data = d[col]
        # if role == Qt.BackgroundRole:
        #    return QtGui.QColor(consts.BEFORE_TAX_COLOR)

        if role == Qt.ForegroundRole:
            if (col == 7 or col == 8) and float(data) < 0:
                return QtGui.QColor('#ff0000')
            if "*" in str(d[1]):
                return QtGui.QColor(consts.CLOSED_POS_COLOR)
            if col == 11 and data > self.today:
                return QtGui.QColor('#0000ff')

        if role == Qt.TextAlignmentRole:
            if col > 1:
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter if (col < 2 or col > 9) else Qt.AlignRight | Qt.AlignVCenter
        if role != Qt.ItemDataRole.DisplayRole:
            # for all roles you're not interested in return python's None
            # which is interpreted as an invalid QVariant value
            return None
        # if isinstance(data, float) and (col >= 8 and col <= 10):
        #    return "{:.2f}".format(data)
        return data

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
        # if orientation == Qt.Vertical:
        #    return self.vertical_header_labels[section]
