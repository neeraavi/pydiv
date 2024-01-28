import csv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import yfinance as yf
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QPushButton
from PyQt5.QtCore import Qt, QAbstractTableModel


class StockTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.header = ['Ticker', 'Name', '#', 'Invested', 'CPS', 'Current', 'Value', 'Gain', 'Gain%', 'Div', 'Div%',
                       'Date', 'FXRate']

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
    def __init__x(self):
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


class Tickers():
    def __init__(self):
        self.header = ['Ticker', 'Name', '#', 'Invested', 'CPS', 'Current', 'Value', 'Gain', 'Gain%', 'Div', 'Div%',
                       'Date', 'FXRate']
        self.get_conversion_rates()
        self.remap_init()
        self.read_tickers()
        self.fetch_and_write_stock_data()

    def get_conversion_rates(self):
        data = yf.download(tickers='EURUSD=X', period='15m')
        c = data['Close']
        self.eur_to_usd = float(c.iloc[0])
        data = yf.download(tickers='EURCAD=X', period='15m')
        c = data['Close']
        self.eur_to_cad = float(c.iloc[0])
        data = yf.download(tickers='EURSGD=X', period='15m')
        c = data['Close']
        self.eur_to_sgd = float(c.iloc[0])

    def read_tickers(self):
        self.data = []
        with open('/home/iyerns/tmp/out/summary_table.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            for row in reader:
                symbol = row[0]
                shares = int(row[1])
                total_cost = float(row[2])
                self.data.append([symbol, shares, total_cost])

    def remap_init(self):
        self.remapper_usd = {
            'ALT': 'MO',
            'NUC': 'NUE',
            'BAT': 'BTI',
            'BAE': 'BAESY',
            'BNS2': 'BNS',
            'VIA': 'VTRS',
            'RBC': 'RY',
            'MANU': 'MFC',
            'ARES': 'ARCC',
            'MEDI': 'MED',
            'FORT': 'FTS',
            'CNR': 'CNQ'}
        self.remapper_cad = {
            'CUD': 'CU.TO',
            'CIBC': 'CM.TO',
            'EMA.TO': 'EMA.TO',
            'TRP.TO': 'TRP.TO',
            'POW.TO': 'POW.TO'}
        self.remapper_sig = {
            'DBS': 'D05.SI'}
        self.remapper_eur = {
            'MBG': 'MBG.DE',
            'BMW': 'BMW.DE',
            # 'SSE': 'SCT.MU',
            'BYR': 'BAYN.DE',
            'ALV': 'ALV.DE',
            'BASF': 'BAS.DE',
            'DPW': 'DPW.DE',
            'MUV2': 'MUV2.DE'}
        self.no_map = ['GAZ', 'EMUD', 'T.TO', 'GOV', 'HAB', 'SSE']
        self.remapper = self.remapper_usd | self.remapper_cad | self.remapper_sig | self.remapper_eur
        self.remapper_keys = list(self.remapper)

    def remap(self, ticker):
        if ticker in self.no_map:
            return None, None
        elif ticker in self.remapper_usd.keys():
            return self.remapper[ticker], self.eur_to_usd
        elif ticker in self.remapper_sig.keys():
            return self.remapper[ticker], self.eur_to_sgd
        elif ticker in self.remapper_cad.keys():
            print(ticker, self.eur_to_cad)
            return self.remapper[ticker], self.eur_to_cad
        elif ticker in self.remapper_eur.keys():
            print(ticker, '---euro')
            return self.remapper[ticker], 1
        else:
            return ticker, self.eur_to_usd

    def fetch_and_write_stock_data(self):
        tickers = ''
        for row in self.data:
            ticker = row[0].upper().strip()
            ticker, conversion_rate = self.remap(ticker)
            print(ticker, conversion_rate)
            tickers = f'{tickers} {ticker}'

        with open('/home/iyerns/tmp/out/stock_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.header)
            self.fetch_stock_data(tickers, writer, file)

    def fetch(self, tickers):
        result = yf.Tickers(tickers)
        print(result)
        return result

    def fetch_stock_data(self, tickers, writer, filename):
        with ThreadPoolExecutor() as executor:
            executor.map(self.fetch, tickers)

        result = self.fetch(tickers)
        # result = yf.Tickers(tickers)
        # print(result)
        for row in self.data:
            ticker = row[0].upper().strip()
            modified_ticker, conversion_rate = self.remap(ticker)
            print(ticker, modified_ticker, conversion_rate)
            if modified_ticker is None:
                continue
            info = result.tickers[modified_ticker].info
            shortName = info['shortName']
            curr_div_rate = ''
            dividendYield = ''
            exDividendDate = ''
            lastDividendDate = ''
            divDate = ''
            if 'dividendRate' in info:
                curr_div_rate = info['dividendRate']
                dividendYield = info['dividendYield'] * 100
                edv = info['exDividendDate']
                exDividendDate = datetime.fromtimestamp(edv).strftime('%Y-%m-%d')
                # exDividendDate = datetime.fromtimestamp(edv).date()
                ldv = info['lastDividendDate']
                lastDividendDate = datetime.fromtimestamp(ldv).strftime('%Y-%m-%d')
                divDate = max([exDividendDate, lastDividendDate])
            # lastDividendDate = datetime.fromtimestamp(ldv).date()
            current_price = info['currentPrice'] / conversion_rate
            # currency USD
            # print(ticker, result.tickers[ticker].info)
            nos = row[1]
            invested = row[2]
            # current_price = result.tickers[ticker].history(period="1d")["Close"][-1]
            current_value = nos * current_price
            gain = current_value - invested
            percentage_gain = (gain / invested) * 100
            cps = invested / nos
            print([ticker, shortName, nos, invested, round(cps),
                   '{0:.2f}'.format(current_price),
                   '{0:.2f}'.format(current_value),
                   '{0:.2f}'.format(gain),
                   '{0:.2f}'.format(percentage_gain),
                   curr_div_rate, dividendYield,
                   exDividendDate, lastDividendDate, conversion_rate])
            writer.writerow([ticker, shortName, str(nos), str(invested), str(round(cps)),
                             '{0:.2f}'.format(current_price),
                             '{0:.2f}'.format(current_value),
                             '{0:.2f}'.format(gain),
                             '{0:.2f}'.format(percentage_gain),
                             '{0:.2f}'.format(curr_div_rate),
                             '{0:.2f}'.format(dividendYield),
                             divDate,
                             '{0:.2f}'.format(conversion_rate)])

        # last_quote = data['Close'].iloc[-1]
        # print(stock.dividends.tail(1))
        # dividends = stock.dividends
        # next_dividend_date = None
        # for dividend_date in dividends.index:
        #    if dividend_date > stock.info['regularMarketTime']:
        #        next_dividend_date = dividend_date
        #        break

    # dividend_date = stock.dividends.tail(1).index[0].strftime('%Y-%m-%d')

    # data.append(
    #    [symbol, stock.info['shortName'], shares, total_cost, next_dividend_date, current_price,
    #     current_value, gain, percentage_gain])
    #
    # return data

    def print_table_data(self):
        with open('out.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(StockTableModel(self.get_stock_data()).header)
            for row in StockTableModel(self.get_stock_data())._data:
                writer.writerow(row)


if __name__ == '__main__':
    # app = QApplication([])
    # window = StockTable()
    # app.exec_()
    t = Tickers()
