# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'development-resources/Qt UI/NewUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class UI(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1345, 750)
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        MainWindow.setStyleSheet("centralwidget {\n"
"  background-color: #DBDBDB;\n"
"}\n"
"QMainWindow { background-color: #f4f4f4 }\n"
"\n"
"QPushButton {\n"
"  background-color: #FFFFFF;\n"
"  color: #242424;\n"
"}\n"
"\n"
"QComboBox {\n"
"  background-color: #FFFFFF;\n"
"  color: #242424;\n"
"}\n"
"\n"
"\n"
"QTabWidget {\n"
"    background-color: #FFFFFF;\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                stop: 0 #f4f4f4, stop: 1 #FFFFFF);            \n"
"    border-top-left-radius: 4px;\n"
"    border-top-right-radius: 4px;\n"
"    padding: 7px;\n"
"    border: 1px solid #b6b6b6;\n"
"}\n"
"\n"
"QTabBar::tab:selected {\n"
"    border-color: #9B9B9B;\n"
"    border-bottom-color: #C2C7CB; /* same as pane color */\n"
"    background-color: #f4f4f4;\n"
"}\n"
"\n"
"QTabBar::tab:!selected {\n"
"    margin-top: 2px; /* make non-selected tabs look smaller */\n"
"}\n"
"\n"
"\n"
"")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.repeatCombo = QtWidgets.QComboBox(self.centralwidget)
        self.repeatCombo.setStyleSheet("")
        self.repeatCombo.setObjectName("repeatCombo")
        self.repeatCombo.addItem("")
        self.repeatCombo.addItem("")
        self.repeatCombo.addItem("")
        self.gridLayout_5.addWidget(self.repeatCombo, 0, 0, 1, 1)
        self.lastfmBtn = QtWidgets.QPushButton(self.centralwidget)
        self.lastfmBtn.setStyleSheet("")
        self.lastfmBtn.setText("")
        self.lastfmBtn.setObjectName("lastfmBtn")
        self.gridLayout_5.addWidget(self.lastfmBtn, 0, 1, 1, 1)
        self.verticalLayout_8.addLayout(self.gridLayout_5)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.playPauseBtn = QtWidgets.QPushButton(self.centralwidget)
        self.playPauseBtn.setStyleSheet("")
        self.playPauseBtn.setText("")
        self.playPauseBtn.setObjectName("playPauseBtn")
        self.gridLayout.addWidget(self.playPauseBtn, 0, 1, 1, 1)
        self.prevBtn = QtWidgets.QPushButton(self.centralwidget)
        self.prevBtn.setStyleSheet("")
        self.prevBtn.setText("")
        self.prevBtn.setObjectName("prevBtn")
        self.gridLayout.addWidget(self.prevBtn, 0, 0, 1, 1)
        self.nextBtn = QtWidgets.QPushButton(self.centralwidget)
        self.nextBtn.setStyleSheet("")
        self.nextBtn.setText("")
        self.nextBtn.setObjectName("nextBtn")
        self.gridLayout.addWidget(self.nextBtn, 0, 2, 1, 1)
        self.verticalLayout_8.addLayout(self.gridLayout)
        self.gridLayout_4.addLayout(self.verticalLayout_8, 0, 0, 1, 1)
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.trackLbl = QtWidgets.QLabel(self.centralwidget)
        self.trackLbl.setText("")
        self.trackLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.trackLbl.setObjectName("trackLbl")
        self.verticalLayout_9.addWidget(self.trackLbl)
        self.timeLbl = QtWidgets.QLabel(self.centralwidget)
        self.timeLbl.setText("")
        self.timeLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.timeLbl.setObjectName("timeLbl")
        self.verticalLayout_9.addWidget(self.timeLbl)
        self.trackProgress = QtWidgets.QSlider(self.centralwidget)
        self.trackProgress.setOrientation(QtCore.Qt.Horizontal)
        self.trackProgress.setObjectName("trackProgress")
        self.verticalLayout_9.addWidget(self.trackProgress)
        self.gridLayout_4.addLayout(self.verticalLayout_9, 0, 1, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.volumeLbl = QtWidgets.QLabel(self.centralwidget)
        self.volumeLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.volumeLbl.setObjectName("volumeLbl")
        self.verticalLayout_3.addWidget(self.volumeLbl)
        self.volumeSlider = QtWidgets.QSlider(self.centralwidget)
        self.volumeSlider.setStyleSheet("")
        self.volumeSlider.setPageStep(5)
        self.volumeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.volumeSlider.setObjectName("volumeSlider")
        self.verticalLayout_3.addWidget(self.volumeSlider)
        self.gridLayout_4.addLayout(self.verticalLayout_3, 0, 2, 1, 1)
        self.gridLayout_4.setColumnStretch(0, 20)
        self.gridLayout_4.setColumnStretch(1, 60)
        self.gridLayout_4.setColumnStretch(2, 20)
        self.verticalLayout_2.addLayout(self.gridLayout_4)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.topMenuTabs = QtWidgets.QTabWidget(self.centralwidget)
        self.topMenuTabs.setStyleSheet("")
        self.topMenuTabs.setObjectName("topMenuTabs")
        self.nowPlayingTab = QtWidgets.QWidget()
        self.nowPlayingTab.setStyleSheet("")
        self.nowPlayingTab.setObjectName("nowPlayingTab")
        self.nowPlayingWebInfo = QtWebEngineWidgets.QWebEngineView(self.nowPlayingTab)
        self.nowPlayingWebInfo.setGeometry(QtCore.QRect(950, 260, 371, 191))
        self.nowPlayingWebInfo.setObjectName("nowPlayingWebInfo")
        self.playlist_view = QtWidgets.QListView(self.nowPlayingTab)
        self.playlist_view.setGeometry(QtCore.QRect(0, 0, 201, 601))
        self.playlist_view.setObjectName("playlist_view")
        self.topMenuTabs.addTab(self.nowPlayingTab, "")
        self.browseTab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.browseTab.sizePolicy().hasHeightForWidth())
        self.browseTab.setSizePolicy(sizePolicy)
        self.browseTab.setStyleSheet("")
        self.browseTab.setObjectName("browseTab")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.browseTab)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout()
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.typeOrderByCombo = QtWidgets.QComboBox(self.browseTab)
        self.typeOrderByCombo.setStyleSheet("")
        self.typeOrderByCombo.setObjectName("typeOrderByCombo")
        self.typeOrderByCombo.addItem("")
        self.typeOrderByCombo.addItem("")
        self.horizontalLayout_2.addWidget(self.typeOrderByCombo)
        self.typeBrowseCombo = QtWidgets.QComboBox(self.browseTab)
        self.typeBrowseCombo.setStyleSheet("")
        self.typeBrowseCombo.setObjectName("typeBrowseCombo")
        self.typeBrowseCombo.addItem("")
        self.typeBrowseCombo.addItem("")
        self.typeBrowseCombo.addItem("")
        self.horizontalLayout_2.addWidget(self.typeBrowseCombo)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 13)
        self.verticalLayout_13.addLayout(self.horizontalLayout_2)
        self.verticalLayout_12 = QtWidgets.QVBoxLayout()
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.quickFilter = QtWidgets.QLineEdit(self.browseTab)
        self.quickFilter.setObjectName("quickFilter")
        self.verticalLayout_12.addWidget(self.quickFilter)
        self.browseList = QtWidgets.QListView(self.browseTab)
        self.browseList.setStyleSheet("")
        self.browseList.setObjectName("browseList")
        self.verticalLayout_12.addWidget(self.browseList)
        self.verticalLayout_13.addLayout(self.verticalLayout_12)
        self.horizontalLayout_3.addLayout(self.verticalLayout_13)
        self.verticalLayout_11 = QtWidgets.QVBoxLayout()
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.treeViewFilter = QtWidgets.QLineEdit(self.browseTab)
        self.treeViewFilter.setObjectName("treeViewFilter")
        self.verticalLayout_11.addWidget(self.treeViewFilter)
        self.browseTreeView = QtWidgets.QTreeView(self.browseTab)
        self.browseTreeView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.browseTreeView.setObjectName("browseTreeView")
        self.browseTreeView.header().setMinimumSectionSize(40)
        self.verticalLayout_11.addWidget(self.browseTreeView)
        self.horizontalLayout_3.addLayout(self.verticalLayout_11)
        self.horizontalLayout_3.setStretch(0, 20)
        self.horizontalLayout_3.setStretch(1, 80)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_3)
        self.additionalInfoFrame = QtWidgets.QWidget(self.browseTab)
        self.additionalInfoFrame.setObjectName("additionalInfoFrame")
        self.horizontalLayout_5.addWidget(self.additionalInfoFrame)
        self.horizontalLayout_5.setStretch(0, 6)
        self.horizontalLayout_5.setStretch(1, 1)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_5)
        self.topMenuTabs.addTab(self.browseTab, "")
        self.searchTab = QtWidgets.QWidget()
        self.searchTab.setStyleSheet("")
        self.searchTab.setObjectName("searchTab")
        self.searchTabWidget = QtWidgets.QTabWidget(self.searchTab)
        self.searchTabWidget.setGeometry(QtCore.QRect(17, 9, 421, 561))
        self.searchTabWidget.setStyleSheet("")
        self.searchTabWidget.setObjectName("searchTabWidget")
        self.searchTabGeneral = QtWidgets.QWidget()
        self.searchTabGeneral.setObjectName("searchTabGeneral")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.searchTabGeneral)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.topSearchLayout = QtWidgets.QVBoxLayout()
        self.topSearchLayout.setObjectName("topSearchLayout")
        self.SearchOptionsLayout = QtWidgets.QGridLayout()
        self.SearchOptionsLayout.setObjectName("SearchOptionsLayout")
        self.startDateLbl = QtWidgets.QLabel(self.searchTabGeneral)
        self.startDateLbl.setObjectName("startDateLbl")
        self.SearchOptionsLayout.addWidget(self.startDateLbl, 3, 1, 1, 1)
        self.artistFilterLbl = QtWidgets.QLabel(self.searchTabGeneral)
        self.artistFilterLbl.setObjectName("artistFilterLbl")
        self.SearchOptionsLayout.addWidget(self.artistFilterLbl, 0, 1, 1, 1)
        self.artistFilter = QtWidgets.QLineEdit(self.searchTabGeneral)
        self.artistFilter.setObjectName("artistFilter")
        self.SearchOptionsLayout.addWidget(self.artistFilter, 0, 3, 1, 1)
        self.dateFrom = QtWidgets.QDateEdit(self.searchTabGeneral)
        self.dateFrom.setDateTime(QtCore.QDateTime(QtCore.QDate(1950, 1, 1), QtCore.QTime(0, 0, 0)))
        self.dateFrom.setMaximumDate(QtCore.QDate(2016, 1, 1))
        self.dateFrom.setObjectName("dateFrom")
        self.SearchOptionsLayout.addWidget(self.dateFrom, 3, 3, 1, 1)
        self.genreFilterLbl = QtWidgets.QLabel(self.searchTabGeneral)
        self.genreFilterLbl.setObjectName("genreFilterLbl")
        self.SearchOptionsLayout.addWidget(self.genreFilterLbl, 1, 1, 1, 1)
        self.endDateLbl = QtWidgets.QLabel(self.searchTabGeneral)
        self.endDateLbl.setObjectName("endDateLbl")
        self.SearchOptionsLayout.addWidget(self.endDateLbl, 4, 1, 1, 1)
        self.dateTo = QtWidgets.QDateEdit(self.searchTabGeneral)
        self.dateTo.setMinimumDate(QtCore.QDate(1960, 1, 1))
        self.dateTo.setDate(QtCore.QDate(2017, 1, 1))
        self.dateTo.setObjectName("dateTo")
        self.SearchOptionsLayout.addWidget(self.dateTo, 4, 3, 1, 1)
        self.genreFilter = QtWidgets.QLineEdit(self.searchTabGeneral)
        self.genreFilter.setObjectName("genreFilter")
        self.SearchOptionsLayout.addWidget(self.genreFilter, 1, 3, 1, 1)
        self.trackNameFilter = QtWidgets.QLineEdit(self.searchTabGeneral)
        self.trackNameFilter.setObjectName("trackNameFilter")
        self.SearchOptionsLayout.addWidget(self.trackNameFilter, 2, 3, 1, 1)
        self.trackNameLbl = QtWidgets.QLabel(self.searchTabGeneral)
        self.trackNameLbl.setObjectName("trackNameLbl")
        self.SearchOptionsLayout.addWidget(self.trackNameLbl, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.SearchOptionsLayout.addItem(spacerItem, 1, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.SearchOptionsLayout.addItem(spacerItem1, 3, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.SearchOptionsLayout.addItem(spacerItem2, 2, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.SearchOptionsLayout.addItem(spacerItem3, 4, 0, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.SearchOptionsLayout.addItem(spacerItem4, 0, 0, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.SearchOptionsLayout.addItem(spacerItem5, 6, 0, 1, 1)
        self.orderByLbl = QtWidgets.QLabel(self.searchTabGeneral)
        self.orderByLbl.setObjectName("orderByLbl")
        self.SearchOptionsLayout.addWidget(self.orderByLbl, 5, 1, 1, 1)
        self.orderByFilter = QtWidgets.QComboBox(self.searchTabGeneral)
        self.orderByFilter.setObjectName("orderByFilter")
        self.orderByFilter.addItem("")
        self.orderByFilter.addItem("")
        self.orderByFilter.addItem("")
        self.orderByFilter.addItem("")
        self.SearchOptionsLayout.addWidget(self.orderByFilter, 5, 3, 1, 1)
        self.numResultsLbl = QtWidgets.QLabel(self.searchTabGeneral)
        self.numResultsLbl.setObjectName("numResultsLbl")
        self.SearchOptionsLayout.addWidget(self.numResultsLbl, 6, 1, 1, 1)
        self.numResultsSpinbox = QtWidgets.QSpinBox(self.searchTabGeneral)
        self.numResultsSpinbox.setMaximum(10000)
        self.numResultsSpinbox.setProperty("value", 500)
        self.numResultsSpinbox.setObjectName("numResultsSpinbox")
        self.SearchOptionsLayout.addWidget(self.numResultsSpinbox, 6, 3, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.SearchOptionsLayout.addItem(spacerItem6, 5, 0, 1, 1)
        self.topSearchLayout.addLayout(self.SearchOptionsLayout)
        self.searchBtn = QtWidgets.QPushButton(self.searchTabGeneral)
        self.searchBtn.setObjectName("searchBtn")
        self.topSearchLayout.addWidget(self.searchBtn)
        self.horizontalLayout_9.addLayout(self.topSearchLayout)
        self.searchTabWidget.addTab(self.searchTabGeneral, "")
        self.geographyTab = QtWidgets.QWidget()
        self.geographyTab.setObjectName("geographyTab")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.geographyTab)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.geographyLayout = QtWidgets.QGridLayout()
        self.geographyLayout.setObjectName("geographyLayout")
        self.vanueLbl = QtWidgets.QLabel(self.geographyTab)
        self.vanueLbl.setStyleSheet("")
        self.vanueLbl.setObjectName("vanueLbl")
        self.geographyLayout.addWidget(self.vanueLbl, 0, 1, 1, 1)
        self.venueFilter = QtWidgets.QLineEdit(self.geographyTab)
        self.venueFilter.setStyleSheet("background: #FFFFFF;")
        self.venueFilter.setObjectName("venueFilter")
        self.geographyLayout.addWidget(self.venueFilter, 0, 3, 1, 1)
        self.locationFilter = QtWidgets.QLineEdit(self.geographyTab)
        self.locationFilter.setStyleSheet("background: #FFFFFF;")
        self.locationFilter.setObjectName("locationFilter")
        self.geographyLayout.addWidget(self.locationFilter, 1, 3, 1, 1)
        self.locationFilterLbl = QtWidgets.QLabel(self.geographyTab)
        self.locationFilterLbl.setStyleSheet("")
        self.locationFilterLbl.setObjectName("locationFilterLbl")
        self.geographyLayout.addWidget(self.locationFilterLbl, 1, 1, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.geographyLayout.addItem(spacerItem7, 0, 0, 1, 1)
        self.countryFilterLbl = QtWidgets.QLabel(self.geographyTab)
        self.countryFilterLbl.setStyleSheet("")
        self.countryFilterLbl.setObjectName("countryFilterLbl")
        self.geographyLayout.addWidget(self.countryFilterLbl, 3, 1, 1, 1)
        self.countryFilter = QtWidgets.QLineEdit(self.geographyTab)
        self.countryFilter.setStyleSheet("background: #FFFFFF;")
        self.countryFilter.setObjectName("countryFilter")
        self.geographyLayout.addWidget(self.countryFilter, 3, 3, 1, 1)
        spacerItem8 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.geographyLayout.addItem(spacerItem8, 1, 0, 1, 1)
        spacerItem9 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.geographyLayout.addItem(spacerItem9, 3, 0, 1, 1)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.geographyLayout.addItem(spacerItem10, 5, 1, 1, 1)
        self.locationRangeFilter = QtWidgets.QLineEdit(self.geographyTab)
        self.locationRangeFilter.setStyleSheet("background: #FFFFFF;")
        self.locationRangeFilter.setObjectName("locationRangeFilter")
        self.geographyLayout.addWidget(self.locationRangeFilter, 2, 3, 1, 1)
        self.rangeFilterLbl = QtWidgets.QLabel(self.geographyTab)
        self.rangeFilterLbl.setStyleSheet("")
        self.rangeFilterLbl.setObjectName("rangeFilterLbl")
        self.geographyLayout.addWidget(self.rangeFilterLbl, 2, 1, 1, 1)
        spacerItem11 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.geographyLayout.addItem(spacerItem11, 2, 0, 1, 1)
        self.geographyLayout.setColumnStretch(1, 2)
        self.geographyLayout.setColumnStretch(3, 6)
        self.geographyLayout.setRowStretch(0, 2)
        self.geographyLayout.setRowStretch(1, 2)
        self.geographyLayout.setRowStretch(2, 2)
        self.geographyLayout.setRowStretch(3, 2)
        self.geographyLayout.setRowStretch(4, 2)
        self.geographyLayout.setRowStretch(5, 5)
        self.horizontalLayout_10.addLayout(self.geographyLayout)
        self.searchTabWidget.addTab(self.geographyTab, "")
        self.AdvTab = QtWidgets.QWidget()
        self.AdvTab.setObjectName("AdvTab")
        self.gridLayoutWidget_6 = QtWidgets.QWidget(self.AdvTab)
        self.gridLayoutWidget_6.setGeometry(QtCore.QRect(10, 40, 301, 461))
        self.gridLayoutWidget_6.setObjectName("gridLayoutWidget_6")
        self.advancedSearchLayout = QtWidgets.QGridLayout(self.gridLayoutWidget_6)
        self.advancedSearchLayout.setContentsMargins(0, 0, 0, 0)
        self.advancedSearchLayout.setObjectName("advancedSearchLayout")
        self.label_2 = QtWidgets.QLabel(self.AdvTab)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 121, 20))
        self.label_2.setObjectName("label_2")
        self.matchingPolicyCombo = QtWidgets.QComboBox(self.AdvTab)
        self.matchingPolicyCombo.setGeometry(QtCore.QRect(120, 10, 81, 21))
        self.matchingPolicyCombo.setObjectName("matchingPolicyCombo")
        self.matchingPolicyCombo.addItem("")
        self.matchingPolicyCombo.addItem("")
        self.addConditionBtn = QtWidgets.QPushButton(self.AdvTab)
        self.addConditionBtn.setGeometry(QtCore.QRect(210, 10, 41, 21))
        self.addConditionBtn.setObjectName("addConditionBtn")
        self.removeConditionBtn = QtWidgets.QPushButton(self.AdvTab)
        self.removeConditionBtn.setGeometry(QtCore.QRect(260, 10, 41, 21))
        self.removeConditionBtn.setObjectName("removeConditionBtn")
        self.searchTabWidget.addTab(self.AdvTab, "")
        self.ViewsTab = QtWidgets.QWidget()
        self.ViewsTab.setObjectName("ViewsTab")
        self.gridLayoutWidget_4 = QtWidgets.QWidget(self.ViewsTab)
        self.gridLayoutWidget_4.setGeometry(QtCore.QRect(0, 20, 291, 92))
        self.gridLayoutWidget_4.setObjectName("gridLayoutWidget_4")
        self.viewsLayout = QtWidgets.QGridLayout(self.gridLayoutWidget_4)
        self.viewsLayout.setContentsMargins(0, 0, 0, 0)
        self.viewsLayout.setObjectName("viewsLayout")
        self.mapViewChk = QtWidgets.QCheckBox(self.gridLayoutWidget_4)
        self.mapViewChk.setChecked(True)
        self.mapViewChk.setObjectName("mapViewChk")
        self.viewsLayout.addWidget(self.mapViewChk, 1, 1, 1, 1)
        self.timelineViewChk = QtWidgets.QCheckBox(self.gridLayoutWidget_4)
        self.timelineViewChk.setChecked(True)
        self.timelineViewChk.setObjectName("timelineViewChk")
        self.viewsLayout.addWidget(self.timelineViewChk, 2, 1, 1, 1)
        self.tableViewChk = QtWidgets.QCheckBox(self.gridLayoutWidget_4)
        self.tableViewChk.setChecked(True)
        self.tableViewChk.setObjectName("tableViewChk")
        self.viewsLayout.addWidget(self.tableViewChk, 0, 1, 1, 1)
        spacerItem12 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.viewsLayout.addItem(spacerItem12, 0, 0, 1, 1)
        spacerItem13 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.viewsLayout.addItem(spacerItem13, 1, 0, 1, 1)
        spacerItem14 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.viewsLayout.addItem(spacerItem14, 2, 0, 1, 1)
        self.viewsLayout.setColumnStretch(0, 2)
        self.viewsLayout.setColumnStretch(1, 17)
        self.searchTabWidget.addTab(self.ViewsTab, "")
        self.topMenuTabs.addTab(self.searchTab, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.tab_3)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label = QtWidgets.QLabel(self.tab_3)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_5.addWidget(self.label)
        self.savedSearchesList = QtWidgets.QListWidget(self.tab_3)
        self.savedSearchesList.setObjectName("savedSearchesList")
        self.verticalLayout_5.addWidget(self.savedSearchesList)
        self.horizontalLayout.addLayout(self.verticalLayout_5)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_3 = QtWidgets.QLabel(self.tab_3)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_6.addWidget(self.label_3)
        self.listWidget_2 = QtWidgets.QListWidget(self.tab_3)
        self.listWidget_2.setObjectName("listWidget_2")
        self.verticalLayout_6.addWidget(self.listWidget_2)
        self.horizontalLayout.addLayout(self.verticalLayout_6)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_5 = QtWidgets.QLabel(self.tab_3)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_7.addWidget(self.label_5)
        self.listView_3 = QtWidgets.QListView(self.tab_3)
        self.listView_3.setObjectName("listView_3")
        self.verticalLayout_7.addWidget(self.listView_3)
        self.horizontalLayout.addLayout(self.verticalLayout_7)
        self.verticalLayout_10.addLayout(self.horizontalLayout)
        self.label_6 = QtWidgets.QLabel(self.tab_3)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_10.addWidget(self.label_6)
        self.historyTableWidget = QtWidgets.QTableWidget(self.tab_3)
        self.historyTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.historyTableWidget.setObjectName("historyTableWidget")
        self.historyTableWidget.setColumnCount(0)
        self.historyTableWidget.setRowCount(0)
        self.verticalLayout_10.addWidget(self.historyTableWidget)
        self.verticalLayout_10.setStretch(0, 2)
        self.verticalLayout_10.setStretch(2, 5)
        self.verticalLayout_14.addLayout(self.verticalLayout_10)
        self.topMenuTabs.addTab(self.tab_3, "")
        self.PreferencesTab = QtWidgets.QWidget()
        self.PreferencesTab.setObjectName("PreferencesTab")
        self.tabWidget = QtWidgets.QTabWidget(self.PreferencesTab)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 1141, 581))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")
        self.prefApplicationTab = QtWidgets.QWidget()
        self.prefApplicationTab.setObjectName("prefApplicationTab")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.prefApplicationTab)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setSpacing(1)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_4 = QtWidgets.QLabel(self.prefApplicationTab)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_6.addWidget(self.label_4)
        self.preferredFormatCombo = QtWidgets.QComboBox(self.prefApplicationTab)
        self.preferredFormatCombo.setObjectName("preferredFormatCombo")
        self.preferredFormatCombo.addItem("")
        self.preferredFormatCombo.addItem("")
        self.preferredFormatCombo.addItem("")
        self.preferredFormatCombo.addItem("")
        self.preferredFormatCombo.addItem("")
        self.horizontalLayout_6.addWidget(self.preferredFormatCombo)
        self.horizontalLayout_6.setStretch(1, 2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_6)
        self.debugChk = QtWidgets.QCheckBox(self.prefApplicationTab)
        self.debugChk.setChecked(False)
        self.debugChk.setObjectName("debugChk")
        self.verticalLayout_4.addWidget(self.debugChk)
        spacerItem15 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_4.addItem(spacerItem15)
        self.verticalLayout_4.setStretch(0, 1)
        self.verticalLayout_4.setStretch(1, 1)
        self.verticalLayout_4.setStretch(2, 4)
        self.horizontalLayout_7.addLayout(self.verticalLayout_4)
        spacerItem16 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_7.addItem(spacerItem16)
        spacerItem17 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_7.addItem(spacerItem17)
        spacerItem18 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_7.addItem(spacerItem18)
        self.horizontalLayout_7.setStretch(0, 2)
        self.horizontalLayout_7.setStretch(3, 5)
        self.tabWidget.addTab(self.prefApplicationTab, "")
        self.prefLastFMTab = QtWidgets.QWidget()
        self.prefLastFMTab.setObjectName("prefLastFMTab")
        self.lastfmStatus = QtWidgets.QPushButton(self.prefLastFMTab)
        self.lastfmStatus.setGeometry(QtCore.QRect(10, 10, 151, 31))
        self.lastfmStatus.setText("")
        self.lastfmStatus.setObjectName("lastfmStatus")
        self.tabWidget.addTab(self.prefLastFMTab, "")
        self.topMenuTabs.addTab(self.PreferencesTab, "")
        self.verticalLayout.addWidget(self.topMenuTabs)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.statusbar.setFont(font)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.topMenuTabs.setCurrentIndex(2)
        self.searchTabWidget.setCurrentIndex(2)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "eTree Browser"))
        self.repeatCombo.setItemText(0, _translate("MainWindow", "Repeat All"))
        self.repeatCombo.setItemText(1, _translate("MainWindow", "Repeat Current"))
        self.repeatCombo.setItemText(2, _translate("MainWindow", "Shuffle"))
        self.volumeLbl.setText(_translate("MainWindow", "Volume"))
        self.topMenuTabs.setTabText(self.topMenuTabs.indexOf(self.nowPlayingTab), _translate("MainWindow", "Now Playing"))
        self.typeOrderByCombo.setItemText(0, _translate("MainWindow", "Asc"))
        self.typeOrderByCombo.setItemText(1, _translate("MainWindow", "Desc"))
        self.typeBrowseCombo.setItemText(0, _translate("MainWindow", "Artist"))
        self.typeBrowseCombo.setItemText(1, _translate("MainWindow", "Genre"))
        self.typeBrowseCombo.setItemText(2, _translate("MainWindow", "Location"))
        self.quickFilter.setPlaceholderText(_translate("MainWindow", "Filter browse tags"))
        self.treeViewFilter.setPlaceholderText(_translate("MainWindow", "Filter performances"))
        self.topMenuTabs.setTabText(self.topMenuTabs.indexOf(self.browseTab), _translate("MainWindow", "Browse"))
        self.startDateLbl.setText(_translate("MainWindow", "Start Date"))
        self.artistFilterLbl.setText(_translate("MainWindow", "Artist"))
        self.dateFrom.setDisplayFormat(_translate("MainWindow", "yyyy-MM-dd"))
        self.genreFilterLbl.setText(_translate("MainWindow", "Genre"))
        self.endDateLbl.setText(_translate("MainWindow", "End Date"))
        self.dateTo.setDisplayFormat(_translate("MainWindow", "yyyy-MM-dd"))
        self.trackNameLbl.setText(_translate("MainWindow", "Track Name"))
        self.orderByLbl.setText(_translate("MainWindow", "Order By"))
        self.orderByFilter.setItemText(0, _translate("MainWindow", "Artist"))
        self.orderByFilter.setItemText(1, _translate("MainWindow", "Date"))
        self.orderByFilter.setItemText(2, _translate("MainWindow", "Label"))
        self.orderByFilter.setItemText(3, _translate("MainWindow", "Location"))
        self.numResultsLbl.setText(_translate("MainWindow", "Num. Results"))
        self.searchBtn.setText(_translate("MainWindow", "Search"))
        self.searchTabWidget.setTabText(self.searchTabWidget.indexOf(self.searchTabGeneral), _translate("MainWindow", "General"))
        self.vanueLbl.setText(_translate("MainWindow", "Venue"))
        self.locationFilterLbl.setText(_translate("MainWindow", "Location"))
        self.countryFilterLbl.setText(_translate("MainWindow", "Country"))
        self.rangeFilterLbl.setText(_translate("MainWindow", "Range (KM)"))
        self.searchTabWidget.setTabText(self.searchTabWidget.indexOf(self.geographyTab), _translate("MainWindow", "Geography"))
        self.label_2.setText(_translate("MainWindow", "Matching policy:"))
        self.matchingPolicyCombo.setItemText(0, _translate("MainWindow", "ALL"))
        self.matchingPolicyCombo.setItemText(1, _translate("MainWindow", "OR"))
        self.addConditionBtn.setText(_translate("MainWindow", "+"))
        self.removeConditionBtn.setText(_translate("MainWindow", "-"))
        self.searchTabWidget.setTabText(self.searchTabWidget.indexOf(self.AdvTab), _translate("MainWindow", "Advanced"))
        self.mapViewChk.setText(_translate("MainWindow", "Map"))
        self.timelineViewChk.setText(_translate("MainWindow", "Timeline"))
        self.tableViewChk.setText(_translate("MainWindow", "Table"))
        self.searchTabWidget.setTabText(self.searchTabWidget.indexOf(self.ViewsTab), _translate("MainWindow", "Views"))
        self.topMenuTabs.setTabText(self.topMenuTabs.indexOf(self.searchTab), _translate("MainWindow", "Search"))
        self.label.setText(_translate("MainWindow", "Saved Searches"))
        self.label_3.setText(_translate("MainWindow", "Most Played Tracks"))
        self.label_5.setText(_translate("MainWindow", "Placeholder"))
        self.label_6.setText(_translate("MainWindow", "Playback History"))
        self.topMenuTabs.setTabText(self.topMenuTabs.indexOf(self.tab_3), _translate("MainWindow", "History"))
        self.label_4.setText(_translate("MainWindow", "Preferred Format:"))
        self.preferredFormatCombo.setItemText(0, _translate("MainWindow", "MP3 (64Kbps)"))
        self.preferredFormatCombo.setItemText(1, _translate("MainWindow", "MP3 (VBR)"))
        self.preferredFormatCombo.setItemText(2, _translate("MainWindow", "FLAC"))
        self.preferredFormatCombo.setItemText(3, _translate("MainWindow", "OGG"))
        self.preferredFormatCombo.setItemText(4, _translate("MainWindow", "SHN"))
        self.debugChk.setText(_translate("MainWindow", "Show Debug Interface"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.prefApplicationTab), _translate("MainWindow", "Application"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.prefLastFMTab), _translate("MainWindow", "Last.FM"))
        self.topMenuTabs.setTabText(self.topMenuTabs.indexOf(self.PreferencesTab), _translate("MainWindow", "Preferences"))

from PyQt5 import QtWebEngineWidgets