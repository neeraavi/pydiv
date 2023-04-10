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
import columnNames as consts


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.investmentCalendarModel = None
        self._label_ = []
        self.dividendSourceModel = None
        self.calendarDetailsModel = None
        self._tickers_active_only = None
        self._tickers_all = None
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

        self.setup_shortcuts_and_connections()
        self.create_status_bar()
        self.fill_summary_table()
        self.setFixedSize(self.width(), self.height())

    def setup_shortcuts_and_connections(self):
        self.shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Find), self)
        self.shortcut.activated.connect(self.ui.mainFilter.setFocus)
        self.closeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Quit), self)
        self.closeShortcut.activated.connect(self.close)
        self.closeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Cancel), self)
        self.closeShortcut.activated.connect(self.reset_main_filter)
        self.closeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F2), self)
        self.closeShortcut.activated.connect(
            lambda: self.ui.searchAllColumns.setChecked(not self.ui.searchAllColumns.isChecked()))
        self.closeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F3), self)
        self.closeShortcut.activated.connect(
            lambda: self.ui.showClosedPositions.setChecked(not self.ui.showClosedPositions.isChecked()))
        # self.ui.summaryView.setStyleSheet("alternate-background-color: #fefae0; background-color: white;")
        # self.ui.summaryView.setStyleSheet("""QTableView {  gridline-color: #F2D2BD;}""")
        self.ui.mainFilter.returnPressed.connect(self.main_filter_return_pressed)
        self.ui.showClosedPositions.stateChanged.connect(self.show_closed_positions_changed)
        self.ui.searchAllColumns.stateChanged.connect(self.search_all_columns_changed)

    def main_filter_return_pressed(self):
        print('Enter pressed')
        self.ui.summaryView.setFocus()

    def show_closed_positions_changed(self):
        show_closed_pos = self.ui.showClosedPositions.isChecked()
        self.selected_summary = self.summary if show_closed_pos else self.summary_active_positions_only
        self.visible_tickers = self._tickers_all if show_closed_pos else self._tickers_active_only
        self.sourceModel = SummaryModel(self.selected_summary, self.summaryHeader)
        self.proxyModel.setSourceModel(self.sourceModel)

    def search_all_columns_changed(self):
        cols = -1 if self.ui.searchAllColumns.isChecked() else consts.SMRY_TICKER
        # self.ui.searchAllColumns.isChecked(cols)
        self.proxyModel.setFilterKeyColumn(cols)

    def fill_summary_table(self):
        # transaction calculations
        t = transactions.Transactions(self.startYear, self.pathPrefix)
        t.fill_transactions()
        self.update_transaction_calendar(t)
        (self.summary, self.transactionMap, self.totalInvested, self.summaryHeader) = t.get_transaction_results()
        self.summary_active_positions_only = [x for x in self.summary if x[1] != '*']
        self._label_[consts.LBL_ACTIVE].setText(f'Active#  {len(self.summary_active_positions_only)}')
        self._label_[consts.LBL_INVESTED].setText(f'Invested:  {self.totalInvested}')
        self._tickers_all = [x[consts.SMRY_TICKER] for x in self.summary]
        self._tickers_active_only = [x[consts.SMRY_TICKER] for x in self.summary if x[consts.SMRY_STATUS] != '*']

        # dividend calculations
        d = dividends.Dividends(self.startYear, self.pathPrefix, self.summary, self.totalInvested)
        d.fill_dividends()
        (self.dividendMap, self.dividendHeader, annual_div_a, annual_div_b) = d.get_dividend_results()
        self.update_status_bar(annual_div_a, annual_div_b)

        # display summary table
        self.proxyModel = QtCore.QSortFilterProxyModel(self)
        self.show_closed_positions_changed()
        self.proxyModel.setFilterKeyColumn(consts.SMRY_TICKER)
        self.proxyModel.sort(0, Qt.AscendingOrder)
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.ui.mainFilter.textChanged.connect(self.ticker_filter_changed)
        self.ui.summaryView.setModel(self.proxyModel)
        self.ui.summaryView.selectionModel().selectionChanged.connect(self.main_selection_changed)

        self.ui.summaryView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for col in range(10):
            self.ui.summaryView.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)

        self.ui.summaryView.show()
        self.ui.summaryView.setCurrentIndex(self.ui.summaryView.model().index(0, 0))

    def main_selection_changed(self):
        selected = self.ui.summaryView.selectedIndexes()
        if len(selected) <= 0:
            self.ui.dividendsView.setVisible(False)
            self.ui.transactionsView.setVisible(False)
            return
        ticker = selected[consts.SMRY_TICKER].data()
        print("selected: ", ticker)
        self.display_filtered_transactions(ticker)
        self.display_filtered_dividends(ticker)

    def reset_main_filter(self):
        if self.ui.mainFilter.hasFocus():
            self.ui.mainFilter.setText('')
        else:
            self.ui.mainFilter.setFocus()

    def ticker_filter_changed(self, new_filter):
        self.proxyModel.setFilterFixedString(new_filter)
        self.ui.summaryView.selectRow(0)
        selected = self.ui.summaryView.selectedIndexes()
        if len(selected) <= 0:
            self.ui.dividendsView.setVisible(False)
            self.ui.transactionsView.setVisible(False)
            return
        ticker = selected[consts.SMRY_TICKER].data()
        print("selected: ", ticker)
        self.display_filtered_transactions(ticker)
        self.display_filtered_dividends(ticker)

    def display_filtered_dividends(self, ticker):
        if ticker not in self.dividendMap:
            self.ui.dividendsView.setVisible(False)
            return

        filtered = self.dividendMap[ticker]
        self.dividendSourceModel = DividendModel(filtered, self.dividendHeader)
        self.ui.dividendsView.setModel(self.dividendSourceModel)
        self.ui.dividendsView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for col in [consts.DIV_DPS, consts.DIV_BEFORE, consts.DIV_AFTER, consts.DIV_WHERE]:
            self.ui.dividendsView.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
        self.ui.dividendsView.scrollToBottom()
        self.ui.dividendsView.show()

    def display_filtered_transactions(self, ticker):
        filtered = self.transactionMap[ticker]
        self.transactionsSourceModel = TransactionModel(filtered, ['Ticker', 'B/S', 'Date', '#', 'Cost', 'CPS', 'Sign'])
        self.ui.transactionsView.setModel(self.transactionsSourceModel)
        self.ui.transactionsView.setColumnHidden(6, True)
        self.ui.transactionsView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        for col in range(4, 7):
            self.ui.transactionsView.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
        self.ui.transactionsView.scrollToBottom()
        self.ui.transactionsView.show()

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

        f = self._label_[8].font()
        f.setBold(True)
        # f.setPointSize(9)
        self._label_[8].setFont(f)

    def update_status_bar(self, annual_div_a, annual_div_b):
        t = 'FwdAnnDivA: {m:0.0f}'.format(m=annual_div_a)
        self._label_[consts.LBL_FwdAnnDivA_before_deduction].setText(t)
        annual_div_after_deduction_claim = annual_div_a + consts.TAX_Standard_deduction
        t = 'FwdAnnDivA: {m:0.0f}'.format(m=annual_div_after_deduction_claim)
        self._label_[consts.LBL_FwdAnnDivA_after_deduction].setText(t)
        t = 'YoC_A: {m:0.2f}%'.format(m=annual_div_after_deduction_claim / self.totalInvested * 100)
        self._label_[consts.LBL_YoC_A].setText(t)
        t = 'FwdAnnDivA_M: {m:0.0f}'.format(m=annual_div_after_deduction_claim / 12)
        self._label_[consts.LBL_FwdAnnDivA_M].setText(t)

        t = 'FwdAnnDivB: {m:0.0f}'.format(m=annual_div_b)
        self._label_[consts.LBL_FwdAnnDivB].setText(t)
        t = 'YoC_B: {m:0.2f}%'.format(m=annual_div_b / self.totalInvested * 100)
        self._label_[consts.LBL_YoC_B].setText(t)
        t = 'FwdAnnDivB_M: {m:0.0f}'.format(m=annual_div_b / 12)
        self._label_[consts.LBL_FwdAnnDivB_M].setText(t)

    def update_transaction_calendar(self, t):
        (self.investmentCalendar, investment_calendar_header, month_header) = t.get_investment_calendar()
        self.investmentCalendarModel = CalendarModel(self.investmentCalendar, investment_calendar_header, month_header)

        proxy_model = QtCore.QSortFilterProxyModel(self)
        # proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        proxy_model.setSourceModel(self.investmentCalendarModel)
        self.ui.investmentCalendarView.setModel(proxy_model)
        self.ui.investmentCalendarView.selectionModel().selectionChanged.connect(self.inv_cal_selection_changed)
        self.ui.investmentCalendarView.horizontalHeader().setStretchLastSection(False)
        self.ui.investmentCalendarView.resizeColumnsToContents()
        self.ui.investmentCalendarView.setStyleSheet("alternate-background-color: #fefae0; background-color: white;")
        self.ui.investmentCalendarView.clicked.connect(self.investment_calendar_clicked)

    def inv_cal_selection_changed(self, selected):
        for idx in selected.indexes():
            self.redisplay_investment(idx.row() + 1, self.now.year - idx.column())

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


def create_app():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    win.ui.summaryView.setFocus()
    sys.exit(app.exec_())


if __name__ == '__main__':
    create_app()
