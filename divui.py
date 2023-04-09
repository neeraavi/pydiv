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
        MainWindow.resize(1119, 865)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 1101, 771))
        self.tabWidget.setObjectName("tabWidget")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.summaryView = QtWidgets.QTableView(self.tab_1)
        self.summaryView.setGeometry(QtCore.QRect(10, 20, 1081, 301))
        font = QtGui.QFont()
        font.setFamily("Noto Mono")
        font.setPointSize(9)
        self.summaryView.setFont(font)
        self.summaryView.setAutoFillBackground(False)
        self.summaryView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
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
        self.transactionsView.setGeometry(QtCore.QRect(10, 360, 441, 371))
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
        self.dividendsView.setGeometry(QtCore.QRect(460, 360, 631, 371))
        font = QtGui.QFont()
        font.setFamily("Noto Mono")
        font.setPointSize(9)
        self.dividendsView.setFont(font)
        self.dividendsView.setObjectName("dividendsView")
        self.dividendsView.horizontalHeader().setStretchLastSection(False)
        self.dividendsView.verticalHeader().setVisible(False)
        self.dividendsView.verticalHeader().setDefaultSectionSize(18)
        self.dividendsView.verticalHeader().setMinimumSectionSize(16)
        self.mainFilter = QtWidgets.QLineEdit(self.tab_1)
        self.mainFilter.setGeometry(QtCore.QRect(20, 330, 113, 25))
        self.mainFilter.setObjectName("mainFilter")
        self.showClosedPositions = QtWidgets.QCheckBox(self.tab_1)
        self.showClosedPositions.setGeometry(QtCore.QRect(150, 330, 171, 23))
        self.showClosedPositions.setObjectName("showClosedPositions")
        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.dividendCalendar = QtWidgets.QGroupBox(self.tab_2)
        self.dividendCalendar.setGeometry(QtCore.QRect(0, 0, 591, 361))
        self.dividendCalendar.setObjectName("dividendCalendar")
        self.dividendCalendarView = QtWidgets.QTableView(self.dividendCalendar)
        self.dividendCalendarView.setGeometry(QtCore.QRect(10, 60, 571, 291))
        self.dividendCalendarView.setObjectName("dividendCalendarView")
        self.dividendCalendarView.verticalHeader().setDefaultSectionSize(21)
        self.dividendCalendarView.verticalHeader().setMinimumSectionSize(16)
        self.beforeTax = QtWidgets.QRadioButton(self.dividendCalendar)
        self.beforeTax.setGeometry(QtCore.QRect(10, 30, 112, 23))
        self.beforeTax.setObjectName("beforeTax")
        self.afterTax = QtWidgets.QRadioButton(self.dividendCalendar)
        self.afterTax.setGeometry(QtCore.QRect(130, 30, 112, 23))
        self.afterTax.setObjectName("afterTax")
        self.investmentCalendar = QtWidgets.QGroupBox(self.tab_2)
        self.investmentCalendar.setGeometry(QtCore.QRect(0, 360, 591, 351))
        self.investmentCalendar.setObjectName("investmentCalendar")
        self.investmentCalendarView = QtWidgets.QTableView(self.investmentCalendar)
        self.investmentCalendarView.setGeometry(QtCore.QRect(10, 31, 571, 311))
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
        self.calendarDetailsView.setGeometry(QtCore.QRect(600, 20, 491, 681))
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
        self.tabWidget.addTab(self.tab_3, "")
        self.btn_1 = QtWidgets.QPushButton(self.centralwidget)
        self.btn_1.setGeometry(QtCore.QRect(1020, 790, 89, 25))
        self.btn_1.setObjectName("btn_1")
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
        self.showClosedPositions.setText(_translate("MainWindow", "Show closed positions"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("MainWindow", "Summary"))
        self.dividendCalendar.setTitle(_translate("MainWindow", "Dividend calendar"))
        self.beforeTax.setText(_translate("MainWindow", "Before tax"))
        self.afterTax.setText(_translate("MainWindow", "After tax"))
        self.investmentCalendar.setTitle(_translate("MainWindow", "Investment calendar"))
        self.calendarDetailsMode.setText(_translate("MainWindow", "Investment details"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Calendar"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Diversification"))
        self.btn_1.setText(_translate("MainWindow", "OK"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
