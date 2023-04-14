# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'divui.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1119, 912)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 1101, 851))
        self.tabWidget.setObjectName("tabWidget")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.summaryView = QtWidgets.QTableView(self.tab_1)
        self.summaryView.setGeometry(QtCore.QRect(10, 10, 1081, 381))
        font = QtGui.QFont()
        font.setFamily("Fira Code")
        font.setPointSize(10)
        self.summaryView.setFont(font)
        self.summaryView.setAutoFillBackground(False)
        self.summaryView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.summaryView.setTabKeyNavigation(False)
        self.summaryView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.summaryView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.summaryView.setGridStyle(QtCore.Qt.SolidLine)
        self.summaryView.setSortingEnabled(True)
        self.summaryView.setCornerButtonEnabled(False)
        self.summaryView.setObjectName("summaryView")
        self.summaryView.horizontalHeader().setVisible(True)
        self.summaryView.horizontalHeader().setDefaultSectionSize(100)
        self.summaryView.horizontalHeader().setStretchLastSection(False)
        self.summaryView.verticalHeader().setVisible(False)
        self.summaryView.verticalHeader().setDefaultSectionSize(18)
        self.summaryView.verticalHeader().setMinimumSectionSize(16)
        self.summaryView.verticalHeader().setStretchLastSection(False)
        self.transactionsView = QtWidgets.QTableView(self.tab_1)
        self.transactionsView.setGeometry(QtCore.QRect(10, 440, 451, 371))
        font = QtGui.QFont()
        font.setFamily("Noto Mono")
        font.setPointSize(9)
        self.transactionsView.setFont(font)
        self.transactionsView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.transactionsView.setSortingEnabled(True)
        self.transactionsView.setObjectName("transactionsView")
        self.transactionsView.horizontalHeader().setStretchLastSection(False)
        self.transactionsView.verticalHeader().setVisible(False)
        self.transactionsView.verticalHeader().setDefaultSectionSize(18)
        self.transactionsView.verticalHeader().setMinimumSectionSize(16)
        self.dividendsView = QtWidgets.QTableView(self.tab_1)
        self.dividendsView.setGeometry(QtCore.QRect(470, 440, 621, 371))
        font = QtGui.QFont()
        font.setFamily("Noto Mono")
        font.setPointSize(9)
        self.dividendsView.setFont(font)
        self.dividendsView.setObjectName("dividendsView")
        self.dividendsView.horizontalHeader().setStretchLastSection(False)
        self.dividendsView.verticalHeader().setVisible(False)
        self.dividendsView.verticalHeader().setDefaultSectionSize(18)
        self.dividendsView.verticalHeader().setMinimumSectionSize(16)
        self.label = QtWidgets.QLabel(self.tab_1)
        self.label.setGeometry(QtCore.QRect(10, 410, 101, 17))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.tab_1)
        self.label_2.setGeometry(QtCore.QRect(460, 410, 67, 17))
        self.label_2.setObjectName("label_2")
        self.mainFilter = QtWidgets.QLineEdit(self.tab_1)
        self.mainFilter.setGeometry(QtCore.QRect(962, 400, 121, 25))
        self.mainFilter.setObjectName("mainFilter")
        self.showClosedPositions = QtWidgets.QCheckBox(self.tab_1)
        self.showClosedPositions.setGeometry(QtCore.QRect(730, 400, 211, 23))
        self.showClosedPositions.setObjectName("showClosedPositions")
        self.searchAllColumns = QtWidgets.QCheckBox(self.tab_1)
        self.searchAllColumns.setGeometry(QtCore.QRect(550, 400, 171, 23))
        self.searchAllColumns.setObjectName("searchAllColumns")
        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.dividendCalendar = QtWidgets.QGroupBox(self.tab_2)
        self.dividendCalendar.setGeometry(QtCore.QRect(0, 0, 591, 431))
        self.dividendCalendar.setObjectName("dividendCalendar")
        self.dividendCalendarView = QtWidgets.QTableView(self.dividendCalendar)
        self.dividendCalendarView.setGeometry(QtCore.QRect(10, 60, 571, 361))
        font = QtGui.QFont()
        font.setFamily("Noto Sans Mono")
        font.setPointSize(9)
        self.dividendCalendarView.setFont(font)
        self.dividendCalendarView.setAlternatingRowColors(True)
        self.dividendCalendarView.setObjectName("dividendCalendarView")
        self.dividendCalendarView.verticalHeader().setDefaultSectionSize(21)
        self.dividendCalendarView.verticalHeader().setMinimumSectionSize(16)
        self.beforeTax = QtWidgets.QRadioButton(self.dividendCalendar)
        self.beforeTax.setGeometry(QtCore.QRect(20, 30, 112, 23))
        self.beforeTax.setChecked(True)
        self.beforeTax.setObjectName("beforeTax")
        self.afterTax = QtWidgets.QRadioButton(self.dividendCalendar)
        self.afterTax.setGeometry(QtCore.QRect(130, 30, 112, 23))
        self.afterTax.setObjectName("afterTax")
        self.investmentCalendar = QtWidgets.QGroupBox(self.tab_2)
        self.investmentCalendar.setGeometry(QtCore.QRect(0, 440, 591, 381))
        self.investmentCalendar.setObjectName("investmentCalendar")
        self.investmentCalendarView = QtWidgets.QTableView(self.investmentCalendar)
        self.investmentCalendarView.setGeometry(QtCore.QRect(10, 30, 571, 341))
        font = QtGui.QFont()
        font.setFamily("Fira Code")
        font.setPointSize(10)
        self.investmentCalendarView.setFont(font)
        self.investmentCalendarView.setAlternatingRowColors(True)
        self.investmentCalendarView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.investmentCalendarView.setCornerButtonEnabled(False)
        self.investmentCalendarView.setObjectName("investmentCalendarView")
        self.investmentCalendarView.horizontalHeader().setStretchLastSection(True)
        self.investmentCalendarView.verticalHeader().setDefaultSectionSize(18)
        self.investmentCalendarView.verticalHeader().setMinimumSectionSize(16)
        self.investmentCalendarView.verticalHeader().setStretchLastSection(True)
        self.calendarDetailsView = QtWidgets.QTableView(self.tab_2)
        self.calendarDetailsView.setGeometry(QtCore.QRect(600, 20, 491, 791))
        self.calendarDetailsView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.calendarDetailsView.setObjectName("calendarDetailsView")
        self.calendarDetailsView.verticalHeader().setVisible(False)
        self.calendarDetailsView.verticalHeader().setDefaultSectionSize(21)
        self.calendarDetailsView.verticalHeader().setMinimumSectionSize(16)
        self.calendarDetailsMode = QtWidgets.QLabel(self.tab_2)
        self.calendarDetailsMode.setGeometry(QtCore.QRect(600, 0, 231, 17))
        self.calendarDetailsMode.setObjectName("calendarDetailsMode")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.sectorSummaryView = QtWidgets.QTableView(self.tab_3)
        self.sectorSummaryView.setGeometry(QtCore.QRect(10, 10, 491, 431))
        self.sectorSummaryView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.sectorSummaryView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.sectorSummaryView.setObjectName("sectorSummaryView")
        self.sectorDetailsView = QtWidgets.QTableView(self.tab_3)
        self.sectorDetailsView.setGeometry(QtCore.QRect(510, 0, 581, 441))
        self.sectorDetailsView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.sectorDetailsView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.sectorDetailsView.setObjectName("sectorDetailsView")
        self.image_label = QtWidgets.QLabel(self.tab_3)
        self.image_label.setGeometry(QtCore.QRect(10, 450, 1071, 361))
        self.image_label.setObjectName("image_label")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.graph_label = QtWidgets.QLabel(self.tab)
        self.graph_label.setGeometry(QtCore.QRect(10, 10, 1071, 791))
        self.graph_label.setObjectName("graph_label")
        self.tabWidget.addTab(self.tab, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1119, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Transactions"))
        self.label_2.setText(_translate("MainWindow", "Dividends"))
        self.showClosedPositions.setText(_translate("MainWindow", "F3: Show closed positions"))
        self.searchAllColumns.setText(_translate("MainWindow", "F2: Search all columns"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("MainWindow", "Summary"))
        self.dividendCalendar.setTitle(_translate("MainWindow", "Dividend calendar"))
        self.beforeTax.setText(_translate("MainWindow", "Before tax"))
        self.afterTax.setText(_translate("MainWindow", "After tax"))
        self.investmentCalendar.setTitle(_translate("MainWindow", "Investment calendar"))
        self.calendarDetailsMode.setText(_translate("MainWindow", "Investment details"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Calendar"))
        self.image_label.setText(_translate("MainWindow", "Sector"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Diversification"))
        self.graph_label.setText(_translate("MainWindow", "Graph"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Progress"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
