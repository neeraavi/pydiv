from operator import itemgetter
import json
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtWidgets import QApplication, QHeaderView, QLabel, QFrame
import sys

import Dividends
from SummaryModel import SummaryModel
from divui import Ui_MainWindow
import transactions
from TransactionModel import TransactionModel
from CalendarModel import CalendarModel
from CalendarDetailsModel import CalendarDetailsModel
from DividendModel import DividendModel
import columnNames as consts


def resize_columns_for_details_view(view, cols):
    view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    for col in cols:
        view.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
    view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    view.scrollToBottom()
    view.show()


def resize_columns_for_calendar_view(view):
    view.horizontalHeader().setStretchLastSection(True)
    view.verticalHeader().setStretchLastSection(True)
    for i in range(9):  # last nine years - fixed column width
        view.setColumnWidth(i, 50)
    view.setColumnWidth(0, 60)
    view.setStyleSheet("alternate-background-color: floralwhite; background-color: white;")


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.dividendCalendarModel = None
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

        self.sourceModel = None
        self.proxyModel = None
        self.parse_config()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_shortcuts()
        self.setup_connections()
        self.create_status_bar()
        self.fill_summary_table()
        self.display_summary_table()
        self.set_font()
        self.setFixedSize(self.width(), self.height())

    def setup_shortcuts(self):
        # @formatter:off
        key_function_mapping = [
            [QtGui.QKeySequence.StandardKey.Find, self.ui.mainFilter.setFocus],
            [QtGui.QKeySequence.StandardKey.Cancel, self.reset_main_filter],
            [QtGui.QKeySequence.StandardKey.Quit, self.close],
            [QtCore.Qt.Key_F2, lambda: self.ui.searchAllColumns.setChecked(not self.ui.searchAllColumns.isChecked())],
            [QtCore.Qt.Key_F3, lambda: self.ui.showClosedPositions.setChecked(not self.ui.showClosedPositions.isChecked())],
            [QtCore.Qt.Key_Tab, self.next_tab],
            [QtCore.Qt.Key_A, lambda: self.ui.afterTax.setChecked(True)],
            [QtCore.Qt.Key_B, lambda: self.ui.beforeTax.setChecked(True)],
        ]
        # @formatter:on

        for item in key_function_mapping:
            shortcut = QtWidgets.QShortcut(item[0], self)
            shortcut.activated.connect(item[1])

    def update_on_closed_positions_changed(self):
        (self.selected_summary, self.visible_tickers) = self.select_summary_based_on_show_closed_positions()
        self.sourceModel = SummaryModel(self.selected_summary, self.summaryHeader)
        self.proxyModel.setSourceModel(self.sourceModel)

    def select_summary_based_on_show_closed_positions(self):
        show_closed_pos = self.ui.showClosedPositions.isChecked()
        if show_closed_pos:
            return self.summary, self._tickers_all
        return self.summary_active_positions_only, self._tickers_active_only

    def search_all_columns_changed(self):
        cols = -1 if self.ui.searchAllColumns.isChecked() else consts.SMRY_TICKER
        self.proxyModel.setFilterKeyColumn(cols)

    def setup_connections(self):
        # self.ui.summaryView.setStyleSheet("alternate-background-color: #fefae0; background-color: white;")
        # self.ui.summaryView.setStyleSheet("""QTableView {  gridline-color: seashell;}""")
        self.ui.mainFilter.returnPressed.connect(lambda: self.ui.summaryView.setFocus())
        self.ui.showClosedPositions.stateChanged.connect(self.update_on_closed_positions_changed)
        self.ui.searchAllColumns.stateChanged.connect(self.search_all_columns_changed)
        self.ui.mainFilter.textChanged.connect(self.ticker_filter_changed)

    def fill_summary_table(self):
        self.do_calculations_on_transactions()
        self.do_calculations_on_dividends()

    def do_calculations_on_transactions(self):
        t = transactions.Transactions(self.startYear, self.pathPrefix, self.now)
        self.update_transaction_calendar(t)
        (self.summary, self.transactionMap, self.totalInvested, self.summaryHeader) = t.get_transaction_results()
        self.summary_active_positions_only = [x for x in self.summary if x[consts.SMRY_STATUS] != "*"]
        self._tickers_all = [x[consts.SMRY_TICKER] for x in self.summary]
        self._tickers_active_only = [x[consts.SMRY_TICKER] for x in self.summary_active_positions_only]

    def do_calculations_on_dividends(self):
        d = Dividends.Dividends(self.startYear, self.pathPrefix, self.summary, self.totalInvested, self.now)
        self.update_dividend_calendar(d)
        (self.dividendMap, self.dividendHeader, self.annual_div_a, self.annual_div_b) = d.get_dividend_results()
        self.update_status_bar()

    def display_summary_table(self):
        self.proxyModel = QtCore.QSortFilterProxyModel(self)
        self.update_on_closed_positions_changed()
        self.proxyModel.setFilterKeyColumn(consts.SMRY_TICKER)
        self.proxyModel.sort(0, Qt.AscendingOrder)
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        view = self.ui.summaryView
        view.setModel(self.proxyModel)
        view.selectionModel().selectionChanged.connect(self.display_filtered_transactions_and_dividends)
        view.setWordWrap(False)
        view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for col in range(10):
            view.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
        view.show()
        view.setCurrentIndex(view.model().index(0, 0))

    def reset_main_filter(self):
        if self.ui.mainFilter.hasFocus():
            self.ui.mainFilter.setText("")
        else:
            self.ui.mainFilter.setFocus()

    def ticker_filter_changed(self, new_filter):
        self.proxyModel.setFilterFixedString(new_filter)
        self.ui.summaryView.selectRow(0)
        self.display_filtered_transactions_and_dividends()

    def display_filtered_transactions_and_dividends(self):
        selected = self.ui.summaryView.selectedIndexes()
        if len(selected) <= 0:
            self.ui.dividendsView.setVisible(False)
            self.ui.transactionsView.setVisible(False)
            return
        ticker = selected[consts.SMRY_TICKER].data()
        # print("selected: ", ticker)
        self.display_filtered_transactions(ticker)
        self.display_filtered_dividends(ticker)

    def display_filtered_transactions(self, ticker):
        filtered = self.transactionMap[ticker]
        self.transactionsSourceModel = TransactionModel(filtered, ["Ticker", "B/S", "Date", "#", "Cost", "CPS", "Sign"])
        view = self.ui.transactionsView
        view.setModel(self.transactionsSourceModel)
        view.setColumnHidden(6, True)
        resize_columns_for_details_view(view, range(4, 7))

    def display_filtered_dividends(self, ticker):
        if ticker not in self.dividendMap:
            self.ui.dividendsView.setVisible(False)
            return

        filtered = self.dividendMap[ticker]
        self.dividendSourceModel = DividendModel(filtered, self.dividendHeader)
        view = self.ui.dividendsView
        view.setModel(self.dividendSourceModel)
        resize_columns_for_details_view(
            view, [consts.DIV_DPS, consts.DIV_BEFORE, consts.DIV_AFTER, consts.DIV_WHERE])

    def create_status_bar(self):
        self.ui.status_bar = self.statusBar()
        font = QtGui.QFont()
        font.setFamily(self.mainFont)
        font.setPointSize(9)
        colors = ['lightskyblue', 'lightskyblue',
                  'bisque', 'bisque', 'bisque',
                  '#dde5b6', '#dde5b6', '#dde5b6', 'yellowgreen']
        for i in range(9):
            label = QLabel(str(i))
            label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            label.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
            label.setFont(font)
            label.setStyleSheet(f"background-color: {colors[i]}")
            self._label_.append(label)
            self.ui.status_bar.addPermanentWidget(label, 1)

        f = self._label_[-1].font()
        f.setBold(True)
        self._label_[-1].setFont(f)

    def set_font(self):
        font = QtGui.QFont()
        # font.setFamily("Ubuntu")
        # font.setFamily("FiraCode")
        font.setFamily(self.mainFont)
        font.setPointSize(self.mainFontSize)

        dv = self.ui.dividendsView
        dcv = self.ui.dividendCalendarView
        icv = self.ui.investmentCalendarView
        cdv = self.ui.calendarDetailsView
        items = [
            self.ui.summaryView,
            self.ui.summaryView.horizontalHeader(),
            self.ui.transactionsView,
            dv, dv.horizontalHeader(), dv.verticalHeader(),
            dcv, dcv.horizontalHeader(), dcv.verticalHeader(),
            icv, icv.horizontalHeader(), icv.verticalHeader(),
            cdv, cdv.horizontalHeader(), cdv.verticalHeader()
        ]
        for item in items:
            item.setFont(font)

    def update_status_bar(self):
        annual_div_after_deduction_claim = self.annual_div_a + consts.TAX_Standard_deduction
        f = 100 / self.totalInvested
        yoc_a = annual_div_after_deduction_claim * f
        yoc_b = self.annual_div_b * f
        fwd_a_m = annual_div_after_deduction_claim / 12
        # @formatter:off
        items = [
            [consts.LBL_ACTIVE                      , f"Active#  {len(self.summary_active_positions_only)}"]           ,
            [consts.LBL_INVESTED                    , f"Invested:  {self.totalInvested}"]                              ,
            [consts.LBL_FwdAnnDivA_before_deduction , "FwdAnnDivA: {m:0.0f}".format(m=self.annual_div_a)]              ,
            [consts.LBL_FwdAnnDivA_after_deduction  , "FwdAnnDivA: {m:0.0f}".format(m=annual_div_after_deduction_claim)],
            [consts.LBL_YoC_A                       , "YoC_A: {m:0.2f}%".format(m=yoc_a)]                              ,
            [consts.LBL_FwdAnnDivA_M                , "FwdAnnDivA_M: {m:0.0f}".format(m=fwd_a_m)]                      ,
            [consts.LBL_FwdAnnDivB                  , "FwdAnnDivB: {m:0.0f}".format(m=self.annual_div_b)]              ,
            [consts.LBL_YoC_B                       , "YoC_B: {m:0.2f}%".format(m=yoc_b)]                              ,
            [consts.LBL_FwdAnnDivB_M                , "FwdAnnDivB_M: {m:0.0f}".format(m=self.annual_div_b / 12)]
        ]
        # @formatter:on
        for row in items:
            self._label_[row[0]].setText(row[1])

    def update_transaction_calendar(self, t):
        (self.investmentCalendar, investment_calendar_header, month_header) = t.get_investment_calendar()
        self.investmentCalendarModel = CalendarModel(self.investmentCalendar, investment_calendar_header, month_header)

        proxy_model = QtCore.QSortFilterProxyModel(self)
        proxy_model.setSourceModel(self.investmentCalendarModel)
        view = self.ui.investmentCalendarView
        view.setModel(proxy_model)
        view.selectionModel().selectionChanged.connect(self.inv_cal_selection_changed)

        resize_columns_for_calendar_view(view)
        view.clicked.connect(self.investment_calendar_clicked)

    def update_dividend_calendar(self, d):
        (dividendCalendar, dividend_calendar_header, month_header) = d.get_dividend_calendar_before_tax()
        self.dividendCalendarModel = CalendarModel(dividendCalendar, dividend_calendar_header, month_header)

        proxy_model = QtCore.QSortFilterProxyModel(self)
        proxy_model.setSourceModel(self.dividendCalendarModel)
        view = self.ui.dividendCalendarView
        view.setModel(proxy_model)
        view.selectionModel().selectionChanged.connect(self.div_cal_selection_changed)

        resize_columns_for_calendar_view(view)
        view.clicked.connect(self.dividend_calendar_clicked)

    def inv_cal_selection_changed(self, selected):
        for idx in selected.indexes():
            self.redisplay_investment(idx.row() + 1, self.now.year - idx.column())

    def investment_calendar_clicked(self, item):
        m = 1 + item.row()
        y = self.now.year - item.column()
        self.redisplay_investment(m, y)

    def div_cal_selection_changed(self, selected):
        for idx in selected.indexes():
            self.redisplay_dividend(idx.row() + 1, self.now.year - idx.column())

    def dividend_calendar_clicked(self, item):
        m = 1 + item.row()
        y = self.now.year - item.column()
        self.redisplay_dividend(m, y)

    def redisplay_investment(self, m, y):
        if m > 12:
            return

        ym = "{y}-{m:02d}".format(m=m, y=y)
        result = [row for ticker, items in self.transactionMap.items() for row in items if ym in row[2]]
        result = sorted(result, key=itemgetter(2))
        header = ["Ticker", "B/S", "Date", "#", "Cost", "CPS", "Sign", "z"]
        self.calendarDetailsModel = CalendarDetailsModel(result, header, [])
        self.ui.calendarDetailsMode.setText(f"Investments in {ym}")

        view = self.ui.calendarDetailsView
        indices_to_hide = [6]
        self.redisplay(view, indices_to_hide)

    def redisplay_dividend(self, m, y):
        if m > 12:
            return

        ym = "{y}-{m:02d}".format(m=m, y=y)
        result = [row for ticker, items in self.dividendMap.items() for row in items if ym in row[consts.DIV_YM]]
        result = sorted(result, key=itemgetter(consts.DIV_TICKER))
        self.calendarDetailsModel = CalendarDetailsModel(result, self.dividendHeader, [])
        self.ui.calendarDetailsMode.setText(f"Dividends in {ym}")

        view = self.ui.calendarDetailsView
        indices_to_hide = [consts.DIV_YOC_A, consts.DIV_YOC_B, consts.DIV_WHERE, consts.DIV_CHANGE]
        self.redisplay(view, indices_to_hide)

    def redisplay(self, view, indices_to_hide):
        view.setModel(self.calendarDetailsModel)
        for col in indices_to_hide:
            view.setColumnHidden(col, True)
        view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        view.show()

    def next_tab(self):
        tab = self.ui.tabWidget
        cur_index = tab.currentIndex()
        if cur_index < len(tab) - 1:
            tab.setCurrentIndex(cur_index + 1)
        else:
            tab.setCurrentIndex(0)

    def parse_config(self):
        with open("config.json", "r") as config:
            data = json.load(config)
            print("Read successful")
        print(data)
        self.pathPrefix = data["path_prefix"]
        self.mainFont = data["main_font"]
        self.mainFontSize = data["main_font_size"]


def create_app():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    win.ui.summaryView.setFocus()
    index = win.ui.dividendCalendarView.model().index(0, 0)
    win.ui.dividendCalendarView.selectionModel().select(index, QItemSelectionModel.Select)

    sys.exit(app.exec_())


if __name__ == "__main__":
    create_app()
