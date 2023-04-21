import csv
import yfinance as yf
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QPushButton
from PyQt5.QtCore import Qt, QAbstractTableModel


class StockTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.header = ['Symbol', 'Name', 'Shares', 'Total Cost', 'Next Div', 'Current Price', 'Gain', 'Percentage Gain']

    def data(self, index, role):
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return str(self._data[row][col])
        return None

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self.header):
                    return self.header[section]
            # else:
            #    return str(section + 1)
        return None


class StockTable(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stock Price Fetcher")
        self.setGeometry(0, 0, 800, 600)

        self.table = QTableView(self)
        self.table.setGeometry(10, 10, 780, 530)
        self.table.setModel(StockTableModel(self.get_stock_data()))

        self.print_button = QPushButton("Print", self)
        self.print_button.setGeometry(10, 550, 780, 40)
        self.print_button.clicked.connect(self.print_table_data)

        self.show()

    def get_stock_data(self):
        data = []
        with open('symbols.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            for row in reader:
                symbol = row[0]
                shares = int(row[1])
                total_cost = float(row[2])

                stock = yf.Ticker(symbol)
                # current_price = stock.info['regularMarketPrice']
                current_price = stock.history(period="1d")["Close"][-1]
                print(current_price)
                # last_quote = data['Close'].iloc[-1]
                current_value = shares * current_price
                gain = current_value - total_cost
                percentage_gain = (gain / total_cost) * 100
                print(stock.dividends.tail(1))
                dividends = stock.dividends
                next_dividend_date = None
                for dividend_date in dividends.index:
                    if dividend_date > stock.info['regularMarketTime']:
                        next_dividend_date = dividend_date
                        break

                # dividend_date = stock.dividends.tail(1).index[0].strftime('%Y-%m-%d')

                data.append(
                    [symbol, stock.info['shortName'], shares, total_cost, next_dividend_date, current_price, gain,
                     percentage_gain])

        return data

    def print_table_data(self):
        with open('out.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(StockTableModel(self.get_stock_data()).header)
            for row in StockTableModel(self.get_stock_data())._data:
                writer.writerow(row)


if __name__ == '__main__':
    app = QApplication([])
    window = StockTable()
    app.exec_()
