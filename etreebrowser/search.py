from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
import application
import cache
import view
from math import sin, cos, sqrt, atan2, radians
import graph
import view
import time
import traceback
import sys

class searchForm():
  """
  Initializes an instance of the search form, which contains the search and results tabs.
  """
  def __init__(self, app, parent=None):
    """
    Create an instance of the search form class.

    Parameters
    ----------
    app : instance
        Reference to the main application module.
    """

    # Store reference to main-level tab
    self.app = app
    self.topLevelTab = app.searchTab
    self.topLevelSearchLayout = QtWidgets.QHBoxLayout()
    self.leftSide = self.generate_left_side()
    self.rightSide = self.generate_right_side()
    self.topLevelSearchLayout.addWidget(self.leftSide)
    self.topLevelSearchLayout.addWidget(self.rightSide)

    # Set spanning between left / right sides of top-level layout
    self.topLevelSearchLayout.setStretch(0, 2)
    self.topLevelSearchLayout.setStretch(1, 8)

    # Set auto-completes
    self.artistFilter.setCompleter(self.app.auto_comp(self.app.cache.load('artistList')))
    self.genreFilter.setCompleter(self.app.auto_comp(self.app.cache.load('genreList')))
    self.locationFilter.setCompleter(self.app.auto_comp(self.app.cache.load('newReversedGroupedLocations')))
    self.countryFilter.setCompleter(self.app.auto_comp(self.app.cache.load('countries')))

    # Set layout
    self.topLevelTab.setLayout(self.topLevelSearchLayout)

  def generate_left_side(self):
    """
    Generates the left side of the search form (not the data views, but the search form, results tab
    and all widgets held within.
    """

    # Create our search form
    self.searchFormVerticalWidget = QtWidgets.QWidget(self.app.searchTab)
    self.searchFormVerticalLayout = QtWidgets.QVBoxLayout(self.searchFormVerticalWidget)
    self.searchFormVerticalLayout.addWidget(self.generate_search_tab())

    self.searchBtn = QtWidgets.QPushButton('Perform Search')
    self.searchFormVerticalLayout.addWidget(self.searchBtn)
    # self.searchBtn.clicked.connect(self.search_button_clicked)
    self.searchFormVerticalWidget.setLayout(self.searchFormVerticalLayout)

    # Create our results side?
    self.resultsFormVerticalWidget = QtWidgets.QWidget(self.app.searchTab)
    self.resultsFormVerticalLayout = QtWidgets.QVBoxLayout(self.resultsFormVerticalWidget)
    self.resultsFormVerticalLayout.addWidget(self.create_results_view())

    # Wrap this within our left-side tab interface for swapping between results, and the search form
    self.leftSideWidget =  QtWidgets.QTabWidget(self.app.searchTab)
    self.leftSideWidget.setTabPosition(2)
    self.leftSideWidget.addTab(self.searchFormVerticalWidget, 'Search Form')
    self.leftSideWidget.addTab(self.resultsFormVerticalWidget, 'Results')
    # self.leftSideWidget.setTabEnabled(1, False)

    # Signal for performing a search
    self.searchBtn.clicked.connect(self.app.searchHandler.perform_search)

    return self.leftSideWidget

  def generate_on_this_day(self):
    """
    Generates a default view (shown during start-up), of the performance on this day / months
    in history.
    """

    q = """
        PREFIX etree:<http://etree.linkedmusic.org/vocab/>
        PREFIX mo:<http://purl.org/ontology/mo/>
        PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
        PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX calma: <http://calma.linkedmusic.org/vocab/>

        SELECT DISTINCT ?label ?name ?place ?location ?date (group_concat(distinct ?calma; separator = "\\n") AS ?calma) WHERE {{

         ?art skos:prefLabel ?label.
         ?art mo:performer ?performer. 
         ?art etree:description ?description.
         ?performer foaf:name ?name.
         ?art event:place ?location.
         ?art etree:date ?date.
         ?location etree:location ?place.
         ?art event:hasSubEvent ?subEvent
         OPTIONAL {{?performer etree:mbTag ?genre}}.
         OPTIONAL {{?subEvent calma:data ?calma}}.

         FILTER (regex(?date,'{0}', 'i'))

        }}
        ORDER BY ?name
        LIMIT 25
    """.format(time.strftime('-%m-%d'))
    results = self.app.sparql.execute_string(q)

    self.app.searchHandler.setup_views(['map', 'table', 'timeline', 'today in history'], results)
    self.app.searchHandler.lastQueryExecuted = q

  def generate_right_side(self):
    """
    Generates the right side of the search form (data views).
    """

    self.rightSideWidget = QtWidgets.QWidget(self.app.searchTab)
    self.rightSideLayout = QtWidgets.QVBoxLayout()

    return self.rightSideWidget

  def generate_search_tab(self):
    self.searchFormTabs = QtWidgets.QTabWidget()
    self.searchFormTabs.addTab(self.generate_search_form_general(), 'General')
    self.searchFormTabs.addTab(self.generate_search_form_geography(), 'Geography')
    self.searchFormTabs.addTab(self.generate_search_form_advanced(), 'Advanced')
    self.searchFormTabs.addTab(self.generate_search_form_views(), 'Views')

    return self.searchFormTabs

  def generate_search_form_general(self):
    # Create layout and widget to place contents in
    self.searchGeneralLayout = QtWidgets.QGridLayout()
    self.searchGeneralWidget = QtWidgets.QWidget(self.app.searchTab)

    # Artist field
    self.artistFilterLbl = QtWidgets.QLabel('Artist')
    self.artistFilter = QtWidgets.QLineEdit()
    self.searchGeneralLayout.addWidget(self.artistFilterLbl, 0, 1, 1, 1)
    self.searchGeneralLayout.addWidget(self.artistFilter, 0, 3, 1, 1)

    # Genre field
    self.genreFilterLbl = QtWidgets.QLabel('Genre')
    self.genreFilter = QtWidgets.QLineEdit()
    self.searchGeneralLayout.addWidget(self.genreFilterLbl, 1, 1, 1, 1)
    self.searchGeneralLayout.addWidget(self.genreFilter, 1, 3, 1, 1)

    # Track name field
    self.trackNameLbl = QtWidgets.QLabel('Track Name')
    self.trackNameFilter = QtWidgets.QLineEdit()
    self.searchGeneralLayout.addWidget(self.trackNameLbl, 2, 1, 1, 1)
    self.searchGeneralLayout.addWidget(self.trackNameFilter, 2, 3, 1, 1)

    # Start date field
    self.dateFromLbl = QtWidgets.QLabel('From Date')
    self.dateFrom = QtWidgets.QDateEdit()
    self.dateFrom.setDisplayFormat('dd-MM-yyyy')
    self.dateFrom.setDateTime(QtCore.QDateTime(QtCore.QDate(1950, 1, 1), QtCore.QTime(0, 0, 0)))
    self.dateFrom.setMaximumDate(QtCore.QDate(2016, 1, 1))
    self.searchGeneralLayout.addWidget(self.dateFromLbl, 3, 1, 1, 1)
    self.searchGeneralLayout.addWidget(self.dateFrom, 3, 3, 1, 1)

    # End date field
    self.dateToLbl = QtWidgets.QLabel('To Date')
    self.dateTo = QtWidgets.QDateEdit()
    self.dateTo.setDisplayFormat('dd-MM-yyyy')
    self.dateTo.setDateTime(QtCore.QDateTime(QtCore.QDate(2017, 1, 1), QtCore.QTime(0, 0, 0)))
    self.dateTo.setMaximumDate(QtCore.QDate(2017, 1, 1))
    self.searchGeneralLayout.addWidget(self.dateToLbl, 4, 1, 1, 1)
    self.searchGeneralLayout.addWidget(self.dateTo, 4, 3, 1, 1)

    # # Order-by field
    self.orderByLbl = QtWidgets.QLabel('Order By')
    self.orderByFilter = QtWidgets.QComboBox()
    self.orderByFilter.addItem('Artist')
    self.orderByFilter.addItem('Date')
    self.orderByFilter.addItem('Genre')
    self.orderByFilter.addItem('Label')
    self.orderByFilter.addItem('Location')
    self.searchGeneralLayout.addWidget(self.orderByLbl, 5, 1, 1, 1)
    self.searchGeneralLayout.addWidget(self.orderByFilter, 5, 3, 1, 1)

    # Num results field
    self.numResultsLbl = QtWidgets.QLabel('No. Results')
    self.numResultsSpinbox = QtWidgets.QSpinBox()
    self.numResultsSpinbox.setMaximum(10000)
    self.numResultsSpinbox.setProperty("value", 500)
    self.searchGeneralLayout.addWidget(self.numResultsLbl, 6, 1, 1, 1)
    self.searchGeneralLayout.addWidget(self.numResultsSpinbox, 6, 3, 1, 1)

    # CALMA-available only field
    self.hasCalmaLbl = QtWidgets.QLabel('Has CALMA')
    self.hasCalmaCheck = QtWidgets.QCheckBox()
    self.searchGeneralLayout.addWidget(self.hasCalmaLbl, 7, 1, 1, 1)
    self.searchGeneralLayout.addWidget(self.hasCalmaCheck, 7, 3, 1, 1)

    # Set layout to widget
    self.searchGeneralWidget.setLayout(self.searchGeneralLayout)

    # Return widget
    return self.searchGeneralWidget

  def generate_search_form_geography(self):
    # Create layout and widget to place contents in
    self.searchGeographyLayout = QtWidgets.QGridLayout()
    self.searchGeographyWidget = QtWidgets.QWidget()

    # Venue field
    self.venueFilterLbl = QtWidgets.QLabel('Venue')
    self.venueFilter = QtWidgets.QLineEdit()
    self.searchGeographyLayout.addWidget(self.venueFilterLbl, 0, 1, 1, 1)
    self.searchGeographyLayout.addWidget(self.venueFilter, 0, 3, 1, 1)

    # Location field
    self.locationFilterLbl = QtWidgets.QLabel('Location')
    self.locationFilter = QtWidgets.QLineEdit()
    self.searchGeographyLayout.addWidget(self.locationFilterLbl, 1, 1, 1, 1)
    self.searchGeographyLayout.addWidget(self.locationFilter, 1, 3, 1, 1)

    # Range field
    self.locationRangeFilterLbl = QtWidgets.QLabel('Range (KM)')
    self.locationRangeFilter = QtWidgets.QLineEdit()
    self.searchGeographyLayout.addWidget(self.locationRangeFilterLbl, 2, 1, 1, 1)
    self.searchGeographyLayout.addWidget(self.locationRangeFilter, 2, 3, 1, 1)

    # Country field
    self.countryFilterLbl = QtWidgets.QLabel('Country')
    self.countryFilter = QtWidgets.QLineEdit()
    self.searchGeographyLayout.addWidget(self.countryFilterLbl, 3, 1, 1, 1)
    self.searchGeographyLayout.addWidget(self.countryFilter, 3, 3, 1, 1)

    # Set layout to widget
    self.searchGeographyWidget.setLayout(self.searchGeographyLayout)

    # Return widget
    return self.searchGeographyWidget

  def generate_search_form_views(self):
    # Create layout and widget to place contents in
    self.searchViewsLayout = QtWidgets.QGridLayout()
    self.searchViewsWidget = QtWidgets.QWidget()

    # Create check-boxes
    self.mapViewChk = QtWidgets.QCheckBox()
    self.mapViewChk.setText('Map')
    self.tableViewChk = QtWidgets.QCheckBox()
    self.tableViewChk.setText('Table')
    self.timelineViewChk = QtWidgets.QCheckBox()
    self.timelineViewChk.setText('Feature Analyses')

    # Set all to checked by default
    self.mapViewChk.setChecked(True)
    self.tableViewChk.setChecked(True)
    self.timelineViewChk.setChecked(True)

    # Add widgets to layout
    # self.searchViewsLayout.addWidget(self.tableViewChk, 1, 1, 1, 1)
    self.searchViewsLayout.addWidget(self.mapViewChk, 3, 1, 1, 1)
    self.searchViewsLayout.addWidget(self.timelineViewChk, 5, 1, 1, 1)

    # Set layout to widget
    self.searchViewsWidget.setLayout(self.searchViewsLayout)

    # Return widget
    return self.searchViewsWidget

  def generate_search_form_advanced(self):
    # Create layout and widget to place contents in
    self.searchAdvancedLayout = QtWidgets.QVBoxLayout()
    self.searchAdvancedWidget = QtWidgets.QWidget()

    # Buttons and labels for adding / removing conditions
    self.advancedConditionLbl = QtWidgets.QLabel('Match')
    self.matchingPolicyCombo = QtWidgets.QComboBox()
    self.matchingPolicyCombo.addItem("ALL")
    self.matchingPolicyCombo.addItem("OR")
    self.addConditionBtn = QtWidgets.QPushButton('+')
    self.removeConditionBtn = QtWidgets.QPushButton('-')
    self.searchAdvancedControlsLayout = QtWidgets.QHBoxLayout()
    self.searchAdvancedControlsLayout.addWidget(self.advancedConditionLbl)
    self.searchAdvancedControlsLayout.addWidget(self.matchingPolicyCombo)
    self.searchAdvancedControlsLayout.addWidget(self.addConditionBtn)
    self.searchAdvancedControlsLayout.addWidget(self.removeConditionBtn)
    self.searchAdvancedControlsWidget = QtWidgets.QWidget()
    self.searchAdvancedControlsWidget.setLayout(self.searchAdvancedControlsLayout)

    # Layout for adding conditions to
    self.advancedSearchLayout = QtWidgets.QGridLayout()
    self.advancedSearchWidget = QtWidgets.QWidget()
    self.advancedSearchWidget.setLayout(self.advancedSearchLayout)

    # Add both widgets to upper layout
    self.searchAdvancedLayout.addWidget(self.searchAdvancedControlsWidget)
    self.searchAdvancedLayout.addWidget(self.advancedSearchWidget)
    self.searchAdvancedLayout.setStretch(0, 1)
    self.searchAdvancedLayout.setStretch(1, 20)

    # Add signals for communication
    self.addConditionBtn.pressed.connect(self.app.searchHandler.add_custom_condition)
    self.removeConditionBtn.pressed.connect(self.app.searchHandler.remove_custom_condition)

    # Set layout to widget
    self.searchAdvancedWidget.setLayout(self.searchAdvancedLayout)

    # Return widget
    return self.searchAdvancedWidget

  def change_proportions(self):
    # Account for possibility of default form (with an additional element at the top)
    if self.app.searchHandler.view.viewLayout.count() == 4:
      offset = 1
    else:
      offset = 0

    if (self.infoWindowWidgets['tableSpan'].value() > 0):
      self.topLevelSearchLayout.itemAt(1).widget().layout().setStretch(0+offset, int(self.infoWindowWidgets['tableSpan'].value()))
    # Timeline slider
    if (self.infoWindowWidgets['timelineSpan'].value() > 0):
      self.topLevelSearchLayout.itemAt(1).widget().layout().setStretch(2+offset, int(self.infoWindowWidgets['timelineSpan'].value()))
    # Map slider
    if (self.infoWindowWidgets['mapSpan'].value() > 0):
      self.topLevelSearchLayout.itemAt(1).widget().layout().setStretch(1+offset, int(self.infoWindowWidgets['mapSpan'].value()))

  def feature_calma_changed(self, index):
    if len(self.tracklistView.selectedIndexes()) > 0:
      self.app.searchHandler.view.graph_calma(self.tracklistView.selectedIndexes()[0])

  def create_results_view(self):
    """
    Creates a properties window for a data view.

    Parameters
    ----------
    self : instance
        Class instance.
    """

    # Create layouts for each tab
    layoutTabLayout = QtWidgets.QGridLayout()
    searchTabLayout = QtWidgets.QGridLayout()

    self.infoWindowWidgets = {}

    # Add sliders for adjusting the layout
    layoutTabLayout.addWidget(QtWidgets.QLabel('Table Span'), 1, 0)
    self.infoWindowWidgets['tableSpan'] = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    self.infoWindowWidgets['tableSpan'].setMaximum(10)
    self.infoWindowWidgets['tableSpan'].setValue(2)
    self.infoWindowWidgets['tableSpan'].setSingleStep(1)
    layoutTabLayout.addWidget(self.infoWindowWidgets['tableSpan'], 1, 1)

    layoutTabLayout.addWidget(QtWidgets.QLabel('Map Span'), 2, 0)
    self.infoWindowWidgets['mapSpan'] = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    self.infoWindowWidgets['mapSpan'].setMaximum(10)
    self.infoWindowWidgets['mapSpan'].setValue(6)
    self.infoWindowWidgets['mapSpan'].setSingleStep(1)
    layoutTabLayout.addWidget(self.infoWindowWidgets['mapSpan'], 2, 1)

    layoutTabLayout.addWidget(QtWidgets.QLabel('Timeline Span'), 3, 0)
    self.infoWindowWidgets['timelineSpan'] = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    self.infoWindowWidgets['timelineSpan'].setMaximum(10)
    self.infoWindowWidgets['timelineSpan'].setValue(2)
    self.infoWindowWidgets['timelineSpan'].setSingleStep(1)
    layoutTabLayout.addWidget(self.infoWindowWidgets['timelineSpan'], 3, 1)

    self.infoWindowWidgets['tableSpan'].sliderMoved.connect(lambda: self.change_proportions())
    self.infoWindowWidgets['mapSpan'].sliderMoved.connect(lambda: self.change_proportions())
    self.infoWindowWidgets['timelineSpan'].sliderMoved.connect(lambda: self.change_proportions())

    # Add search button
    self.infoWindowWidgets['searchButton'] = QtWidgets.QPushButton('Search')
    self.infoWindowWidgets['searchBox'] = QtWidgets.QLineEdit()
    searchTabLayout.addWidget(self.infoWindowWidgets['searchBox'], 1, 0)
    searchTabLayout.addWidget(self.infoWindowWidgets['searchButton'], 1, 1)
    searchTabLayout.addWidget(QtWidgets.QWidget(), 1, 2)
    searchTabLayout.setRowStretch(0, 1)
    searchTabLayout.setRowStretch(1, 12)
    searchTabLayout.setRowStretch(2, 12)

    # Add save tab
    saveTabLayout = QtWidgets.QGridLayout()
    self.infoWindowWidgets['saveButton'] = QtWidgets.QPushButton('Save Search')
    self.infoWindowWidgets['saveEdit'] = QtWidgets.QLineEdit()
    self.infoWindowWidgets['savePlotButton'] = QtWidgets.QPushButton('Save CALMA Plot')
    saveTabLayout.addWidget(self.infoWindowWidgets['saveEdit'], 0, 0)
    saveTabLayout.addWidget(self.infoWindowWidgets['saveButton'], 0, 1)
    saveTabLayout.addWidget(self.infoWindowWidgets['savePlotButton'], 2, 0)
    saveTabLayout.addWidget(QtWidgets.QWidget(), 3, 2)
    # saveTabLayout.setRowStretch(0, 1)
    # saveTabLayout.setRowStretch(1, 12)
    # saveTabLayout.setRowStretch(3, 12)

    # Create tracklist label for properties sub-window
    self.infoWindowWidgets['tracklistLabel'] = QtWidgets.QLabel("Tracklist:")

    # Add toggle for swapping between segmentation and key info for properties sub-window
    self.infoWindowWidgets['toggleKeysSegments'] = QtWidgets.QComboBox()
    self.infoWindowWidgets['toggleKeysSegments'].addItem('Key Changes')
    self.infoWindowWidgets['toggleKeysSegments'].addItem('Segmentation')
    self.infoWindowWidgets['toggleKeysSegments'].currentIndexChanged.connect(self.feature_calma_changed)

    # Create individual tabs
    self.tabWidget = QtWidgets.QTabWidget()
    self.layoutTab = QtWidgets.QTabWidget()
    self.searchTab = QtWidgets.QTabWidget()
    self.saveTab = QtWidgets.QTabWidget()
    self.propertiesTab = QtWidgets.QTabWidget()

    # Add tracklist tab components
    self.tracklistView = QtWidgets.QListWidget(self.propertiesTab)
    self.tracklistLayout = QtWidgets.QVBoxLayout(self.propertiesTab)
    self.tracklistLayout.addWidget(self.infoWindowWidgets['tracklistLabel'])
    self.tracklistLayout.addWidget(self.infoWindowWidgets['toggleKeysSegments'])
    self.tracklistLayout.addWidget(self.tracklistView)
    self.tracklistWidget = QtWidgets.QWidget()
    self.tracklistWidget.setLayout(self.tracklistLayout)

    # Create properties tab layout
    self.propertiesTreeView = application.TreePropertiesView(self.app) # QtWidgets.QTreeView(self.propertiesTab)
    self.propertiesTabLayout = QtWidgets.QVBoxLayout(self.propertiesTab)
    self.propertiesTabLayout.addWidget(self.propertiesTreeView)
    self.propertiesTabLayout.addWidget(self.tracklistWidget)
    self.propertiesTab.setLayout(self.propertiesTabLayout)
    self.propertiesTreeView.header().hide()

    # Set tab layouts
    self.layoutTab.setLayout(layoutTabLayout)
    self.searchTab.setLayout(searchTabLayout)
    self.saveTab.setLayout(saveTabLayout)

    # Finally, add tabs to the tab widget
    self.tabWidget.addTab(self.propertiesTab, 'Properties')
    self.tabWidget.addTab(self.searchTab, 'Filter')
    self.tabWidget.addTab(self.layoutTab, 'Layout')
    self.tabWidget.addTab(self.saveTab, 'Save')

    # Add tooltips
    # self.add_tooltips()

    return self.tabWidget

