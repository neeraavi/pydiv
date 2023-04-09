from operator import itemgetter

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QHeaderView, QLabel, QFrame
import sys

import dividends
from SummaryModel import SummaryModel
from divui import Ui_MainWindow
import transactions
from datetime import datetime
from TransactionModel import TransactionModel
from CalendarModel import CalendarModel
from CalendarDetailsModel import CalendarDetailsModel
from DividendModel import DividendModel


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self._label_ = []
        self.dividendSourceModel = None
        self.calendarDetailsModel = None
        self._visible_tickers_active_only = None
        self._visible_tickers_all = None
        self.summary_active_positions_only = None
        self.visible_tickers = None
        self.selected_summary = None
        self.now = datetime.now()
        self.startYear = 2015
        self.totalInvested = 0
        self.summary = None
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

        self.shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Find), self)
        self.shortcut.activated.connect(self.ui.mainFilter.setFocus)
        self.closeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Quit), self)
        self.closeShortcut.activated.connect(self.close)
        self.closeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Cancel), self)
        self.closeShortcut.activated.connect(self.reset_main_filter)
        # self.ui.summaryView.setStyleSheet("alternate-background-color: #fefae0; background-color: white;")
        # self.ui.summaryView.setStyleSheet("""QTableView {  gridline-color: #F2D2BD;}""")
        self.ui.showClosedPositions.stateChanged.connect(self.show_closed_positions_changed)

        self.create_status_bar()
        self.fill_summary_table()

    def show_closed_positions_changed(self):
        if not self.ui.showClosedPositions.isChecked():
            self.selected_summary = self.summary_active_positions_only
            self.visible_tickers = self._visible_tickers_active_only
        else:
            self.selected_summary = self.summary
            self.visible_tickers = self._visible_tickers_all

        self.sourceModel = SummaryModel(self.selected_summary, self.summaryHeader)
        self.proxyModel.setSourceModel(self.sourceModel)

    def fill_summary_table(self):
        # transaction calculations
        t = transactions.Transactions(self.startYear, self.pathPrefix)
        t.fill_transactions()
        self.update_transaction_calendar(t)
        (self.summary, self.transactionMap, self.totalInvested, self.summaryHeader) = t.get_transaction_results()
        self.summary_active_positions_only = [x for x in self.summary if x[1] != '*']
        self._label_[0].setText(f'Active#  {len(self.summary_active_positions_only)}')
        self._label_[1].setText(f'Invested:  {self.totalInvested}')
        self._visible_tickers_all = [x[0] for x in self.summary]
        self._visible_tickers_active_only = [x[0] for x in self.summary if x[1] != '*']

        # dividend calculations
        d = dividends.Dividends(self.startYear, self.pathPrefix, self.summary, self.totalInvested)
        d.fill_dividends()
        (self.dividendMap, self.dividendHeader, annual_div_a, annual_div_b) = d.get_dividend_results()
        self.update_status_bar(annual_div_a, annual_div_b)

        # display transactions
        self.proxyModel = QtCore.QSortFilterProxyModel(self)
        self.show_closed_positions_changed()
        self.proxyModel.setFilterKeyColumn(-1)  # Search all columns.
        self.proxyModel.sort(0, Qt.AscendingOrder)
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.ui.mainFilter.textChanged.connect(self.ticker_filter_changed)
        self.ui.summaryView.setModel(self.proxyModel)
        self.ui.summaryView.selectionModel().selectionChanged.connect(self.main_selection_changed)
        # self.ui.summaryView.setWordWrap(False)
        ##self.ui.summaryView.setColumnHidden(1, True)
        # self.ui.summaryView.horizontalHeader().setMinimumWidth(10)
        # self.ui.summaryView.horizontalHeader().setMaximumWidth(20)
        ##self.ui.summaryView.resizeColumnsToContents()
        # self.ui.summaryView.setColumnWidth(0, 25)
        # self.ui.summaryView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # .verticalHeader()->setSectionResizeMode(QHeaderView::ResizeToContents);
        ##self.ui.summaryView.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.ui.summaryView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.summaryView.horizontalHeader().setSectionResizeMode(12,
                                                                    QtWidgets.QHeaderView.ResizeToContents)
        for col in range(10):
            self.ui.summaryView.horizontalHeader().setSectionResizeMode(col,
                                                                        QtWidgets.QHeaderView.ResizeToContents)

        self.ui.summaryView.show()
        index = self.ui.summaryView.model().index(0, 0)
        self.ui.summaryView.setCurrentIndex(index)
        # for col in range(10):
        #    self.ui.summaryView.setColumnWidth(col, 40)

    def update_status_bar(self, annual_div_a, annual_div_b):
        t = 'FwdAnnDivA:  {m:0.0f}'.format(m=annual_div_a)
        self._label_[5].setText(t)
        annual_div_after_deduction_claim = annual_div_a + 2000
        t = 'FwdAnnDivA:  {m:0.0f}'.format(m=annual_div_after_deduction_claim)
        self._label_[6].setText(t)
        t = 'YoC_A:  {m:0.2f}%'.format(m=annual_div_after_deduction_claim / self.totalInvested * 100)
        self._label_[7].setText(t)
        t = 'FwdAnnDivM:  {m:0.0f}'.format(m=annual_div_after_deduction_claim / 12)
        self._label_[8].setText(t)
        # self._sb_annual_div_a.setText(t)

        t = 'FwdAnnDivB:  {m:0.0f}'.format(m=annual_div_b)
        self._label_[2].setText(t)
        t = 'YoC_B:  {m:0.2f}%'.format(m=annual_div_b / self.totalInvested * 100)
        self._label_[3].setText(t)
        t = 'FwdAnnDivM:  {m:0.0f}'.format(m=annual_div_b / 12)
        self._label_[4].setText(t)

    def update_transaction_calendar(self, t):
        (self.investmentCalendar, investment_calendar_header, month_header) = t.get_investment_calendar()
        self.investmentCalendarModel = CalendarModel(self.investmentCalendar, investment_calendar_header, month_header)
        ##self.ui.investmentCalendarView.setModel(self.investmentCalendarModel)
        # self.ui.investmentCalendarView.setColumnWidth(1, 100)
        # self.ui.investmentCalendarView.horizontalHeader().setMaximumWidth(40)
        # self.ui.investmentCalendarView.horizontalHeader().setMinimumWidth(30)

        proxy_model = QtCore.QSortFilterProxyModel(self)
        proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        proxy_model.setSourceModel(self.investmentCalendarModel)
        self.ui.investmentCalendarView.setModel(proxy_model)
        self.ui.investmentCalendarView.selectionModel().selectionChanged.connect(self.inv_cal_selection_changed)
        self.ui.investmentCalendarView.horizontalHeader().setStretchLastSection(False)
        self.ui.investmentCalendarView.resizeColumnsToContents()
        self.ui.investmentCalendarView.setStyleSheet("alternate-background-color: #fefae0; background-color: white;")
        self.ui.investmentCalendarView.clicked.connect(self.investment_calendar_clicked)

    def inv_cal_selection_changed(self, selected):
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
        if ticker not in self.dividendMap or ticker not in self.visible_tickers:
            self.ui.dividendsView.setVisible(False)
            return

        filtered = self.dividendMap[ticker]
        # print(ticker, filtered)
        self.dividendSourceModel = DividendModel(filtered, self.dividendHeader)
        self.ui.dividendsView.setModel(self.dividendSourceModel)
        # self.ui.transactionsView.setColumnHidden(6, True)
        # self.ui.dividendsView.resizeColumnsToContents()
        # self.ui.transactionsView.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # self.ui.dividendsView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.dividendsView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for col in range(5):
            self.ui.dividendsView.horizontalHeader().setSectionResizeMode(col,
                                                                          QtWidgets.QHeaderView.ResizeToContents)
        self.ui.dividendsView.scrollToBottom()
        self.ui.dividendsView.show()

    def display_filtered_transactions(self, ticker):
        if ticker not in self.transactionMap or ticker not in self.visible_tickers:
            self.ui.transactionsView.setVisible(False)
            return

        filtered = self.transactionMap[ticker]
        # print(ticker, filtered)
        self.transactionsSourceModel = TransactionModel(filtered,
                                                        ['Ticker', 'B/S', 'Date', '#', 'Cost', 'CPS', 'Sign', 'z'])
        self.ui.transactionsView.setModel(self.transactionsSourceModel)
        self.ui.transactionsView.setColumnHidden(6, True)
        # self.ui.transactionsView.resizeColumnsToContents()

        # self.ui.transactionsView.setSizeAdjustPolicy(self.ui.transactionsView.AdjustToContents)
        # self.ui.transactionsView.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.ui.transactionsView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for col in range(4):
            self.ui.transactionsView.horizontalHeader().setSectionResizeMode(col,
                                                                             QtWidgets.QHeaderView.ResizeToContents)
        # self.ui.transactionsView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.transactionsView.scrollToBottom()
        self.ui.transactionsView.show()

    def main_selection_changed(self, selected):
        if len(selected.indexes()) > 0:
            ticker = selected.indexes()[0].data()
            print("selected: ", ticker)
            self.display_filtered_transactions(ticker)
            self.display_filtered_dividends(ticker)

    def create_status_bar(self):
        self.ui.status_bar = self.statusBar()
        font = QtGui.QFont()
        font.setFamily("Noto Mono")
        font.setPointSize(9)
        for i in range(9):
            self._label_.append(QLabel(str(i)))
            self._label_[i].setFrameStyle(QFrame.Panel | QFrame.Sunken)
            self._label_[i].setAlignment(Qt.AlignBottom | Qt.AlignLeft)
            self._label_[i].setFont(font)
            if i > 7:
                self._label_[i].setStyleSheet("background-color: yellowgreen")
            elif i > 4:
                self._label_[i].setStyleSheet("background-color: #dde5b6")
            elif i > 1:
                self._label_[i].setStyleSheet("background-color: bisque")
            else:
                self._label_[i].setStyleSheet("background-color: lightskyblue")
            self.ui.status_bar.addPermanentWidget(self._label_[i], 1)
        # font = QtGui.QFont()
        # font.setFamily("Arial Black")
        # font.setPointSize(9)

        f = self._label_[8].font()
        f.setBold(True)
        # f.setPointSize(9)
        self._label_[8].setFont(f)

        # self._sb_annual_div_a = QLabel("Right")
        # self._sb_annual_div_a.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        # self._sb_annual_div_a.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        # self._sb_annual_div_a.setStyleSheet("background-color: lightgreen")

        # self.ui.status_bar.addPermanentWidget(self._sb_annual_div_b, 1)
        # self.ui.status_bar.addPermanentWidget(self._sb_annual_div_a, 1)


def create_app():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    # win.ui.mainFilter.setFocus()
    win.ui.summaryView.setFocus()
    sys.exit(app.exec_())


if __name__ == '__main__':
    create_app()
