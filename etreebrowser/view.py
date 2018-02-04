from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os
import application
import calma
import graph
import cache
import sys
import datetime
import multithreading
import platform

class View():
  """
  This class defines a data view of a SPARQL query search. This contains all (of a
  subset of) a set containing a map, a graph plot and a table.
  """
  def __init__(self, app, search, views, results, hasCalma):
    """
    Create an instance of the View class.

    The view class defines a series of layout, split into a tabbed list of buttons, and
    a series of data views (a combination of textual, chronological and geographical).

    Parameters
    ----------
    app : instance
        Reference to the main application module.
    search : instance
        Reference to the searchHandler instance.
    views : str[]
        A list of views requested.
    results : float
        The results of the SPARQL query.
    hasCalma : boolean
        Boolean value indicating whether feature analyses are available for this set of results.
    """
    self.app = app
    self.search = search
    self.calma = calma.Calma()
    self.hasCalma = hasCalma
    self.views = views

    # If no results / error occured, log and return
    if isinstance(results, Exception):
      self.errorDialog = application.ErrorDialog(results)
      return

    # Generate components from user check boxes
    for v in views:
      if v == 'map' : self.generate_map(results)
      if v == 'timeline' : self.generate_plot_view()
      if v == 'table' : self.generate_table(results)

    self.viewLayout = QtWidgets.QVBoxLayout()

    # Check seperately to ensure added in 'correct' order
    if 'today in history' in views: self.add_history_label_view()
    if 'table' in views: self.viewLayout.addWidget(self.tableHandler.get_table_container())
    if 'map' in views: self.viewLayout.addWidget(self.mapSearchDialog)
    if 'timeline' in views: self.viewLayout.addWidget(self.calmaGraphView)

    if self.viewLayout.count() == 2:
      self.viewLayout.setStretch(0, 5)
      self.viewLayout.setStretch(1, 5)
    if self.viewLayout.count() == 3:
      self.viewLayout.setStretch(0, 2)
      self.viewLayout.setStretch(1, 6)
      self.viewLayout.setStretch(2, 2)
    if self.viewLayout.count() == 4:
      self.viewLayout.setStretch(0, 1)
      self.viewLayout.setStretch(1, 4)
      self.viewLayout.setStretch(2, 10)
      self.viewLayout.setStretch(3, 4)

    self.viewWidget = QtWidgets.QWidget()
    self.viewWidget.setLayout(self.viewLayout)

    # Setup signals post-view creation
    self.app.searchForm.infoWindowWidgets['searchButton'].clicked.connect(self.search_table)
    self.app.searchForm.infoWindowWidgets['savePlotButton'].clicked.connect(self.save_calma_plot)
    self.app.searchForm.infoWindowWidgets['saveButton'].clicked.connect(self.save_search)
    self.app.searchForm.tracklistView.clicked.connect(self.graph_calma)

  def save_calma_plot(self):
    try:
      path = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Plot Image', '/home')
      if len(path[0]) < 1:
        return
      else:
        self.calmaGraphView.figure.savefig(path[0], bbox_inches='tight')
    except AttributeError as a:
      return

  def add_history_label_view(self):
    # Calculate current day
    today = datetime.date.today()

    # Add to view layout
    font = QtGui.QFont()
    font.setPixelSize(18)
    self.historyLabel = QtWidgets.QLabel("Performances through the years, {0}".format(today.strftime("%A %d %B")))
    self.historyLabel.setFont(font)
    self.viewLayout.addWidget(self.historyLabel)

  def get_widget(self):
    """
    Getter function for the view widget (so that it may be added
    as the right side of the search tab)

    Returns
    ----------
    viewWidget : QWidget
        Widget instance of the view.
    """
    return self.viewWidget

  def generate_map(self, results):
    """
    Generates a map view for the SPARQL query results.

    The map dialog utilizes a QWebEngineView, webkit-based, to display an OpenStreetMap
    tiles layer with the data placed on top.

    Parameters
    ----------
    results : {}
        The results of the SPARQL query.
    """

    # Create web view to execute JavaScript within
    self.mapSearchDialog = QWebEngineView()
    self.searchMapHandler = application.MapHandler(self.app, self.mapSearchDialog)
    self.mapSearchDialog.loadFinished.connect(lambda: self.searchMapHandler.add_search_results_map(results))
    # self.mapsPath = os.path.join(os.path.dirname(__file__) + "/maps/map.htm")
    if platform.system() == 'Windows':
      self.app.mapsPath =  ('file:///' + os.path.join(os.path.dirname(__file__), 'html', 'map.htm').replace('\\', '/'))

    print(self.app.mapsPath)
    self.mapSearchDialog.setUrl(QtCore.QUrl(self.app.mapsPath))

    # Initialize web channel for communication between Python + JS
    self.app.initialize_web_channel(self.mapSearchDialog)


  def generate_plot_view(self):
    """
    Starts a new plot of CALMA data.

    This function is typically called after CALMA data has been retrieved
    and a track has been clicked upon.
    """

    self.calmaGraphView = graph.CalmaPlot(600,600,100, self.hasCalma)
    self.app.debugDialog.add_line('{0}: generated CALMA figure'.format(sys._getframe().f_code.co_name))

  def generate_table(self, results):
    """
    Begins the process of generating a table with the search results.

    Parameters
    ----------
    results : dict
        Dictionary of search results.
    """

    # Create table of results
    self.tableHandler = application.TableHandler(self.app)
    self.tableHandler.fill_table(results)

  def save_search(self):
    """
    Saves a currently displayed search for future loading.
    """

    # Retrieve query which generated this view
    query = self.app.searchHandler.lastQueryExecuted

    # Create list containing desired identifier (from text box), and the query
    subList = [self.app.searchForm.infoWindowWidgets['saveEdit'].text(), query]

    # Append to internal list of saved searches and save to backing store
    self.app.savedSearches.append(subList)
    cache.save(self.app.savedSearches, 'savedSearches')

    # Re-load the history / saved searches table to display our newly saved search
    self.app.initialize_history_table()
    #self.app.debugDialog.add_line('{0}: saved new search under name {1}'.format(sys._getframe().f_code.co_name),
    # self.app.searchForm.infoWindowWidgets['saveEdit'].text())

    return

  def graph_calma(self, item):
    """
    Retrieves CALMA data and then requests a plot of said data.

    Parameters
    ----------
    item : QModelIndex
        Index in the tracklist clicked.
    """

    # Retrieve CALMA URL for this track in the performance
    try:
      calmaURL = self.tracklistCalma[item.data()]
    # If no calma instance return
    except (KeyError, AttributeError) as k:
      return

    # Retrieve and set CALMA data
    # self.calma.set_new_track_calma(calmaURL)
    try:
      self.calma = calma.Calma()
      worker = multithreading.WorkerThread(self.calma.set_new_track_calma, calmaURL)
      worker.qt_signals.finished_set_new_track.connect(self.calma_set_track_callback_signal)
      self.app.threadpool.start(worker)
    except Exception as e:
      pass

    # Update the widget geometry, showing the plot to the user
    self.calmaGraphView.updateGeometry()

  def calma_set_track_callback_signal(self, loudness, keys, segments, duration):
    # Create a plot of the CALMA data
    if self.app.searchForm.infoWindowWidgets['toggleKeysSegments'].currentText() == "Key Changes":
      self.calmaGraphView.plot_calma_data(loudness, keys, duration, "key")
    else:
      self.calmaGraphView.plot_calma_data(loudness, segments, duration, "segment")

    # if self.app.searchForm.infoWindowWidgets['toggleKeysSegments'].currentText() == "Key Changes":
    #   self.calmaGraphView.plot_calma_data(self.calma.loudnessValues, self.calma.keyInfo, self.calma.duration, "key")
    # else:
    #   self.calmaGraphView.plot_calma_data(self.calma.loudnessValues, self.calma.segmentInfo, self.calma.duration, "segment")

  def update_properties_tab(self):
    """
    Updates a set of properties shown to the user.
    """

    # Create model and get release properties to store
    self.propertiesTabModel = QtGui.QStandardItemModel(self.app.searchForm.propertiesTreeView)
    properties = self.app.sparql.get_release_properties(self.get_label_current_row())

    # If properties are of valid type
    if not isinstance(properties, Exception):
      # Load data into model and display in the view
      self.app.searchForm.propertiesTreeView.fill_properties_tree_view(self.propertiesTabModel, properties)
      self.app.searchForm.propertiesTreeView.setModel(self.propertiesTabModel)

  def get_label_current_row(self):
    """
    Retrieve the release name of a clicked row (to allow us to move the focus)

    Returns
    ----------
    label of row : str
      Release name of the row clicked.
    """

    for c in range(0, self.tableHandler.get_table().columnCount()-1):
      try:
        currentRowLabel = self.tableHandler.get_table().item(self.tableHandler.get_table().currentRow(), c).text().lower()

        if 'live at' in currentRowLabel:
          return self.tableHandler.get_table().item(self.tableHandler.get_table().currentRow(), c).text()
      except Exception as e:
        print(e)
        return

  def move_focus(self, index):
    """
    Retrieve the release name of a clicked row (to allow us to move the focus)

    Parameters
    ----------
    index : str / QTableWidgetItem
      Index reference from event fired after user clicks on map or table.
    """

    # If click was from map
    if isinstance(index, str):
      # Change focus on table
      if 'table' in self.views:
        row = self.tableHandler.change_focus(index)
    # If click was from table
    elif isinstance(index, QtWidgets.QTableWidgetItem):
      if 'map' in self.views:
        self.mapSearchDialog.page().runJavaScript("""changeMarkerFocus(`{0}`)""".format(self.tableHandler.resultsTable.item(index.row(), 0).text()))

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
    self.app.searchForm.tracklistView.clear()

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
      self.app.searchForm.tracklistView.addItem(i)

  def search_table(self, text):
    """
    Search the table view for a particular item.

    Parameters
    ----------
    text : string
        The string to be searched for.
    """

    # Search table
    results = self.tableHandler.get_table().findItems(self.app.searchForm.infoWindowWidgets['searchBox'].text(), QtCore.Qt.MatchContains)

    # Move view to selected item
    if len(results) > 0:
      self.move_focus(str(results[0].row()))
      self.move_focus(results[0])

  def add_tooltips(self):
    self.app.searchForm.tracklistView.setToolTip("Displays a track-list for a given performance, click for CALMA data.")