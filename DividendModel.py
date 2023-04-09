from TransactionModel import TransactionModel
from PyQt5 import QtGui
from PyQt5.QtCore import Qt


class DividendModel(TransactionModel):
    def __init__(self, data, hlabels, vlabels=[]):
        super(DividendModel, self).__init__(data, hlabels, vlabels)

    def data(self, index, role):
        if not index.isValid():
            return None
        d = self._data[index.row()]
        col = index.column()
        if role == Qt.BackgroundRole:
            # if index.row() == 12:
            #    return QtGui.QColor('#ffe4c4')
            if 'Total' in str(d[0]):
                return QtGui.QColor('bisque')
            if 'Next' in str(d[0]):
                return QtGui.QColor('tan')
            # if index.row() % 2 == 0:
            if col == 5 or col == 6:
                return QtGui.QColor('seashell')
            if col == 7 or col == 8:
                return QtGui.QColor('wheat')
            return QtGui.QColor('#ffffff')
            # else:
            #    return QtGui.QColor('#f0ead2')
            # if index.row() == 13:
            #    return QtGui.QColor('#e9edc9')
        if role == Qt.ForegroundRole:
            if '*' in str(d[1]):
                return QtGui.QColor('#ff0000')
        if role == Qt.TextAlignmentRole:
            # colNum = index.column()
            return Qt.AlignRight
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
