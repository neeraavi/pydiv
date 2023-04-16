import copy
import json
import sys
from datetime import datetime
from operator import itemgetter

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QItemSelectionModel, QProcess, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QFrame, QHeaderView, QLabel

import Constants as consts
import Dividends
import fileprocessor
import transactions
from CalendarDetailsModel import CalendarDetailsModel
from CalendarModel import CalendarModel
from DividendModel import DividendModel
from divui import Ui_MainWindow
from SectorDetailsModel import SectorDetailsModel
from SectorModel import SectorModel
from SummaryModel import SummaryModel
from TransactionModel import TransactionModel


def get_last_1_2_6_12_ym(y, m):
    import datetime as datetime
    today = datetime.datetime.now()
    result = []
    if y == today.year and m == today.month:
        prev = [1, 2, 6, 12]
        first = today.replace(day=1)
        for m in prev:
            before = first - datetime.timedelta(days=m * 30 + 5)
            before = before.strftime("%Y-%m")
            result.append(before)
    # sprint(result)
    return result


def resize_columns_for_details_view(view, cols):
    hh = view.horizontalHeader()
    hh.setSectionResizeMode(QHeaderView.ResizeToContents)
    for col in cols:
        hh.setSectionResizeMode(col, QHeaderView.Stretch)
    view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    view.scrollToBottom()
    view.show()


