from operator import itemgetter

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
import sys

import dividends
from divui import Ui_MainWindow
import transactions
from datetime import datetime
from TableModel import TableModel
from CalendarModel import CalendarModel
from CalendarDetailsModel import CalendarDetailsModel
from DividendModel import DividendModel


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.now = datetime.now()
        self.startYear = 2015
        self.totalInvested = 0
        self.transactions = None
        self.transactionMap = {}
        self.transactionsProxyModel = None
        self.transactionsSourceModel = None
        self.pathPrefix = '/home/iyerns/tmp/PycharmProjects/pythonProject/tmp'
        self.sourceModel = None
        self.proxyModel = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btn_1.setText("ff")
        self.ui.btn_1.clicked.connect(self.close)
        self.fill_summary_table()
        self.shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Find), self)
        self.shortcut.activated.connect(self.ui.mainFilter.setFocus)
        self.closeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Quit), self)
        self.closeShortcut.activated.connect(self.close)
        self.closeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Cancel), self)
        self.closeShortcut.activated.connect(self.reset_main_filter)
        self.ui.summaryView.setStyleSheet("alternate-background-color: #fefae0; background-color: white;")

    def fill_summary_table(self):
        # transaction calculations
        t = transactions.Transactions(self.startYear, self.pathPrefix)
        t.fill_transactions()
        self.update_transaction_calendar(t)
        (self.transactions, self.transactionMap, self.totalInvested, summaryHeader) = t.get_transaction_results()

        # dividend calculations
        d = dividends.Dividends(self.startYear, self.pathPrefix, self.transactions)
        d.fill_dividends()
        (self.dividendMap, self.dividendHeader) = d.get_dividend_results()

        # display transactions
        self.sourceModel = TableModel(self.transactions, summaryHeader)
        self.proxyModel = QtCore.QSortFilterProxyModel(self)
        self.proxyModel.setFilterKeyColumn(-1)  # Search all columns.
        self.proxyModel.setSourceModel(self.sourceModel)
        self.proxyModel.sort(0, Qt.AscendingOrder)
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.ui.mainFilter.textChanged.connect(self.ticker_filter_changed)
        self.ui.summaryView.setModel(self.proxyModel)
        self.ui.summaryView.selectionModel().selectionChanged.connect(self.main_selection_changed)
        self.ui.summaryView.resizeColumnsToContents()
        self.ui.summaryView.show()

    def update_transaction_calendar(self, t):
        (self.investmentCalendar, investment_calendar_header, month_header) = t.get_investment_calendar()
        self.investmentCalendarModel = CalendarModel(self.investmentCalendar, investment_calendar_header, month_header)
        ##self.ui.investmentCalendarView.setModel(self.investmentCalendarModel)
        # self.ui.investmentCalendarView.setColumnWidth(1, 100)
        # self.ui.investmentCalendarView.horizontalHeader().setMaximumWidth(40)
        # self.ui.investmentCalendarView.horizontalHeader().setMinimumWidth(30)

        proxyModel = QtCore.QSortFilterProxyModel(self)
        proxyModel.setFilterKeyColumn(-1)  # Search all columns.
        proxyModel.setSourceModel(self.investmentCalendarModel)
        self.ui.investmentCalendarView.setModel(proxyModel)
        self.ui.investmentCalendarView.selectionModel().selectionChanged.connect(self.inv_cal_selection_changed)
        self.ui.investmentCalendarView.horizontalHeader().setStretchLastSection(False)
        self.ui.investmentCalendarView.resizeColumnsToContents()
        self.ui.investmentCalendarView.setStyleSheet("alternate-background-color: #fefae0; background-color: white;")
        self.ui.investmentCalendarView.clicked.connect(self.investment_calendar_clicked)

    def inv_cal_selection_changed(self, selected, deselected):
        for idx in selected.indexes():
            r = idx.row()
            c = idx.column()
            self.redisplay_investment(r + 1, self.now.year - c)

    def investment_calendar_clicked(self, item):
        m = 1 + item.row()
        y = self.now.year - item.column()
        self.redisplay_investment(m, y)

    def redisplay_investment(self, m, y):
        if m > 13:
            return

        ym = '{y}-{m:02d}'.format(m=m, y=y)
        # print(ym)
        result = [row for ticker, t_list in self.transactionMap.items() for row in t_list if ym in row[2]]
        result = sorted(result, key=itemgetter(2))
        # print(result)
        header = ['Ticker', 'B/S', 'Date', '#', 'Cost', 'CPS', 'Sign', 'z']
        self.calendarDetailsModel = CalendarDetailsModel(result, header, [])
        self.ui.calendarDetailsMode.setText(f'Investments in {ym}')
        self.ui.calendarDetailsView.setModel(self.calendarDetailsModel)
        self.ui.calendarDetailsView.setColumnHidden(6, True)
        self.ui.calendarDetailsView.resizeColumnsToContents()
        self.ui.calendarDetailsView.show()

    def reset_main_filter(self):
        self.ui.mainFilter.setFocus()
        self.ui.mainFilter.setText('')

    def ticker_filter_changed(self, new_filter):
        self.proxyModel.setFilterFixedString(new_filter)
        self.display_filtered_transactions(new_filter)
        self.display_filtered_dividends(new_filter)

    def display_filtered_dividends(self, ticker):
        if ticker not in self.dividendMap:
            return
        filtered = self.dividendMap[ticker]
        # print(ticker, filtered)
        self.dividendSourceModel = DividendModel(filtered, self.dividendHeader)
        self.ui.dividendsView.setModel(self.dividendSourceModel)
        # self.ui.transactionsView.setColumnHidden(6, True)
        self.ui.dividendsView.resizeColumnsToContents()
        self.ui.dividendsView.scrollToBottom()
        self.ui.dividendsView.show()

    def display_filtered_transactions(self, ticker):
        if ticker not in self.transactionMap:
            return
        filtered = self.transactionMap[ticker]
        # print(ticker, filtered)
        self.transactionsSourceModel = TableModel(filtered,
                                                  ['Ticker', 'B/S', 'Date', '#', 'Cost', 'CPS', 'Sign', 'z'])
        self.ui.transactionsView.setModel(self.transactionsSourceModel)
        self.ui.transactionsView.setColumnHidden(6, True)
        self.ui.transactionsView.resizeColumnsToContents()
        self.ui.transactionsView.scrollToBottom()
        self.ui.transactionsView.show()

    def main_selection_changed(self, selected, deselected):
        if len(selected.indexes()) > 0:
            ticker = selected.indexes()[0].data()
            print("selected: ", ticker)
            self.display_filtered_transactions(ticker)
            self.display_filtered_dividends(ticker)


def create_app():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    win.ui.mainFilter.setFocus()
    sys.exit(app.exec_())


if __name__ == '__main__':
    create_app()