class SearchHandler():
  def __init__(self, main):
    self.main = main

  def load_saved_search(self, index):
    for s in reversed(self.main.savedSearches):
      if index.data() == s[0]:
        self.setup_views(['timeline', 'map', 'table'], self.main.sparql.execute_string(s[1]))
        self.main.topMenuTabs.setCurrentIndex(2)
        return

  def add_custom_condition(self):
    # Each custom condition consists of groups of 3 widgets
    if self.main.searchForm.advancedSearchLayout.count() == 0:
      count = 0
    else:
      count = self.main.searchForm.advancedSearchLayout.count() / 3

    # Add to appropriate indexes our new row of widgets
    self.main.searchForm.advancedSearchLayout.addWidget(self.generate_field_combo(), count + 1, 1, 1, 2)
    self.main.searchForm.advancedSearchLayout.addWidget(self.generate_condition_combo(), count + 1, 2, 1, 3)
    self.main.searchForm.advancedSearchLayout.addWidget(QtWidgets.QLineEdit(), count + 1, 4, 1, 2)

    # Add auto-completion where appropriate
    self.update_auto_complete()

  def remove_custom_condition(self):
    if self.main.searchForm.advancedSearchLayout.count() > 0:
      # Get 3 last items in the layout and remove them
      self.main.searchForm.advancedSearchLayout.itemAt(self.main.searchForm.advancedSearchLayout.count() - 1).widget().setParent(None)
      self.main.searchForm.advancedSearchLayout.itemAt(self.main.searchForm.advancedSearchLayout.count() - 1).widget().setParent(None)
      self.main.searchForm.advancedSearchLayout.itemAt(self.main.searchForm.advancedSearchLayout.count() - 1).widget().setParent(None)

  def generate_field_combo(self):
    items = ['Artist', 'Genre', 'Label', 'Location', 'Venue', 'Date']
    comboBox = QtWidgets.QComboBox()
    comboBox.addItems(items)
    comboBox.currentIndexChanged.connect(self.update_auto_complete)

    return comboBox

  def update_auto_complete(self):
    """
    Generates auto-complete instances for advanced search conditions.
    """

    for i in range(0, self.main.searchForm.advancedSearchLayout.count(), 3):
      self.main.searchForm.advancedSearchLayout.itemAt(i + 2).widget().setCompleter(None)
      widgetText = self.main.searchForm.advancedSearchLayout.itemAt(i).widget().currentText()
      textEditWidget = self.main.searchForm.advancedSearchLayout.itemAt(i + 2).widget()

      if widgetText == 'Artist':
        textEditWidget.setCompleter(self.main.auto_comp(self.main.cache.load('artistList')))
      elif widgetText == 'Location':
        textEditWidget.setCompleter(self.main.auto_comp(self.main.cache.load('newReversedGroupedLocations')))
      elif widgetText == 'Genre':
        textEditWidget.setCompleter(self.main.auto_comp(self.main.cache.load('genreList')))

  def generate_condition_combo(self):
    items = ['is', 'is not', 'starts with', 'ends with', 'contains', 'does not contain', 'matches RegEx', 'does not match RegEx']
    comboBox = QtWidgets.QComboBox()
    comboBox.addItems(items)
    return comboBox

  def generate_advanced_search(self, field, operator, condition):
    field_to_sparql = {'Artist' : '?name', 'Label' : '?prefLabel', 'Location' : '?place', 'Venue' : '?venue',
                       'Date' : '?date', 'Genre' : '?genre'}

    filterString = ''
    if operator == 'is':
      # Check for genre
      if field_to_sparql == 'Genre':
        filterString = """FILTER({0}="{1}") """.format(field_to_sparql[field], condition.lower())
      else:
        filterString = """FILTER({0}="{1}") """.format(field_to_sparql[field], condition)
    elif operator == 'is not':
      if field_to_sparql == 'Genre':
        filterString = """FILTER({0}!="{1}") """.format(field_to_sparql[field], condition.lower())
      else:
        filterString = """FILTER({0}!="{1}") """.format(field_to_sparql[field], condition)
    elif operator == 'starts with':
      filterString = """FILTER(STRSTARTS({0},"{1}")) """.format(field_to_sparql[field], condition)
    elif operator == 'ends with':
      filterString = """FILTER(STRENDS({0},"{1}")) """.format(field_to_sparql[field], condition)
    elif operator == 'contains':
      filterString = """FILTER(CONTAINS({0},"{1}")) """.format(field_to_sparql[field], condition)
    elif operator == 'does not contain':
      filterString = """FILTER(!CONTAINS({0},"{1}") """.format(field_to_sparql[field], condition)
    elif operator == 'matches RegEx':
      filterString = """FILTER(regex({0}, "{1}", "i")) """.format(field_to_sparql[field], condition)
    elif operator == 'does not match RegEx':
      filterString = """FILTER(!regex({0}, "{1}", "i")) """.format(field_to_sparql[field], condition)
    else:
      raise('No matching operator')

    return filterString

  def custom_search(self):
    """
    Generates search filter queries for advanced queries from the interface.
    """

    # Get type for these conditions
    customConditions = []
    for i in range(0, self.main.searchForm.advancedSearchLayout.count(), 3):
      if len(self.main.searchForm.advancedSearchLayout.itemAt(i + 2).widget().text()) > 0:
        customConditions.append(self.generate_advanced_search(self.main.searchForm.advancedSearchLayout.itemAt(i).widget().currentText(),
                                                              self.main.searchForm.advancedSearchLayout.itemAt(i + 1).widget().currentText(),
                                                              self.main.searchForm.advancedSearchLayout.itemAt(i + 2).widget().text()))

    if 'OR' in self.main.searchForm.matchingPolicyCombo.currentText():
      customConditions = self.change_condition_or(customConditions)
    else:
      customConditions = self.ensure_matching_parentheses(customConditions)

    return customConditions

  def change_condition_or(self, customConditions):
    """
    Adjusts a search FILTER from "ALL" or "OR".

    Parameters
    ----------
    customConditions : str[]
        A list of custom conditions returned by the class instance.
    """

    for index, item in enumerate(customConditions):
      if index == 0:
        newStr = item[:item.rfind(')')]
        newStr += " ||"
        customConditions[index] = newStr
      if index > 0:
        newStr = item.replace('FILTER(', '')
        newStr = newStr[:-1]
        newStr += " ||"
        customConditions[index] = newStr
      if index == len(customConditions) - 1:
        newStr = customConditions[index].replace("||", "")
        customConditions[index] = newStr

    return customConditions

  def ensure_matching_parentheses(self, customConditions):
    """
    Performs validation on SPARQL filter queries to ensure that our query is valid.

    Parameters
    ----------
    customConditions : str[]
        A list of custom conditions returned by the class instance.
    """

    for index, item in enumerate(customConditions):
      left = item.count('(')
      right = item.count(')')

      while right < left:
        item += ')'
        right += 1
      customConditions[index] = item

    return customConditions

  def generate_mapped_locations(self):
    """
    A user may request all performances within a specified radius of a given location.

    We calculate the desired locations using point-to-point distance calculations, relative
    to the location map keys.

    Parameters
    ----------
    countries : str[]
        A list of performance countries.
    """

    # If user requested a range
    if len(self.main.searchForm.locationRangeFilter.text()) > 0 and len(self.main.searchForm.locationFilter.text()) > 0:
      locations = []

      # If p-to-p distance is within our range
      words = self.main.browseListHandler.locationList[self.main.searchForm.locationFilter.text()]['latlng'].split()
      centerLat = radians(float(words[0]))
      centerLon = radians(float(words[1]))
      radius = 6373.0
      filter = ''

      # Find all locations within the range specified by the user
      for key, value in sorted(self.main.browseListHandler.locationList.items()):
        a, c, distance = None, None, None

        keyLat, keyLon = value['latlng'].split(' ')

        # Convert to floats from strings, then convert to radians
        keyLat = radians(float(keyLat))
        keyLon = radians(float(keyLon))

        # Calculate delta between pairs of lat / lngs
        deltaLongitude = keyLon - centerLon
        deltaLatitude = keyLat - centerLat

        # Perform point-to-point distance calculation
        a = sin(deltaLatitude / 2) ** 2 + cos(centerLat) * cos(keyLat) * sin(deltaLongitude / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        # a = sin(deltaLat / 2) ** 2 + cos(centerLat) * cos(centerLon) * sin(deltaLon / 2) ** 2
        # # try:
        # c = 2 * atan2(sqrt(a), sqrt(1 - a)) # This line causes an error

        distance = radius * c

        # If location is within our distance radius
        if distance < float(self.main.searchForm.locationRangeFilter.text()):
          self.main.debugDialog.add_line("{0}: {1}".format(sys._getframe().f_code.co_name, str(key)
                                                           + ' by a distance of ' + str(float(self.main.searchForm.locationRangeFilter.text()) -
                                                                                        distance)))

          # Append all mapped locations for this key to our requested locations
          for location in value['locations']:
            locations.append(location)

      return locations
    # If only 1 location requested
    elif len(self.main.searchForm.locationFilter.text()) > 0:
      # Return all mapped locations
      return self.main.browseListHandler.locationList[self.main.searchForm.locationFilter.text()]['locations']
    else:
      return None

  def get_mapped_countries(self, countries):
    """
    Retrieves locations in a requested country.

    Parameters
    ----------
    countries : str[]
        A list of performance countries.
    """

    countries = countries.split(',')
    correspondingLocations = []

    for country in countries:
      for key in self.main.browseListHandler.locationList.keys():
        if country.lower() in key.lower():
          correspondingLocations.append(x for x in self.main.browseListHandler.locationList[key]['locations'])

    # Turn into a flat list of locations
    correspondingLocations = [item for sublist in correspondingLocations for item in sublist]

    return correspondingLocations


  def perform_search(self):
    # Get contents of text boxes
    locations = self.generate_mapped_locations()
    artists = self.main.searchForm.artistFilter.text()
    genres = self.main.searchForm.genreFilter.text().lower()
    orderBy = self.main.searchForm.orderByFilter.currentText()
    limit = self.main.searchForm.numResultsSpinbox.value()
    venue = self.main.searchForm.venueFilter.text()
    trackName = self.main.searchForm.trackNameFilter.text()
    onlyCalma = self.main.searchForm.hasCalmaCheck.isChecked()

    if len(self.main.searchForm.countryFilter.text()) > 0:
      countries = self.get_mapped_countries(self.main.searchForm.countryFilter.text())
    else:
      countries = ''

    # Custom search conditions
    if self.main.searchForm.advancedSearchLayout.count() > 0:
      customSearchString = self.custom_search()
    else:
      customSearchString = ''

    # Generate SPARQL query
    query = self.main.sparql.perform_search(self.main.searchForm.dateFrom.text(), self.main.searchForm.dateTo.text(), artists, genres, locations, limit, trackName,
                                            countries, customSearchString, venue, orderBy, onlyCalma)

    self.lastQueryExecuted = query

    # Execute SPARQL query
    results = self.main.sparql.execute_string(query)
    # Collect requested views
    requestedViews = []
    requestedViews.append('table')
    if self.main.searchForm.mapViewChk.isChecked() : requestedViews.append('map')
    if self.main.searchForm.timelineViewChk.isChecked() : requestedViews.append('timeline')
    # if self.main.searchForm.tableViewChk.isChecked() : requestedViews.append('table')

    # Create views
    self.setup_views(requestedViews, results)

    # Reset fields
    self.reset_search_form()

  def reset_search_form(self):
    self.main.searchForm.artistFilter.setText("")
    self.main.searchForm.genreFilter.setText("")
    self.main.searchForm.trackNameFilter.setText("")
    self.main.searchForm.dateFrom.setDate(QtCore.QDate(1950, 1, 1))
    self.main.searchForm.dateTo.setDate(QtCore.QDate(2017, 1, 1))
    self.main.searchForm.venueFilter.setText("")
    self.main.searchForm.locationFilter.setText("")
    self.main.searchForm.locationRangeFilter.setText("")
    self.main.searchForm.countryFilter.setText("")

  def setup_views(self, requestedViews, results):
    self.requestedViews = requestedViews
    # Check for availability of CALMA data
    hasCalma = False
    try:
      for result in results['results']['bindings']:
        if len(result['calma']['value']) > 0:
          hasCalma = True
    except Exception as e:
      print(e)
      pass

    # Remove previous views on screen
    toRemove = self.main.searchForm.topLevelSearchLayout.takeAt(1)
    toRemove.widget().deleteLater()

    # Create new view
    self.view = view.View(self.main, self, requestedViews, results, hasCalma)

    # Add new view to layout
    self.main.searchForm.topLevelSearchLayout.addWidget(self.view.get_widget())

    # Check span is still correct in top level layout
    self.main.searchForm.topLevelSearchLayout.setStretch(0, 2)
    self.main.searchForm.topLevelSearchLayout.setStretch(1, 8)

    # Set results to viewable if not already
    self.main.searchForm.leftSideWidget.setTabEnabled(1, True)