def resize_columns_for_calendar_view(view):
    view.horizontalHeader().setStretchLastSection(True)
    vh = view.verticalHeader()
    vh.setSectionResizeMode(QHeaderView.ResizeToContents)
    vh.setStretchLastSection(False)
    for i in range(9):  # last nine years - fixed column width
        view.setColumnWidth(i, 50)
    view.setColumnWidth(0, 80)
    view.setStyleSheet("alternate-background-color: floralwhite; background-color: white;")


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.div_obj = None
        self._label_ = []
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
        self.transactions_header = ["Ticker", "B/S", "Date", "#", "Cost", "CPS", "Sign"]
        self.sector_header = ['Ticker', 'Inv', 'Alloc', 'annual_contrib_b', 'annual_contrib_a']
        self.proxyModel = None

        self.parse_config()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_shortcuts()
        self.create_status_bar()
        self.fill_summary_table()
        self.display_summary_table()
        self.display_sector_tables()
        self.set_font()
        self.setFixedSize(self.width(), self.height())
        self.setup_connections()
        self.start_external_process()
        self.setWindowIcon(QtGui.QIcon('icon.png'))

    def setup_shortcuts(self):
        # @formatter:off
        key_function_mapping = [
            [QtGui.QKeySequence.StandardKey.Find, self.ui.mainFilter.setFocus],
            [QtGui.QKeySequence.StandardKey.Cancel, self.reset_main_filter],
            [QtGui.QKeySequence.StandardKey.Quit, self.close],
            [QtCore.Qt.Key_F2, lambda: self.ui.searchAllColumns.setChecked(not self.ui.searchAllColumns.isChecked())],
            [QtCore.Qt.Key_F3, lambda: self.ui.showClosedPositions.setChecked(not self.ui.showClosedPositions.isChecked())],
            [QtCore.Qt.Key_Tab, self.next_tab],
            [QtCore.Qt.Key_NumberSign, self.toggle_before_after],
        ]
        # @formatter:on

        for item in key_function_mapping:
            shortcut = QtWidgets.QShortcut(item[0], self)
            shortcut.activated.connect(item[1])

    def toggle_before_after(self):
        tab = self.ui.tabWidget
        cur_index = tab.currentIndex()
        if cur_index == 1:
            if c := self.ui.afterTax.isChecked():
                self.ui.beforeTax.setChecked(True)
            else:
                self.ui.afterTax.setChecked(True)

    def update_on_closed_positions_changed(self):
        (self.selected_summary, self.visible_tickers) = self.select_summary_based_on_show_closed_positions()
        source_model = SummaryModel(self.selected_summary, self.summaryHeader)
        self.proxyModel.setSourceModel(source_model)

    def select_summary_based_on_show_closed_positions(self):
        if show_closed_pos := self.ui.showClosedPositions.isChecked():
            return self.summary, self._tickers_all
        return self.summary_active_positions_only, self._tickers_active_only

    def search_all_columns_changed(self):
        cols = -1 if self.ui.searchAllColumns.isChecked() else consts.SMRY_TICKER
        self.proxyModel.setFilterKeyColumn(cols)

    def setup_connections(self):
        self.ui.mainFilter.returnPressed.connect(lambda: self.ui.summaryView.setFocus())
        self.ui.showClosedPositions.stateChanged.connect(self.update_on_closed_positions_changed)
        self.ui.searchAllColumns.stateChanged.connect(self.search_all_columns_changed)
        self.ui.mainFilter.textChanged.connect(self.ticker_filter_changed)
        self.ui.beforeTax.toggled.connect(lambda: self.update_dividend_calendar(self.div_obj))

    def fill_summary_table(self):
        self.do_calculations_on_transactions()
        self.do_calculations_on_dividends()
        self.do_calculations_on_sector()

    def do_calculations_on_transactions(self):
        t = transactions.Transactions(self.startYear, self.pathPrefix, self.now, self.outPathPrefix)
        self.update_transaction_calendar(t)
        (self.summary, self.transactionMap, self.totalInvested, self.summaryHeader) = t.get_transaction_results()
        self.summary_active_positions_only = [x for x in self.summary if x[consts.SMRY_STATUS] != "*"]
        self._tickers_all = [x[consts.SMRY_TICKER] for x in self.summary]
        self._tickers_active_only = [x[consts.SMRY_TICKER] for x in self.summary_active_positions_only]

    def do_calculations_on_dividends(self):
        self.div_obj = Dividends.Dividends(self.startYear, self.pathPrefix, self.summary, self.totalInvested, self.now,
                                           self.outPathPrefix)
        self.update_dividend_calendar(self.div_obj)
        (self.dividendMap, self.dividendHeader, self.annual_div_a,
         self.annual_div_b) = self.div_obj.get_dividend_results()
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
        m_filter = self.ui.mainFilter
        if m_filter.hasFocus():
            m_filter.setText("")
        else:
            m_filter.setFocus()

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
        transactions_source_model = TransactionModel(filtered, self.transactions_header)
        view = self.ui.transactionsView
        view.setModel(transactions_source_model)
        view.setColumnHidden(6, True)
        resize_columns_for_details_view(view, range(4, 7))

    def display_filtered_dividends(self, ticker):
        if ticker not in self.dividendMap:
            self.ui.dividendsView.setVisible(False)
            return

        filtered = self.dividendMap[ticker]
        dividend_source_model = DividendModel(filtered, self.dividendHeader)
        view = self.ui.dividendsView
        view.setModel(dividend_source_model)
        resize_columns_for_details_view(
            view, [consts.DIV_DPS, consts.DIV_BEFORE, consts.DIV_AFTER, consts.DIV_WHERE])

    def create_status_bar(self):
        self.ui.status_bar = self.statusBar()
        font = QtGui.QFont()
        font.setFamily(self.mainFont)
        font.setPointSize(10)
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
            [consts.LBL_INVESTED                    , f"Invested:  {round(self.totalInvested)}"]                              ,
            [consts.LBL_FwdAnnDivA_before_deduction , "FwdAnnDivA: {m:0.0f}".format(m=self.annual_div_a)]              ,
            [consts.LBL_FwdAnnDivA_after_deduction  , "FwdAnnDivA: {m:0.0f}".format(m=annual_div_after_deduction_claim)],
            [consts.LBL_YoC_A                       , "YoC_A:   {m:0.2f}%".format(m=yoc_a)]                              ,
            [consts.LBL_FwdAnnDivA_M                , "FwdDivA_M: {m:0.0f}".format(m=fwd_a_m)]                      ,
            [consts.LBL_FwdAnnDivB                  , "FwdAnnDivB: {m:0.0f}".format(m=self.annual_div_b)]              ,
            [consts.LBL_YoC_B                       , "YoC_B:   {m:0.2f}%".format(m=yoc_b)]                              ,
            [consts.LBL_FwdAnnDivB_M                , "FwdDivB_M: {m:0.0f}".format(m=self.annual_div_b / 12)]
        ]
        # @formatter:on
        for row in items:
            self._label_[row[0]].setText(row[1])

    def update_transaction_calendar(self, t):
        (investment_calendar, investment_calendar_header, month_header) = t.get_investment_calendar()
        investment_calendar_model = CalendarModel(investment_calendar, investment_calendar_header, month_header)
        proxy_model = QtCore.QSortFilterProxyModel(self)
        proxy_model.setSourceModel(investment_calendar_model)
        view = self.ui.investmentCalendarView
        view.setModel(proxy_model)
        view.selectionModel().selectionChanged.connect(self.inv_cal_selection_changed)
        resize_columns_for_calendar_view(view)
        view.clicked.connect(self.redisplay_investment)

    def update_dividend_calendar(self, d):
        result = d.get_dividend_calendar_before_tax() if self.ui.beforeTax.isChecked() else d.get_dividend_calendar_after_tax()
        (dividends_calendar, dividend_calendar_header, month_header) = result
        dividends_calendar = [['' if x == 0 else x for x in l] for l in dividends_calendar]

        dividend_calendar_model = CalendarModel(dividends_calendar, dividend_calendar_header, month_header)
        proxy_model = QtCore.QSortFilterProxyModel(self)
        proxy_model.setSourceModel(dividend_calendar_model)
        view = self.ui.dividendCalendarView
        view.setModel(proxy_model)
        view.selectionModel().selectionChanged.connect(self.div_cal_selection_changed)
        resize_columns_for_calendar_view(view)
        view.clicked.connect(self.redisplay_dividend)

    def get_m_y_from_index(self, idx):
        m = idx.row() + 1
        y = self.now.year - idx.column()
        return m, y

    def inv_cal_selection_changed(self, selected):
        for idx in selected.indexes():
            self.redisplay_investment(idx)

    def div_cal_selection_changed(self, selected):
        for idx in selected.indexes():
            self.redisplay_dividend(idx)

    def redisplay_investment(self, idx):
        (m, y) = self.get_m_y_from_index(idx)
        if m > 12:
            return
        ym = "{y}-{m:02d}".format(m=m, y=y)
        result = [row for ticker, items in self.transactionMap.items() for row in items if ym in row[2]]
        result = sorted(result, key=itemgetter(2))
        self.calendarDetailsModel = CalendarDetailsModel(result, self.transactions_header, [])
        self.ui.calendarDetailsMode.setText(f"Investments in {ym}")
        indices_to_hide = [6]
        self.redisplay(self.ui.calendarDetailsView, indices_to_hide, len(result))

    def redisplay_dividend(self, idx):
        (m, y) = self.get_m_y_from_index(idx)
        if m > 12:
            return

        ym = "{y}-{m:02d}".format(m=m, y=y)
        result = [row for ticker, items in self.dividendMap.items() for row in items if ym in row[consts.DIV_YM]]
        result = copy.deepcopy(result)
        result = sorted(result, key=itemgetter(consts.DIV_TICKER))
        current_tickers = {r[0] for r in result}
        div_a = 0
        div_b = 0
        # for r in result:
        #    r[consts.DIV_DPS] = "{m:0.2f}".format(m=r[consts.DIV_DPS])
        if len(result) > 0:
            blist, alist = zip(*[((row[consts.DIV_BEFORE]), (row[consts.DIV_AFTER])) for row in result])
            div_b = sum(blist)
            div_a = sum(alist)

            nos = len(result)
            row = ['Total', nos, '', '', '', round(div_b), '', round(div_a), '', '', '']
            result.append(row)

        # -------------------------------------------------------
        prev = get_last_1_2_6_12_ym(y, m)
        prev_tickers = []
        if len(prev) == 4:
            f = ['M', 'Q', 'B', 'A']
            for count, freq in enumerate(f):
                t = [row[0] for ticker, items in self.dividendMap.items() for row in items if
                     prev[count] in row[consts.DIV_YM] and row[consts.DIV_FREQ] == freq]
                # print(len(t))
                prev_tickers.extend(t)
            prev_tickers = set(prev_tickers)
            # print(prev_tickers, len(prev_tickers))
            expected = prev_tickers.difference(current_tickers)

            if new := current_tickers.difference(prev_tickers):
                for row in result:
                    for n in new:
                        if row[consts.SMRY_TICKER] == n:
                            row[consts.SMRY_TICKER] = f'. {row[consts.SMRY_TICKER]}'

            # print(len(expected), expected)
            e_divs = []
            for row in self.summary:
                ticker = row[consts.SMRY_TICKER]
                if ticker in expected:
                    divs = self.dividendMap[ticker]
                    d = divs[-3]
                    # print(d)
                    f = d[consts.DIV_FREQ]
                    ppy = fileprocessor.payments_per_year(f)
                    # print(ticker, row[consts.SMRY_ANN_DIV_A], row[consts.SMRY_ANN_DIV_B],
                    #      row[consts.SMRY_STATUS], f, dps, '##', ppy)
                    e_b = row[consts.SMRY_ANN_DIV_B] / ppy
                    e_a = row[consts.SMRY_ANN_DIV_A] / ppy
                    dps = d[consts.DIV_DPS]
                    e_row = [f'~ {ticker}', f, '', row[consts.SMRY_NOS], dps, e_b, '', e_a, '', '', '']
                    e_divs.append(e_row)

            e_divs = sorted(e_divs, key=itemgetter(consts.DIV_TICKER))
            if len(e_divs) > 0:
                # for r in e_divs:
                #    r[consts.DIV_DPS] = "{m:0.2f}".format(m=r[consts.DIV_DPS])
                # div_e_b = sum(row[consts.DIV_BEFORE] for row in e_divs)
                # div_e_a = sum(row[consts.DIV_AFTER] for row in e_divs)
                b_list, a_list = zip(*[((row[consts.DIV_BEFORE]), (row[consts.DIV_AFTER])) for row in e_divs])
                div_e_b = sum(b_list)
                div_e_a = sum(a_list)

                nos = len(e_divs)
                row = ['Expected', nos, '', '', '', round(div_e_b), '', round(div_e_a), '', '', '']
                e_divs.append(row)
                row = ['##', nos, '', '', '', round(div_b + div_e_b), '', round(div_a + div_e_a), '', '', '']
                e_divs.append(row)

            result.extend(e_divs)
        # print(result)
        # -------------------------------------------------------
        self.calendarDetailsModel = CalendarDetailsModel(result, self.dividendHeader, [])
        self.ui.calendarDetailsMode.setText(f"Dividends in {ym}")

        view = self.ui.calendarDetailsView
        indices_to_hide = [consts.DIV_YOC_A, consts.DIV_YOC_B, consts.DIV_WHERE, consts.DIV_CHANGE]
        self.redisplay(view, indices_to_hide, len(result))

    def redisplay(self, view, indices_to_hide, row_count):
        view.setModel(self.calendarDetailsModel)
        if row_count > 0:
            for col in indices_to_hide:
                view.setColumnHidden(col, True)
            for i in range(9):
                view.setColumnWidth(i, 60)
            view.setColumnWidth(0, 100)
            view.setColumnWidth(2, 80)
            view.horizontalHeader().setSectionResizeMode(consts.DIV_BEFORE, QHeaderView.Stretch)
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
        # @formatter:off
        self.pathPrefix    = data["path_prefix"]
        self.outPathPrefix = data["out_path_prefix"]
        self.mainFont      = data["main_font"]
        self.mainFontSize  = data["main_font_size"]
        # @formatter:on

    def do_calculations_on_sector(self):
        self.sector_map = {}
        for row in self.summary:
            status = row[consts.SMRY_STATUS]
            if '*' in status:
                continue
            s = row[consts.SMRY_SECTOR]
            ticker = row[consts.SMRY_TICKER]
            inv = row[consts.SMRY_INVESTED]
            alloc = row[consts.SMRY_ALLOC]
            annual_contrib_a = row[consts.SMRY_ANN_DIV_A]
            annual_contrib_b = row[consts.SMRY_ANN_DIV_B]
            if s not in self.sector_map:
                self.sector_map[s] = []
            self.sector_map[s].append([ticker, inv, alloc, annual_contrib_b, annual_contrib_a])

        self.sector_summary = []
        for sector, items in self.sector_map.items():
            nos = len(items)
            inv = sum(row[1] for row in items)
            alloc = inv / self.totalInvested * 100
            self.sector_summary.append([sector, round(inv), alloc, nos])
        self.sector_summary = sorted(self.sector_summary, key=itemgetter(2))

        file_name = f'{self.outPathPrefix}/sector_details.log'
        with open(file_name, "w") as f:
            for item in self.sector_summary:
                print(item[0], ',', item[2], file=f)

        inv_list, nos_list = zip(*[((row[1]), (row[3])) for row in self.sector_summary])
        inv_total = sum(inv_list)
        nos_total = sum(nos_list)

        self.sector_summary.append(['Total', inv_total, 100, nos_total])

    def display_sector_tables(self):
        header = ['Sector', 'Invested', 'Allocation', '#', '5']
        sector_summary_model = SectorModel(self.sector_summary, header, [])
        view = self.ui.sectorSummaryView
        view.setModel(sector_summary_model)
        view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        view.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(len(self.sector_summary)):
            view.setRowHeight(i, 20)
        view.show()
        view.selectionModel().selectionChanged.connect(self.sector_summary_selection_changed)
        view.setCurrentIndex(view.model().index(0, 0))

    def sector_summary_selection_changed(self, selected):
        for idx in selected.indexes():
            selected_row = idx.row()
        sector = self.sector_summary[selected_row][0]
        if sector not in self.sector_map:
            return
        # print(ticker)
        result = self.sector_map[sector]
        result = sorted(result, key=itemgetter(0))

        inv_list, b_list, a_list = zip(*[(row[1], row[3], row[4]) for row in result])
        inv_total = sum(inv_list)
        total_ann_contrib_b = sum(b_list)
        total_ann_contrib_a = sum(a_list)

        sector_inv = inv_total / self.totalInvested * 100
        result.append(['Total', inv_total, sector_inv, total_ann_contrib_b, total_ann_contrib_a])

        view = self.ui.sectorDetailsView
        sector_summary_details_model = SectorDetailsModel(result, self.sector_header, [])
        view.setModel(sector_summary_details_model)
        view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        view.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(len(self.sector_summary)):
            view.setRowHeight(i, 20)
        view.show()

    def start_external_process(self):
        self.p = QProcess()
        self.p.finished.connect(self.process_finished)
        self.p.start("python3", ['graphs.py'])

    def process_finished(self):
        pixmap = QPixmap(f'{self.outPathPrefix}/sector_details.png')
        self.ui.image_label.setPixmap(pixmap)
        pixmap2 = QPixmap(f'{self.outPathPrefix}/div_details.png')
        self.ui.graph_label.setPixmap(pixmap2)
        self.p = None


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
