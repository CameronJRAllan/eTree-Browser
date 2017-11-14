from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os
import application
import multithreading
import calma
import graph

class View():
  """
  This class defines a data view of a SPARQL query search.
  """
  def __init__(self, app, search, views, results, hasCalma, searchLayout):
    """
    Create an instance of the View class.

    The view class defines a series of layout, split into a tabbed list of buttons, and
    a series of data views (a combination of textual, chronological and geographical).

    Parameters
    ----------
    self : instance
        Class instance.
    app : instance
        Reference to the main application module.
    search : instance
        Reference to the searchHandler instance.
    views : str[]
        A list of views requested.
    results : float
        The results of the SPARQL query.
    """

    self.app = app
    self.search = search
    self.calma = calma.Calma()
    self.hasCalma = hasCalma
    self.searchLayout = searchLayout
    # If no results / error occured, log and return
    if isinstance(results, Exception):
      errorDialog = application.ErrorDialog(results)
      return

    # Generate components from user check boxes
    for v in views:
      if v == 'map' : self.generate_map(results)
      if v == 'timeline' : self.generate_plot_view() # generate_timeline(results)
      if v == 'table' : self.generate_table(results)

    # Generate dialog for user
    self.create_layouts(views)
  #
  # def set_left_sidebar(self, layout):
  #   self.infoWidget.setLayout(self.layout())
  #   self.infoWidget.setLayout(layout)

  def get_layout(self):
    try:
      return self.dockedDialog
    except Exception as e:
      return None

  def generate_map(self, results):
    """
    Generates a map view for the SPARQL query results.

    The map dialog utilizes a QWebEngineView, webkit-based, to display an OpenStreetMap
    tiles layer with the data placed on top.

    Parameters
    ----------
    self : instance
        Class instance.
    results : {}
        The results of the SPARQL query.
    """

    # Create web view to execute JavaScript within
    self.mapSearchDialog = QWebEngineView()
    self.searchMapHandler = application.MapHandler(self.app, self.mapSearchDialog)
    self.mapSearchDialog.loadFinished.connect(lambda: self.searchMapHandler.add_search_results_map(results))
    self.mapsPath = os.path.join(os.path.dirname(__file__) + "/maps/map.htm")
    self.mapSearchDialog.setUrl(QtCore.QUrl("file://" + self.app.mapsPath))

    # Initialize web channel for communication between Python + JS
    self.app.initialize_web_channel(self.mapSearchDialog)

  def generate_plot_view(self):
    """
    Starts a new plot of CALMA data.

    This function is typically called after CALMA data has been retrieved
    and a track has been clicked upon.

    Parameters
    ----------
    self : instance
        Class instance.
    """

    self.calmaGraphView = graph.CalmaPlot(600,600,100, self.hasCalma)

  def generate_table(self, results):
    """
    Begins the process of generating a table with the search results.

    Parameters
    ----------
    self : instance
        Class instance.
    results : dict
        Dictionary of search results.
    """

    # Create table of results
    self.tableHandler = application.TableHandler(self.app)
    self.tableHandler.fill_table(results)

  def create_layouts(self, views):
    """
    Creates the layouts for the data view (the overall dialog).

    Parameters
    ----------
    self : instance
        Class instance.
    views : str[]
        List of requested views.
    """

    # Info window (left side)
    self.views = views
    self.propertiesSearchWindow = self.create_search_properties_window()
    self.infoWidget = QtWidgets.QWidget()
    self.infoLayout = QtWidgets.QStackedLayout() # QtWidgets.QBoxLayout(2)
    self.infoLayout.addWidget(self.searchLayout)
    self.infoLayout.addWidget(self.propertiesSearchWindow)
    self.infoWidget.setLayout(self.infoLayout)

    # Docked layout (right side)
    self.viewsWidget = QtWidgets.QWidget()
    self.viewsLayout = QtWidgets.QBoxLayout(2)

    # Create a widget for each requested view
    if 'table' in views:
      self.viewsLayout.addWidget(self.tableHandler.get_table_container())
    if 'map' in views:
      self.viewsLayout.addWidget(self.mapSearchDialog)
    if 'timeline' in views:
      self.viewsLayout.addWidget(self.calmaGraphView) # self.timelineWebView)

    # Set initial spanning between the view components
    if len(views) == 3:
      self.viewsLayout.setStretch(0, 2)
      self.viewsLayout.setStretch(1, 6)
      self.viewsLayout.setStretch(2, 2)
    if len(views) == 2:
      self.viewsLayout.setStretch(0, 5)
      self.viewsLayout.setStretch(1, 5)

    self.viewsWidget.setLayout(self.viewsLayout)

    # Overall top level layout
    self.dockedLayout = QtWidgets.QHBoxLayout()
    self.dockedLayout.addWidget(self.infoWidget)
    self.dockedLayout.addWidget(self.viewsWidget)
    self.dockedDialog = QtWidgets.QWidget()
    self.dockedDialog.setWindowTitle("Data View")
    self.dockedDialog.setMinimumHeight(800)
    self.dockedDialog.setMinimumWidth(1000)
    self.dockedDialog.setLayout(self.dockedLayout)
    self.dockedLayout.setStretch(0, 2)
    self.dockedLayout.setStretch(1, 8)
    # self.dockedDialog.setParent(self.searchLayout)
    # self.dockedDialog.show()
    return self.dockedLayout
  def create_search_properties_window(self):
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
    graphTabLayout = QtWidgets.QGridLayout()

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

    self.infoWindowWidgets['tableSpan'].valueChanged.connect(self.change_proportions)
    self.infoWindowWidgets['mapSpan'].valueChanged.connect(self.change_proportions)
    self.infoWindowWidgets['timelineSpan'].valueChanged.connect(self.change_proportions)

    # Add search button
    self.infoWindowWidgets['searchButton'] = QtWidgets.QPushButton('Search')
    self.infoWindowWidgets['searchBox'] = QtWidgets.QLineEdit()
    searchTabLayout.addWidget(self.infoWindowWidgets['searchBox'], 1, 0)
    searchTabLayout.addWidget(self.infoWindowWidgets['searchButton'], 1, 1)
    self.infoWindowWidgets['searchButton'].clicked.connect(self.search_table)

    # Add tracklist label for properties sub-window
    self.infoWindowWidgets['tracklistLabel'] = QtWidgets.QLabel("Tracklist:")

    # Create individual tabs
    self.tabWidget = QtWidgets.QTabWidget()
    self.layoutTab = QtWidgets.QTabWidget()
    self.searchTab = QtWidgets.QTabWidget()
    self.propertiesTab = QtWidgets.QTabWidget()

    # Add tracklist tab components
    self.tracklistView = QtWidgets.QListWidget(self.propertiesTab)
    self.tracklistView.clicked.connect(self.graph_calma)
    self.tracklistLayout = QtWidgets.QVBoxLayout(self.propertiesTab)
    self.tracklistLayout.addWidget(self.infoWindowWidgets['tracklistLabel'])
    self.tracklistLayout.addWidget(self.tracklistView)
    self.tracklistWidget = QtWidgets.QWidget()
    self.tracklistWidget.setLayout(self.tracklistLayout)

    # Create properties tab layout
    self.propertiesTreeView = QtWidgets.QTreeView(self.propertiesTab)
    self.propertiesTabLayout = QtWidgets.QVBoxLayout(self.propertiesTab)
    self.propertiesTabLayout.addWidget(self.propertiesTreeView)
    self.propertiesTabLayout.addWidget(self.tracklistWidget)
    self.propertiesTab.setLayout(self.propertiesTabLayout)
    self.propertiesTreeView.header().hide()
    self.graphTab = QtWidgets.QTabWidget()

    # Set tab layouts
    self.layoutTab.setLayout(layoutTabLayout)

    self.searchTab.setLayout(searchTabLayout)
    self.graphTab.setLayout(graphTabLayout)

    # Finally, add tabs to the tab widget
    self.tabWidget.addTab(self.propertiesTab, 'Properties')
    self.tabWidget.addTab(self.searchTab, 'Filter')
    self.tabWidget.addTab(self.layoutTab, 'Layout')
    self.tabWidget.addTab(self.graphTab, 'Graph')

    self.goBackToSearchTab = QtWidgets.QTabWidget()
    self.tabWidget.addTab(self.goBackToSearchTab, 'Search -->')
    self.tabWidget.tabBar().setTabTextColor(4, QtCore.Qt.red)
    self.tabWidget.currentChanged.connect(self.change_to_search)

    self.searchVisible = False

    # Add tooltips
    self.add_tooltips()

    return self.tabWidget # self.tabWidget

  def change_to_search(self, index):
    print('Called search func: ' + str(index))
    if index == 4:
      self.infoLayout.setCurrentIndex(0)
      self.tabWidget.setCurrentIndex(0)

  def change_to_results(self, index):
    print('Called results func: ' + str(index))

    if index == 4:
      self.infoLayout.setCurrentIndex(1)
      self.propertiesSearchWindow.setCurrentIndex(0)
  def toggleSearchWindow(self):
    if self.searchVisible:
      self.infoLayout.setCurrentIndex(1)
    else:
      self.infoLayout.setCurrentIndex(0)
    self.searchVisible = not self.searchVisible

  def graph_calma(self, item):
    """
    Retrieves CALMA data and then requests a plot of said data.

    Parameters
    ----------
    self : instance
        Class instance.
    item : QModelIndex
        Index in the tracklist clicked.
    """

    # If no calma instance return
    try:
      # Retrieve CALMA URL for this track in the performance
      calmaURL = self.tracklistCalma[item.data()]

      # Retrieve and set CALMA data
      self.calma.set_new_track_calma(calmaURL)

      # Create a plot of the CALMA data
      self.calmaGraphView.plot_calma_data(self.calma.loudnessValues, self.calma.keyInfo, self.calma.duration)

      # Update the widget geometry, showing the plot to the user
      self.calmaGraphView.updateGeometry()
    except KeyError as e:
      print(e)
      print('Not found')
      return

  def update_properties_tab(self):
    self.propertiesTabModel = QtGui.QStandardItemModel(self.propertiesTreeView)
    properties = self.app.sparql.get_release_properties(self.get_label_current_row())

    if not isinstance(properties, Exception):
      self.app.browseTreeProperties.fill_properties_tree_view(self.propertiesTabModel, properties)
      self.propertiesTreeView.setModel(self.propertiesTabModel)

  def get_label_current_row(self):
    for c in range(0, self.tableHandler.get_table().columnCount()-1):
      try:
        currentRowLabel = self.tableHandler.get_table().item(self.tableHandler.get_table().currentRow(), c).text().lower()

        if 'live at' in currentRowLabel:
          print(self.tableHandler.get_table().item(self.tableHandler.get_table().currentRow(), c))
          return self.tableHandler.get_table().item(self.tableHandler.get_table().currentRow(), c).text()
      except Exception as e:
        print(e)
        return
  def change_proportions(self):
    """
    Adjusts the proportions of dialog given to each individual view.

    This function is called whenever the user moves the sliders in the "Layout" tab, the
    sliders dictate the ratio between the view, e.g. 10:10:10 would give each an equal amount
    of space.

    Parameters
    ----------
    self : instance
        Class instance.
    """

    # Table slider
    if (self.infoWindowWidgets['tableSpan'].value() > 0 ):
      self.viewsLayout.setStretch(0, int(self.infoWindowWidgets['tableSpan'].value()))
    # Timeline slider
    if (self.infoWindowWidgets['timelineSpan'].value() > 0):
      self.viewsLayout.setStretch(2, int(self.infoWindowWidgets['timelineSpan'].value()))
    # Map slider
    if (self.infoWindowWidgets['mapSpan'].value() > 0):
      self.viewsLayout.setStretch(1, int(self.infoWindowWidgets['mapSpan'].value()))

  def move_focus(self, index):
    # If click was from map or timeline
    if isinstance(index, str):
      # Change focus on table
      if 'table' in self.views:
        self.tableHandler.change_focus(index)
      # if 'timeline' in self.views:
      #   self.timelineWebView.page().runJavaScript("""highlightMarker(`{0}`)""".format(index))
      if 'map' in self.views:
        self.mapSearchDialog.page().runJavaScript("""changeMarkerFocus(`{0}`)""".format(index))

    # If click was from table
    elif isinstance(index, QtWidgets.QTableWidgetItem):
      if 'map' in self.views:
        self.mapSearchDialog.page().runJavaScript("""changeMarkerFocus(`{0}`)""".format(index.row()))
      # if 'timeline' in self.views:
      #   self.timelineWebView.page().runJavaScript("""highlightMarker(`{0}`)""".format(index.row()))

    self.update_properties_tab()
    self.update_tracklist()

    return

  def update_tracklist(self):
    """
    Retrieves a tracklist and adds it to the list viewable by the user.

    Parameters
    ----------
    self : instance
        Class instance.
    """
    # Clear previous tracklist
    self.tracklistView.clear()

    # Create dict to store CALMA URLs
    self.tracklistCalma = {}

    # Get label in list
    label = self.get_label_current_row()

    # Retrieve tracklist
    tracklist = self.app.sparql.get_tracklist_grouped(label)

    # Fill CALMA dict, storing the label and track number
    labelNumMapping = {}
    labels = []
    for track in tracklist['results']['bindings']:
      if len(track['calma']['value']) > 0:
        self.tracklistCalma[track['label']['value']] = track['calma']['value']

      # Store relationship between a label and it's track number
      labelNumMapping[track['label']['value']] = float(track['num']['value'])
      labels.append(track['label']['value'])

    # Remove duplicates
    labels = list(set(labels))
    labels.sort(key=lambda x: labelNumMapping[x])

    # Add new tracklist to list widget
    for i in labels:
      self.tracklistView.addItem(i)

  def search_table(self, text):
    """
    Search the table view for a particular item.

    Parameters
    ----------
    self : instance
        Class instance.
    """

    # Search table
    results = self.tableHandler.get_table().findItems(self.infoWindowWidgets['searchBox'].text(), QtCore.Qt.MatchContains)

    # Move view to selected item
    if len(results) > 0:
      self.move_focus(str(results[0].row()))

  def add_tooltips(self):
    self.tracklistView.setToolTip("Displays a track-list for a given performance, click for CALMA data.")