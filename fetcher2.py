from PyQt5.QtWidgets import QApplication, QTableView, QWidget, QVBoxLayout, QPushButton, QHeaderView
from PyQt5 import QtWidgets
from PyQt5.QtCore import QAbstractTableModel, Qt
import yfinance as yf
import csv
import json


class StockTableModel(QAbstractTableModel):
    def __init__(self, data, header, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data
        self._header = header

    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return len(self._data[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        value = self._data[index.row()][index.column()]
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value)

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._header[col]
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class StockApp(QWidget):
    def __init__(self):
        super().__init__()

        self.title = "Stock Price Fetcher"
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        # Read configuration file
        with open('config.json') as f:
            config = json.load(f)

        input_file = config['input_file']
        output_file = config['output_file']

        # Read input file
        with open(input_file) as f:
            reader = csv.reader(f)
            data = list(reader)

        # Fetch current prices from Yahoo Finance
        for row in data[1:]:
            symbol = row[0]
            nos = int(row[1])
            cost = float(row[2])
            stock = yf.Ticker(symbol)
            # row[2] = stock.info['regularMarketPrice']
            print(stock.info['previousClose'])
            print(stock.info['exDividendDate'])
            print(symbol)
            last_price = stock.history(period="1d")["Close"][-1]
            current_value = nos * last_price
            gain = float(current_value) - cost
            gain_pc = gain / cost * 100
            ex_div = stock.info['exDividendDate']
            row.extend([current_value, gain, gain_pc, ex_div])

        # Set up table view
        header = data[0]
        data = data[1:]
        self.table_model = StockTableModel(data, header)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)

        # Set column formatting
        self.table_view.setItemDelegate(FormatDelegate())
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.table_view)

        # Add print button
        print_button = QPushButton("Print")
        print_button.clicked.connect(lambda: self.print_to_file(output_file))
        layout.addWidget(print_button)

        self.setLayout(layout)
        self.show()

    def print_to_file(self, output_file):
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.table_model._header)
            for row in self.table_model._data:
                writer.writerow(row)


class FormatDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value)


if __name__ == '__main__':
    app = QApplication([])
    ex = StockApp()
    app.exec_()
