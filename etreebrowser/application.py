#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
  import sys
  sys.path.append("..")
  import time
  import os
  from PyQt5 import QtCore, QtWidgets, QtGui
  from UI import UI
  import sys
  import lastfm
  import maps
  import sparql
  import pyaudio
  import cache
  import multithreading
  import graph
  import audio
  import requests
  import calma
  import export
  import platform
  import qtawesome as qta
  from PyQt5.QtWebChannel import QWebChannel
  from PyQt5.QtWebEngineWidgets import QWebEngineView
  import search
except (ImportError, ModuleNotFoundError) as e:
  print('You are missing package: ' + str(e)[15:])
  print('Quitting ..')
  exit(1)

class mainWindow(UI):
  def __init__(self, dialog):
    UI.__init__(self)
    # UI
    self.setupUi(dialog)
    self.set_tooltips()
    self.topMenuTabs.widget(0).hide()
    self.topMenuTabs.widget(4).hide()

    # Set-up OS specific properties
    self.setup_os_specific_properties()
    self.add_audio_output_devices()

    # Set-up handlers for classes
    self.searchHandler = search.SearchHandler(self)
    self.audioHandler = audio.Audio(self)
    self.sparql = sparql.SPARQL()
    self.exporter = export.Export(self)
    self.lastfmHandler = lastfm.lastfmAPI('c957283a3dc3401e54b309ee2f18645b', 'f555ab4615197d1583eb2532b502c441')
    self.treeViewHandler = BrowseTreeViewHandler(self)
    self.calmaHandler = calma.Calma()
    self.nowPlayingHandler = NowPlaying(self)
    self.browseTreeProperties = TreePropertiesView(self)
    self.browseListHandler = BrowseListHandler(self)
    self.childrenFetched = {}

    # Set-up volume controls
    self.volumeSlider.setValue(50)
    self.volumeSlider.valueChanged.connect(self.audioHandler.set_volume)

    # Set icons for playback
    self.playPauseBtn.setIcon(qta.icon('fa.play'))
    self.prevBtn.setIcon(qta.icon('fa.step-backward'))
    self.nextBtn.setIcon(qta.icon('fa.step-forward'))
    self.lastfmBtn.setIcon(qta.icon('fa.lastfm'))

    # Set-up preferred formats
    self.formats = ['FLAC', 'SHN', 'MP3 (VBR)', 'OGG', 'MP3 (64Kbps)', 'WAV']
    self.formatDict = {'FLAC' : '.flac', 'MP3 (64Kbps)' : '.64.mp3', 'SHN' : '.shn', 'WAV' : '.wav', 'OGG' : '.ogg',
                        'MP3 (VBR)' : 'vbr.mp3'}

    # Set-up multi-threading pools
    self.threadpool = QtCore.QThreadPool()
    self.audioThreadpool = QtCore.QThreadPool()

    self.latlng = cache.load('locationLatLng')

    # self.c = calma.CalmaPlotRelease(self, 'Drive-By Truckers Live at B&A Warehouse on 2004-11-26', 'segmentation')

    # If we already have a session key stored for Last.FM
    if self.lastfmHandler.hasSession() == True:
      # Set button to red to indicate this
      self.lastfmBtn.setStyleSheet("""QPushButton {
                                      background-color: #BA2024;
                                      }""")
      self.lastfmStatus.setText("Log-out of Last.FM")
      self.clickable(self.lastfmStatus).connect(self.lastfm_deauthenticate)
    else:
      # Set text to indicate user to connect to Last.FM
      self.lastfmStatus.setText("Connect to Last.FM")
      self.clickable(self.lastfmStatus).connect(self.check_lastfm_status)

    # Set-up signals for message passing
    self.trackProgress.sliderPressed.connect(self.audioHandler.lock_progress_user_drag)
    self.trackProgress.sliderReleased.connect(self.audioHandler.track_seek)
    self.browseTreeView.clicked.connect(self.treeViewHandler.expand_tree_item)
    self.browseTreeView.doubleClicked.connect(self.treeViewHandler.play_tree_item)
    self.clickable(self.playPauseBtn).connect(self.audioHandler.play_pause)
    self.clickable(self.nextBtn).connect(self.audioHandler.next_click)
    self.clickable(self.prevBtn).connect(self.audioHandler.previous_click)
    self.typeBrowseCombo.currentIndexChanged.connect(self.browseListHandler.change_type)
    self.typeOrderByCombo.currentIndexChanged.connect(self.browseListHandler.change_type_order)
    self.quickFilter.textChanged.connect(self.browseListHandler.quick_filter_update)
    self.treeViewFilter.textChanged.connect(self.treeViewHandler.tree_view_filter_update)
    self.browseList.clicked.connect(self.browseListHandler.browse_link_clicked)
    self.preferredFormatCombo.currentTextChanged.connect(self.preferred_format_changed)
    self.playlist_view.doubleClicked.connect(self.nowplaying_playlist_clicked)
    self.savedSearchesList.doubleClicked.connect(self.searchHandler.load_saved_search)

    # Set-up debug dialog
    self.debugDialog = DebugDialog()
    self.debugChk.stateChanged.connect(self.debug_window_state_changed)

    # Set-up now playing dialog
    self.playlist_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    # Hide header in tree-vew
    self.browseTreeView.header().close()

    # Create menu
    self.browseTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.browseTreeView.customContextMenuRequested.connect(self.open_tree_menu)
    self.browseTreeView.setStyleSheet("QTreeView::item { height: 50px;}")

    # Set our model to the browsing list
    self.browseList.setModel(self.browseListHandler.artistListModel)

    # Create history table, and "most played" lists
    self.initialize_history_table()
    self.initialize_most_played()

    self.searchForm = search.searchForm(self)
    if self.historyonLoadChk.isChecked():
      self.searchForm.generate_on_this_day()

  def setup_os_specific_properties(self):
    # If Windows
    if platform.system() == 'Windows':
      self.mapsPath = ('file:///' + os.path.join(os.path.dirname(__file__), 'html', 'map.htm').replace('\\', '/'))
    # If Linux or Mac
    else:
      self.mapsPath = ('file:///' + os.path.join(os.path.dirname(__file__), 'html', 'map.htm'))

  def add_audio_output_devices(self):
    pyAudio = pyaudio.PyAudio()
    for i in range(0, pyAudio.get_device_count()):
      self.audioOutputCombo.addItem(pyAudio.get_device_info_by_index(i)['name'])
      if pyAudio.get_default_output_device_info()['name'] == pyAudio.get_device_info_by_index(i)['name']:
        self.audioOutputCombo.setCurrentIndex(i)

  def initialize_most_played(self):
    self.mostPlayedReleases = {}
    self.mostPlayedArtists = {}

    # Iterate through the table
    for index in range(0, self.historyTableWidget.rowCount()-1):
      if self.historyTableWidget.item(index, 1).text() in self.mostPlayedArtists.keys():
        self.mostPlayedArtists[self.historyTableWidget.item(index, 1).text()] += 1
      else:
        self.mostPlayedArtists[self.historyTableWidget.item(index, 1).text()] = 1

      if self.historyTableWidget.item(index, 3).text() in self.mostPlayedReleases.keys():
        self.mostPlayedReleases[self.historyTableWidget.item(index, 3).text()] += 1
      else:
        self.mostPlayedReleases[self.historyTableWidget.item(index, 3).text()] = 1

    # Create most played releases
    self.sortedArtists = sorted(self.mostPlayedArtists.keys(), key=lambda x: self.mostPlayedArtists[x], reverse=True)
    for a in self.sortedArtists:
      self.mostPlayedArtistsTbl.addItem("{0} ({1})".format(a, self.mostPlayedArtists[a]))

    # Create most played artists
    self.sortedReleases = sorted(self.mostPlayedReleases.keys(), key=lambda y: self.mostPlayedReleases[y], reverse=True)
    for r in self.sortedReleases:
      self.mostPlayedReleasesTbl.addItem("{0} ({1})".format(r, self.mostPlayedReleases[r]))

  def debug_window_state_changed(self, state):
    """
    Hides or displays the debug window depending on whether the check-box is ticked.

    Parameters
    ----------
    state : int
        Signal from the event fired when user changes the state of the tick-box.
    """
    if state == 2:
      self.debugDialog.show()
    else:
      self.debugDialog.hide()

  def nowplaying_playlist_clicked(self, item):
    self.audioHandler.start_audio_single_link(self.audioHandler.playlist[item.row()][1], 0)

  def initialize_web_channel(self, widget):
    """
    Initializes a communications channel between Python and JavaScript components.

    Parameters
    ----------
    widget : QWidget
        Widget parameter, typically of type QWebEngine.
    """

    # Set-up web channel between python + JS components
    self.mapChannel = QWebChannel()
    self.mapHandler = CallHandler(self)
    self.mapChannel.registerObject('mapHandler', self.mapHandler)
    widget.page().setWebChannel(self.mapChannel)

  def preferred_format_changed(self, item):
    """
    Changes the user's preferred format for audio streaming.

    Parameters
    ----------
    item : int
        Index of the item clicked.
    """

    # Change format to new preferred
    index = self.formats.index(item)
    self.formats[index], self.formats[0] = self.formats[0], self.formats[index]

    # Add line to debug dialog
    self.debugDialog.add_line('{0}: set new preferred format to {1}'.format(sys._getframe().f_code.co_name, self.formats[0]))

  def append_history_table(self, track, artist, label, url):
    """
    Sets up the history table, loading from file store, and adding to
    the table in reverse order.

    Parameters
    ----------
    track : str
        Track name.
    artist : str
        Artist name.
    label : str
        Label (i.e. the performance title).
    url : str
        URL of the track.
    """

    # Append to history table data structure
    self.track_history.append([track, artist, time.strftime('%Y-%m-%d %H:%M:%S'), label, url])

    # Save and reload in the UI
    cache.save(self.track_history, 'play_history')
    self.initialize_history_table()

  def initialize_history_table(self):
    """
    Sets up the history table, loading from file store, and adding to
    the table in reverse order.
    """

    # Clear previous and load data from backing store
    self.savedSearchesList.clear()
    self.savedSearches = cache.load('savedSearches')

    # Add in reverse order
    for item in reversed(self.savedSearches):
      self.savedSearchesList.addItem(item[0])

    # Clear history table
    self.historyTableWidget.clear()
    self.historyTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    # self.historyTableWidget.doubleClicked.connect(self.history_table_clicked)

    # Load from file the previous history
    self.track_history = cache.load('play_history')

    # Set-up properties
    self.historyTableWidget.setColumnCount(4)
    self.historyTableWidget.setRowCount(len(self.track_history))
    self.historyTableWidget.setHorizontalHeaderLabels(['Track', 'Artist', 'Date Played', 'Recording'])
    header = self.historyTableWidget.horizontalHeader()
    header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    header.setStretchLastSection(True)

    # Add data
    rowIndex = 0
    for track_played in reversed(self.track_history):
      columnIndex = 0
      for field in track_played[:-1]:
        # Set item at appropriate indexes
        self.historyTableWidget.setItem(rowIndex, columnIndex, QtWidgets.QTableWidgetItem(str(field)))
        columnIndex += 1
      rowIndex += 1

    # Format history table nicely
    self.historyTableWidget.setVisible(False)
    self.historyTableWidget.resizeColumnsToContents()
    self.historyTableWidget.setSortingEnabled(True)
    self.historyTableWidget.setVisible(True)


  def scrobble_track_lastfm(self):
    """
    Sends an API request to Last.FM to record playback of a given track.
    """
    try:
      artist = self.sparql.get_artist_from_tracklist(self.audioHandler.playlist[self.audioHandler.playlist_index][2])
      self.lastfmHandler.update_now_playing(artist, self.audioHandler.playlist[self.audioHandler.playlist_index][1])
    except Exception as e:
      print(e)
      return

  def auto_comp(self, inputList):
    """
    Creates and returns an auto-completer with the input list.

    Parameters
    ----------
    inputList : str[]
        The input list providing the model for the auto-completer.
    """

    # If the inputList is a dict
    if type(inputList) is type(dict()):

      # Convert to list first
      tempList = []
      for key in inputList.keys():
        tempList.append(key)
      inputList = tempList

    # Create qCompleter instance with input list
    lineEditCompleter = QtWidgets.QCompleter(inputList)
    lineEditCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

    # Return to be set to the relevant GUI text-box
    return lineEditCompleter

  def set_tooltips(self):
    """
    Sets up help tooltips which appear when the user hovers over a particular widget.
    """

    self.repeatCombo.setToolTip("Playback behaviour for after a track finishes")
    self.nextBtn.setToolTip("Skip to the next track")
    self.prevBtn.setToolTip("Skip to the previous track")
    self.playPauseBtn.setToolTip("Play or pause the current track")
    self.lastfmBtn.setToolTip("View Last.FM status")

    self.timeLbl.setToolTip("The current position in the track")
    self.trackLbl.setToolTip("Currently playing track name")
    self.trackProgress.setToolTip("Press to seek to a specific time")

    self.volumeLbl.setToolTip("Change the volume of the music playing")
    self.volumeSlider.setToolTip("Slide to adjust volume")

    self.nowPlayingTab.setToolTip("Provides information about the release currently being played")
    self.browseTab.setToolTip("Browse the meta-data")

  def open_tree_menu(self, pos):
    """
    Called when the user requests a context menu from the tree view.

    Parameters
    ----------
    pos : QPoint
        Relative geometric position in the widget.
    """
    self.menu_on_item = pos
    indexes = self.browseTreeView.selectedIndexes()

    # Calculate number of levels
    if len(indexes) > 0:
      level = 0
      index = indexes[0]
      while index.parent().isValid():
        index = index.parent()
        level += 1

      # Create menu
      self.menu = QtWidgets.QMenu()
      exportFormatMenu = QtWidgets.QMenu("Export Data")
      self.menu.triggered.connect(self.tree_browse_menu_click)

      # If performance
      if level == 0:
        self.menu.addAction(QtCore.QT_TR_NOOP("Expand Item"))
        self.menu.addAction(QtCore.QT_TR_NOOP("Collapse Item"))
        self.menu.addMenu(exportFormatMenu)
        exportFormatMenu.addAction('JSON')
        exportFormatMenu.addAction('CSV')
        exportFormatMenu.addAction('XML')
        exportFormatMenu.addAction('M3U')

      # Map menu to the view-port
        self.menu.exec_(self.browseTreeView.viewport().mapToGlobal(pos))

  def tree_browse_menu_click(self, index):
    """
    Processes use of the menu in the tree view.

    Parameters
    ----------
    index : QAction
      Action object based on where in the tree-view clicked.
    """
    contextRow = self.browseTreeView.indexAt(self.menu_on_item)

    # Process menu options
    if 'Collapse' in index.text():
      self.browseTreeView.setExpanded(contextRow, False)
    elif 'Expand' in index.text():
      self.browseTreeView.setExpanded(contextRow, True)
    elif 'JSON' == index.text():
      self.exporter.export_data(self.sparql.get_release_properties(contextRow.data()), self.browseTreeProperties.get_translation_uri(), 'JSON')
    elif 'CSV' == index.text():
      self.exporter.export_data(self.sparql.get_release_properties(contextRow.data()), self.browseTreeProperties.get_translation_uri(), 'CSV')
    elif 'XML' == index.text():
      self.exporter.export_data(self.sparql.get_release_properties(contextRow.data()), self.browseTreeProperties.get_translation_uri(), 'XML')
    elif 'M3U' == index.text():
      self.exporter.export_data(self.sparql.get_release_properties(contextRow.data()), self.browseTreeProperties.get_translation_uri(),  'M3U')
    else:
      pass

  def clickable(self, associatedWidget):
    """
    Takes an input a widget, and returned an instance of a inline-defined class (eventFilter),
    which allows it to become "clickable" with a signal built within the Qt5 slot / signal mechanism.

    Parameters
    ----------
    associatedWidget : QtWidget
      Widget parameter.
    """

    class Filter(QtCore.QObject):
      clickedSignal = QtCore.pyqtSignal()

      def eventFilter(self, object, user_event):
        # If this object matches the one we wish to have an action performed on
        if object == associatedWidget:

          # If the event was a click, and not another QEvent
          if user_event.type() == QtCore.QEvent.MouseButtonRelease:

            # Ensure that the object contains the user event that occured
            if object.rect().contains(user_event.pos()):

              # Emit a signal
              self.clickedSignal.emit()
              return True
        return False

    # Create a instance of Filter, passing the widget as argument
    filterOfWidget = Filter(associatedWidget)

    # Apply the event filter (needed to detect when it's 'clicked')
    associatedWidget.installEventFilter(filterOfWidget)

    # Return the signal, to be applied to a slot
    return filterOfWidget.clickedSignal

  def lastfm_deauthenticate(self):
    """
    Logs a user out of Last.FM integration, and changes UI elements to reflect that.
    """

    self.lastfmHandler.logout()
    self.lastfmBtn.setStyleSheet('')
    self.lastfmStatus.setText("Connect to Last.FM")
    self.clickable(self.lastfmStatus).connect(self.check_lastfm_status)

  def check_lastfm_status(self):
    """
    Checks whether we have an existing Last.FM session, and if not,
    initiates authentication with the API.
    """

    # If we do not have a Last.FM session key already
    if self.lastfmHandler.hasSession() == False:
      # Generate token
      token = self.lastfmHandler.request_auth_token()

      # Create browser dialog for user authentication
      self.browserDialog = QWebEngineView()
      self.browserDialog.setWindowTitle("Connect to Last.FM")
      self.browserDialog.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
      self.browserDialog.setUrl(QtCore.QUrl("https://last.fm/api/auth/?api_key="
                                            + str(self.lastfmHandler.getAPIKey()) + "&token=" + str(token)))
      self.browserDialog.destroyed.connect(self.lastfmHandler.request_session_key)
      self.browserDialog.show()
    # If we have a Last.FM session, change button colour to reflect that
    else:
      self.lastfmBtn.setStyleSheet("""QPushButton {
                                      background-color: #BA2024;
                                    }""")

class BrowseListHandler():
  def __init__(self, app):
    self.app = app

    # Load lists of artists, genres, etc
    self.artistList = sorted(cache.load('artistList'))
    self.artistList[0] = 'Unknown Artist'
    self.genreList = sorted(cache.load('genreList'))
    self.locationList = cache.load('newReversedGroupedLocations')

    self.artistListModel = QtGui.QStandardItemModel(self.app.browseList)
    self.genreListModel = QtGui.QStandardItemModel(self.app.browseList)
    self.locationListModel = QtGui.QStandardItemModel(self.app.browseList)
    self.generate_browse_models(self.artistList, self.artistListModel)
    self.generate_browse_models(self.genreList, self.genreListModel)
    self.generate_location_model(self.locationList, self.locationListModel)

    return

  def change_type(self, type):
    """
    Changes the model shown to the user for browsing the meta-data.

    Parameters
    ----------
    type : int
        The index corresponding to the new browse model
    """

    # Update model relative to 'type'
    if type == 0:
      self.app.browseList.setModel(self.artistListModel)
    elif type == 1:
      self.app.browseList.setModel(self.genreListModel)
    elif type == 2:
      self.app.browseList.setModel(self.locationListModel)

    # Change type order for new list
    self.change_type_order(self.app.typeOrderByCombo.currentIndex())

    return

  def quick_filter_update(self):
    """
    Provides filter functionality for the browsing models.
    """

    # Get text in filter box
    searchStr = self.app.quickFilter.text()  # Created a QlineEdit to input search strings

    # Perform a "CONTAINS" search on the model
    itemsFound = self.app.browseList.model().findItems(searchStr, QtCore.Qt.MatchContains)

    # If items found
    if len(itemsFound) > 0:
      for item in itemsFound:
        if searchStr:
          # Remove row from it's current position
          self.app.browseList.model().takeRow(item.row())

          # Move the row to the top of the list
          self.app.browseList.model().insertRow(0, item)

    self.app.browseList.verticalScrollBar().setValue(0)

  def browse_link_clicked(self, item):
    """
    Adds items relative to the clicked browse item, to the tree view.

    Parameters
    ----------
    item : QStandardItem
        The item clicked
    """

    if 'Genre' in self.app.typeBrowseCombo.currentText():
      self.app.treeViewHandler.update_tree_view(item.data().lower())
    elif 'Location' in self.app.typeBrowseCombo.currentText():
      self.app.treeViewHandler.update_tree_view(self.app.browseListHandler.locationList[item.data()]['locations'])
    else:
      self.app.treeViewHandler.update_tree_view(item.data())

  def generate_browse_models(self, list, model):
    """
    Takes an input list and an empty model, and fills said model.

    Parameters
    ----------
    list : str[]
        The input list of items for the model
    model : QStandardItemModel
        An empty model for QStandardItems
    """

    for item in list:
      item = QtGui.QStandardItem(item)
      model.appendRow(item)

  def generate_location_model(self, dict, model):
    """
    Takes an input dict of locations and an empty model, and fills said model.

    Parameters
    ----------
    dict : dictionary
        The input dictionary of locations for the model
    model : QStandardItemModel
        An empty model for QStandardItems
    """

    list = []

    for key in dict:
      list.append(key)

    for item in sorted(list, key=lambda x: x.replace(' - ', '').rstrip()):
      temp = QtGui.QStandardItem(item)
      model.appendRow(temp)

  def change_type_order(self, index):
    """
    Changes the order of the browse model.

    Parameters
    ----------
    index : int
        The index corresponding to the new type order requested by user.
    """

    types = {}

    # Set the appropriate list and model relative to the browsing model
    if self.app.typeBrowseCombo.currentText() == 'Artist':
      self.artistListModel = QtGui.QStandardItemModel()
      type = self.artistListModel
      loadedList = self.artistList
    elif self.app.typeBrowseCombo.currentText() == 'Genre':
      self.genreListModel = QtGui.QStandardItemModel()
      type = self.genreListModel
      loadedList = self.genreList
    elif self.app.typeBrowseCombo.currentText() == 'Location':
      self.locationListModel = QtGui.QStandardItemModel()
      type = self.locationListModel
      loadedList = self.locationList
    else:
      type = ''
      loadedList = None

    # If not managing locations
    if loadedList is not self.locationList:
      # AZ
      if index == 0:
        self.generate_browse_models(list(sorted(loadedList, key=lambda x: (x[0].isdigit(), x))), type)
      # ZA
      elif index == 1:
        self.generate_browse_models(list(reversed(sorted(loadedList, key=lambda x: (x[0].isdigit(), x)))), type)
    # If handling locations
    else:
      # AZ
      if index == 0:
        self.generate_location_model(loadedList, type)
      # ZA
      elif index == 1:
        location_list = []

        for key in loadedList:
          location_list.append(key)

        # Add row to models
        for item in list(reversed(sorted(location_list, key=lambda x: x.replace('-', '')))):
          temp = QtGui.QStandardItem(item)
          type.appendRow(temp)

    # Set browse list model
    self.app.browseList.setModel(type)

class TreePropertiesView(QtWidgets.QTreeView):
  def __init__(self, app):
    super().__init__()
    self.app = app
    self.setWordWrap(True)
    self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    self.clicked.connect(self.retrieve_properties_subwindow)
    return

  def get_translation_uri(self):
    """
    Returns a list of URI references and corresponding text labels.

    Returns
    ----------
    labels : dict
      Dictionary of URI references and text labels corresponding.
    """

    labels = {'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' : 'Type',
              'http://www.w3.org/2000/01/rdf-schema#seeAlso' : 'See Also',
              'http://purl.org/ontology/mo/performer' : 'Performer',
              'http://etree.linkedmusic.org/vocab/date' : 'Date',
              'http://etree.linkedmusic.org/vocab/description' : 'Description',
              'http://etree.linkedmusic.org/vocab/id' : 'ID',
              'http://etree.linkedmusic.org/vocab/keyword' : 'Keyword(s)',
              'http://etree.linkedmusic.org/vocab/lineage' : 'Lineage',
              'http://etree.linkedmusic.org/vocab/notes' : 'Notes',
              'http://etree.linkedmusic.org/vocab/source' : 'Source',
              'http://etree.linkedmusic.org/vocab/uploader' : 'Uploader',
              'http://purl.org/NET/c4dm/event.owl#place' : 'Place',
              'http://www.w3.org/2004/02/skos/core#prefLabel' : 'Label',
              'http://purl.org/NET/c4dm/event.owl#hasSubEvent' : 'Has Sub Event',
              'http://purl.org/NET/c4dm/event.owl#time' : 'Time',
              'http://etree.linkedmusic.org/vocab/audio' : 'Audio URL',
              'http://etree.linkedmusic.org/vocab/isSubEventOf' : 'Sub Events',
              'http://etree.linkedmusic.org/vocab/number' : 'Track Number',
              'http://purl.org/ontology/mo/performed' : 'Performances',
              'http://xmlns.com/foaf/0.1/name' : 'Name'
              }

    return labels

  def retrieve_properties_subwindow(self, index):
    """
    Provides a properties sub (i.e. below root level) view for a given performance.

    Parameters
    ----------
    index : QModelIndex
      Index in the tree structure the user clicked on.
    """

    # Get labels dictionary for translation to human-readable formats
    labels = self.get_translation_uri()
    if isinstance(index.data(), type(None)):
      return

    if 'http' not in index.data():
      return

    # Retrieve properties for this release
    properties = self.app.sparql.get_release_subproperties(index.data())

    # If no properties retrieved, return
    if type(properties) == None:
      return

    # Group together attributes again
    for property in properties['results']['bindings']:
      treeViewPropertiesDict = self.group_properties(properties)

      # Set to child of item
      i = 0
      for key in sorted(treeViewPropertiesDict.keys()):
        if len(treeViewPropertiesDict[key]) > 0 and len(key) > 4:
          try:
            labelItem = QtGui.QStandardItem(labels[key])
          except KeyError as e:
            labelItem = QtGui.QStandardItem(key)

          try:
            if labels[key] == 'Label':
              self.model().itemFromIndex(index).setText(treeViewPropertiesDict[key][0])
            else:
              self.model().itemFromIndex(index).setChild(i, labelItem)
          except KeyError as e:
            pass
          i += 1

          # Put children in a tree-esque format
          e = 0
          for property in treeViewPropertiesDict[key]:
            propertyItem = QtGui.QStandardItem(property)
            labelItem.setChild(e, propertyItem)
            e += 1

  def retrieve_release_info(self, release):
    """
    Provides an initial properties view for a given performance.

    Parameters
    ----------
    release : str
      Name of release we're retrieving properties for.

    Returns
    ----------
    self : TreePropertiesView
      The instance of the class (to be added to a relevant layout).

    """

    properties = self.app.sparql.get_release_properties(release)
    self.setParent(self.app.additionalInfoFrame)
    self.treePropertiesModel = QtGui.QStandardItemModel(self)
    self.setModel(self.treePropertiesModel)
    self.fill_properties_tree_view(self.treePropertiesModel, properties)
    self.header().hide()

    # Return widget
    return self

  def fill_properties_tree_view(self, model, properties):
    """
    Takes a model and a set of properties, groups them together, and adds them to the tree model.

    Parameters
    ----------
    model : QStandardItemModel
      Tree view model for storing data.

    properties : dict
      Name of release we're retrieving properties for.

    """

    labels = self.get_translation_uri()
    treeViewPropertiesDict = self.group_properties(properties)
    for key in sorted(treeViewPropertiesDict.keys()):
      if len(treeViewPropertiesDict[key]) > 0 and len(key) > 4:
        # Create first level of tree using keyword
        labelItem = QtGui.QStandardItem(labels[key])
        model.appendRow(labelItem)

        # Create children in tree for each property
        e = 0
        for property in treeViewPropertiesDict[key]:
          propertyItem = QtGui.QStandardItem(property)
          labelItem.setChild(e, propertyItem)
          e += 1

  def group_properties(self, properties):
    """
    Provides a properties view for a given performance.

    Parameters
    ----------
    properties : dict
      A dictionary of ungrouped properties.

    Returns
    ----------
    treeViewPropertiesDict : dict
      A dictionary of grouped properties.

    """

    treeViewPropertiesDict = {}
    for property in properties['results']['bindings']:
      if property['p']['value'] not in treeViewPropertiesDict:
        treeViewPropertiesDict[property['p']['value']] = []
      treeViewPropertiesDict[property['p']['value']].append(property['o']['value'])
    return treeViewPropertiesDict


class BrowseTreeViewHandler():
  def __init__(self, main):
    self.main = main
    self.main.browseList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

  def tree_view_filter_update(self):
    """
    Provides filter functionality for the the tree view.
    """
    try:
      searchStr = self.main.treeViewFilter.text()
      itemsFound = self.main.browseTreeView.model().findItems(searchStr, QtCore.Qt.MatchContains)

      # If items found
      if len(itemsFound) > 0:
        for item in itemsFound:
          if searchStr:
            # Remove row from it's current position
            self.main.browseTreeView.model().takeRow(item.row())

            # Move the row to the top of the list
            self.main.browseTreeView.model().insertRow(0, item)

      self.main.browseTreeView.verticalScrollBar().setValue(0)
    except AttributeError as e:
      # If no model set, return
      return

  def expand_tree_item(self, index):
    """
    Expands a performance, adding its tracklist as children in the tree.

    Parameters
    ----------
    index : QModelIndex
        The index in the treeview (i.e. the performance), clicked.
    """

    # If not a child (i.e. a track belonging to a release
    if type(self.main.treeViewModel.itemFromIndex(index)) != None:
      if self.main.treeViewModel.itemFromIndex(index).parent() == None:
        # Retrieve tracklist from SPARQL end-point
        tracklist = self.main.sparql.get_tracklist_grouped(str(index.data()))
        self.currentReleaseData = tracklist['results']['bindings']

        i = 0
        preventDuplicates = []
        for track in tracklist['results']['bindings']:
          if track['num']['value'] not in preventDuplicates:
            # Add to treeView
            listItem = QtGui.QStandardItem(str(track['num']['value']) + '. ' + track['label']['value'])
            preventDuplicates.append(track['num']['value'])
            self.main.treeViewModel.itemFromIndex(index).setChild(i, listItem)
            i += 1

        self.main.browseTreeView.collapseAll()
        self.main.browseTreeView.expand(index)

        try:
          self.main.browseTreePropertiesLayout.takeAt(1)
        except AttributeError:
          self.main.browseTreePropertiesLayout = QtWidgets.QBoxLayout(1)

        self.main.browseTreePropertiesLayout.setContentsMargins(0, 0, 0, 0)
        self.main.browseTreePropertiesLayout.addWidget(self.main.browseTreeProperties.retrieve_release_info(index.data()))

        self.main.additionalInfoFrame.setLayout(self.main.browseTreePropertiesLayout)

  def play_tree_item(self, index):
    """
    Called when an item in the browse tab treeview is double-clicked, starting audio playback

    Parameters
    ----------
    index : QModelIndex
        The row index clicked by the user.
    """

    # If this is a release, and not a singular track
    if self.main.treeViewModel.itemFromIndex(index).parent() == None:
      # Play every track in this recording
      tracklist = self.main.sparql.get_tracklist(index.data())
      self.main.debugDialog.add_line("{0}: retrieved tracklist for release {1}".format(sys._getframe().f_code.co_name, index.data()))
      self.main.audioHandler.user_audio_clicked(self.main.audioHandler.extract_tracklist_single_format(tracklist), 0)
    # If user clicked on a track
    else:
      trackIndex, prefFormat = self.get_track_index_and_format(index, self.currentReleaseData)

      # Extract individual tracks in that format, add to audioList
      if prefFormat == None:
        # Add error to debug dialog
        self.main.debugDialog.add_line("{0}: failed to retrieve matching format for release {1}".format(sys._getframe().f_code.co_name, index.data()))
        return
      else:
        # Generate audio list
        audioList = self.add_tracks_audiolist(self.currentReleaseData, trackIndex, prefFormat)

        # Start audio playback
        self.main.audioHandler.user_audio_clicked(audioList, trackIndex)

        # Update icons
        self.main.audioHandler.isPlaying = True
        self.main.playPauseBtn.setIcon(qta.icon('fa.pause'))

  def get_track_index_and_format(self, index, releaseData):
    # Get all formats available
    foundFormat = False
    prefFormat = None
    trackIndex = 0

    # Find track to start from
    for track in releaseData:
      if track['num']['value'] == index.data()[:1]:
        trackIndex = int(float(track['num']['value']))

    # Extract formats and choose relative to users preferred choice
    for url in releaseData[0]['audio']['value'].split('\n'):
      for format in self.main.formats:
        if not foundFormat:
          if self.main.formatDict[format] in url:
            # Found valid format
            foundFormat = True
            prefFormat = self.main.formatDict[format]

    return trackIndex, prefFormat

  def add_tracks_audiolist(self, releaseData, trackIndex, prefFormat):
    audioList = []
    for track in releaseData:
      if int(float(track['num']['value'])) >= trackIndex:
        prefUrl = None

        # Get url
        for url in track['audio']['value'].split('\n'):
          if prefFormat in url[-10:]:
            prefUrl = url

            # Add to audio list
            audioList.append(track)
            audioList[-1]['audio']['value'] = prefUrl

    return audioList

  def update_tree_view(self, itemText):
    selectedType = self.main.typeBrowseCombo.currentText()

    # We do not need any extra triples to get artist information, so final 2 arguments are NULL
    if selectedType == 'Artist':
      modelRawData = self.main.sparql.get_artist_releases('name', itemText, '', '')
    elif selectedType == 'Genre':
      modelRawData = self.main.sparql.get_artist_releases('genre', itemText, '?genre', '?performer etree:mbTag ?genre.\n')
    elif selectedType == 'Location':
      modelRawData = self.main.sparql.get_artist_releases('place', itemText, '', '')
    else:
      raise(str('Error'))
    self.main.treeViewModel = QtGui.QStandardItemModel(self.main.browseTreeView)

    for result in modelRawData["results"]["bindings"]:
      # Create an item to add to the model
      item = QtGui.QStandardItem(result['prefLabel']['value'])

      # Add item to our model
      self.main.treeViewModel.appendRow(item)

      # Set our model to the browsing list
      self.main.browseTreeView.setModel(self.main.treeViewModel)

class TableHandler():
  def __init__(self, prog):
    self.prog = prog

    # Create table thread
    self.sublist = {}

    # Create a new tab in our table widget
    self.widget = QtWidgets.QWidget()
    self.layout = QtWidgets.QGridLayout(self.widget)
    self.resultsTable = Table(self.widget) # QtWidgets.QTableWidget(self.widget)

  def on_table_scroll(self, value):
    """
    Starts a new thread for replacing URIs with location labels.

    Parameters
    ----------
    value : int
        The desired row index.
    """
    rect = self.resultsTable.viewport().rect()
    topRow = self.resultsTable.indexAt(rect.topLeft()).row()

    # Retrieve labels for next 5 items
    worker = multithreading.WorkerThread(self.retrieve_labels_scroll, topRow)
    worker.qt_signals.update_table_item.connect(self.update_table_item)
    self.prog.threadpool.start(worker)

  def retrieve_labels_scroll(self, startRow, **kwargs):
    """
    Retrieves location labels to replace URIs, upon scrolling.

    Parameters
    ----------
    value : int
        The desired row index.
    """
    try:
      for rowIndex in range(startRow, startRow+int(self.resultsTable.height()/25.5)):
        for columnIndex in range(0,self.resultsTable.columnCount()-1):
          if 'http://etree.' in self.resultsTable.item(rowIndex, columnIndex).text():
            newLabel = self.get_label_for_URI(self.resultsTable.item(rowIndex, columnIndex).text())
            kwargs['update_table_item'].emit(rowIndex, columnIndex, newLabel)
    except AttributeError as a:
      print(a)
      return

  def update_table_item(self, row, col, text):
    """
    Updates a particular table item.

    This function is mainly used for replacing URIs with human-readable labels.

    Parameters
    ----------
    row : int
        The desired row index.
    col : int
        The desired column index.
    text : str
        The text to update the item with.
    """
    self.resultsTable.item(row, col).setText(text)

  def get_table_container(self):
    """
    Returns the table element instance widget.
    """
    return self.widget

  def get_table(self):
    """
    Returns the table element instance.
    """
    return self.resultsTable

  def fill_table(self, results):
    """
    Starts a thread to fill the table with the data returned from a search.

    Parameters
    ----------
    results : dict
        Dictionary of results returned from the SPARQL query.
    """
    worker = multithreading.WorkerThread(self.generate_results_table, results)
    worker.qt_signals.add_table_item.connect(self.add_table_item)
    worker.qt_signals.start_table.connect(self.generate_table_start)
    worker.qt_signals.end_table.connect(self.generate_table_end)
    self.prog.threadpool.start(worker)
    self.prog.debugDialog.add_line("{0}: started table thread".format(sys._getframe().f_code.co_name))

  def add_table_item(self, i, c, itemText):
    """
    Adds an item to the table view.

    Parameters
    ----------
    i : int
        Row index.
    c : int
        Row index.
    itemText : str
        Table item text.
    """
    try:
      self.resultsTable.setItem(i, c, itemText)
    except IndexError as e:
      self.prog.debugDialog.add_line("{0}: {1}".format(sys._getframe().f_code.co_name, "AddTableItem error"))
    except RuntimeError as r:
      self.prog.debugDialog.add_line("{0}: {1}".format(sys._getframe().f_code.co_name, "RunTime error"))
      pass
  def generate_table_start(self, c, col, columnNames):
    """
    Adds an item to the table view.

    Parameters
    ----------
    c : int
        Number of rows for the table.
    col : int
        Number of columns for the table.
    columnNames : str[]
        List of column names.
    """

    # Hide the widget while we process data
    self.widget.hide()

    # Set table size and initial properties
    self.resultsTable.setRowCount(c)
    self.resultsTable.setColumnCount(col)
    self.resultsTable.setHorizontalHeaderLabels(columnNames)
    self.resultsTable.setSortingEnabled(False)

    # Set header properties
    header = self.resultsTable.horizontalHeader()
    header.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
    # header.setStretchLastSection(True)
    vHeader = self.resultsTable.verticalHeader()
    vHeader.setVisible(False)

    self.prog.debugDialog.add_line("{0}: set initial table properties".format(sys._getframe().f_code.co_name))

  def generate_table_end(self):
    """
    Performs post-processing on table after all the data has been entered.
    """

    try:
      # Set final properties for the table
      # self.resultsTable.setVisible(False)
      self.resultsTable.resizeColumnsToContents()
      # self.resultsTable.setVisible(True)
      self.resultsTable.setSortingEnabled(True)
      self.resultsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
      self.resultsTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
      self.resultsTable.setMinimumHeight(100)
      self.resultsTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
      self.resultsTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
      self.layout.setContentsMargins(0,0,0,11)
      #  self.resultsTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
      # Add focus signal handlers
      self.resultsTable.itemClicked.connect(self.prog.searchHandler.view.move_focus)
      self.resultsTable.verticalScrollBar().valueChanged.connect(self.on_table_scroll)
      self.resultsTable.itemDoubleClicked.connect(self.search_table_clicked)
      self.resultsTable.horizontalHeader().setStretchLastSection(True)
      # Get first 5 URI replacements
      self.on_table_scroll(0)

      # Add widget to the data view
      self.resultsTable.setParent(self.widget)
      self.layout.addWidget(self.resultsTable, 0, 0, 1, 1)

      self.resultsTable.setColumnWidth(3, 150)
      self.resultsTable.setColumnWidth(0, 250)

      self.resultsTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
      self.resultsTable.customContextMenuRequested.connect(self.open_table_menu)
      self.resultsTable.setStyleSheet("QTreeView::item { height: 50px;}")

      self.widget.show()

      self.prog.debugDialog.add_line("{0}: set final table properties".format(sys._getframe().f_code.co_name))
    except RuntimeError as e:
      print(e)
      return

  def open_table_menu(self, pos):
    """
    Called when the user requests a context menu from the tree view.

    Parameters
    ----------
    pos : QPoint
        Relative geometric position in the widget.
    """

    self.menuOnItem = pos
    indexes = self.resultsTable.selectedIndexes()

    # Create menu
    self.menu = QtWidgets.QMenu()
    exportFormatMenu = QtWidgets.QMenu("Export Data")
    self.menu.triggered.connect(self.table_browse_menu_click)

    # # If performance
    # if level == 0:
    self.menu.addMenu(exportFormatMenu)
    exportFormatMenu.addAction('JSON')
    exportFormatMenu.addAction('CSV')
    exportFormatMenu.addAction('XML')
    exportFormatMenu.addAction('M3U')

    for c in range(0, self.resultsTable.columnCount()):
      if self.resultsTable.horizontalHeaderItem(c).text() == 'Calma':
        if (self.resultsTable.item(indexes[0].row(), c).text()) == 'Y':
          calmaOptionMenu = QtWidgets.QMenu("CALMA")
          self.menu.addMenu(calmaOptionMenu)
          calmaOptionMenu.addAction('View Segmentation')
          calmaOptionMenu.addAction('View Key Changes')

    # Map menu to the view-port
    self.menu.exec_(self.resultsTable.viewport().mapToGlobal(pos))
  def table_browse_menu_click(self, index):
    """
    Processes use of the menu in the tree view.

    Parameters
    ----------
    index : QAction
      Action object based on where in the tree-view clicked.
    """
    contextRow = self.resultsTable.indexAt(self.menuOnItem)

    for c in range(0, self.resultsTable.columnCount()):
      if self.resultsTable.horizontalHeaderItem(c).text() == 'Performance Title':
        label = self.resultsTable.item(contextRow.row(), c).text()
        self.exporter = export.Export(self.prog)

        # Process menu options
        if 'JSON' == index.text():
          self.exporter.export_data(self.prog.sparql.get_release_properties(label), self.prog.browseTreeProperties.get_translation_uri(),
                                    'JSON')
        elif 'CSV' == index.text():
          self.exporter.export_data(self.prog.sparql.get_release_properties(label), self.prog.browseTreeProperties.get_translation_uri(), 'CSV')
        elif 'XML' == index.text():
          self.exporter.export_data(self.prog.sparql.get_release_properties(label), self.prog.browseTreeProperties.get_translation_uri(), 'XML')
        elif 'M3U' == index.text():
          self.exporter.export_data(self.prog.sparql.get_release_properties(label), self.prog.browseTreeProperties.get_translation_uri(),  'M3U')
        elif 'View Segmentation' == index.text():
          self.releaseView = calma.CalmaPlotRelease(self.prog, label, 'segment')
          self.prog.debugDialog.add_line("{0}: started CALMA segmentation plot release for {1}".format(sys._getframe().f_code.co_name, label))
        elif 'View Key Changes' == index.text():
          self.releaseView = calma.CalmaPlotRelease(self.prog, label, 'key')
          self.prog.debugDialog.add_line("{0}: started CALMA key change plot release for {1}".format(sys._getframe().f_code.co_name, label))
        else:
          pass

  def search_table_clicked(self, title):
    searchColumn = None

    # If another column clicked
    if title.column() != 0:
      title = title.tableWidget().item(title.row(), 0)
    tracklist = self.prog.sparql.get_tracklist(title.text())
    self.prog.audioHandler.user_audio_clicked(self.prog.audioHandler.extract_tracklist_single_format(tracklist), 0)

  def change_focus(self, index):
    searchColumn = None
    try:
      # Add line to debug dialog
      self.prog.debugDialog.add_line("{0}: moving focus to index {1}".format(sys._getframe().f_code.co_name, index))

      # If index is a number
      if self.check_is_number(index):
        # Select that row
        self.resultsTable.selectRow(int(index))
        return int(index)
      else:
        # Find label column in table
        for c in range(0, self.resultsTable.columnCount() - 1):
          if self.resultsTable.horizontalHeaderItem(c).text() == 'Performance Title':
            searchColumn = c

        if searchColumn is not None:
          # Find matching label
          for row in range(0, self.resultsTable.rowCount() -1):
            if self.resultsTable.item(row, searchColumn).text().rstrip() == index.rstrip():
              self.resultsTable.selectRow(row)
              return row
        return None
    except IndexError as e:
      self.main.debugDialog.add_line('{0}: {1}'.format(sys._getframe().f_code.co_name, self.main.formats[e]))
      return None

  def check_is_number(self, n):
    # Try and convert to a float
    try:
      float(n)
      return True
    # If not a number
    except ValueError as v:
      return False

  def generate_results_table(self, results, **kwargs):
    c = 0
    col = 0
    keys = []
    self.titleList = []

    if results is not None:
      try:
        # Calculate the properties we should apply to our table
        for result in results["results"]["bindings"]:
          self.titleList.append(result['label']['value'])
          keys = list(result.keys())
          c = c + 1
          col = len(keys)

        # Tidy up column names
        columnNames = []
        for e in keys:
          if e == 'label':
            columnNames.append("Performance Title")
          else:
            columnNames.append(e.title())

        # Dynamically set table properties
        kwargs['start_table_callback'].emit(c, col, columnNames)

        # Add data to the table
        i = 0
        for result in results["results"]["bindings"]:
          c = 0
          for column in keys:
            # Create new table item and emit details of this to main thread
            if i < 5 and 'http://etree' in result[str(column)]["value"]:
              artist = QtWidgets.QTableWidgetItem(self.get_label_for_URI(result[str(column)]["value"]))
            elif column == 'calma':
              if len(result[str(column)]["value"]) > 0:
                artist = QtWidgets.QTableWidgetItem("Y")
              else:
                artist = QtWidgets.QTableWidgetItem("N")
            else:
              artist = QtWidgets.QTableWidgetItem(result[str(column)]["value"])
            kwargs['add_table_item'].emit(i, c, artist)
            c = c + 1
          i = i + 1
      except KeyError as e:
        self.main.debugDialog.add_line('{0}: {1}'.format(sys._getframe().f_code.co_name, e))

    # Resize to contents after adding data
    kwargs['fin_table_callback'].emit()

  def get_label_for_URI(self, URI):
    label = None
    properties = self.prog.sparql.get_release_subproperties(URI)

    try:
      for property in properties['results']['bindings']:
        if property['p']['value'] == "http://www.w3.org/2004/02/skos/core#prefLabel":
          label = property['o']['value']
          self.prog.debugDialog.add_line("{0}: retrieved label {1}".format(sys._getframe().f_code.co_name, label))

    except TypeError as t:
      pass

    if label == None : label = URI

    return label

  def set_location_width(self):
    for c in range(0,self.resultsTable.columnCount()-1):
      if self.resultsTable.horizontalHeaderItem(c).text() == 'Location':
        self.resultsTable.setColumnWidth(c, 400)


class MapHandler():
  def __init__(self, prog, webEngine):
    self.engine = webEngine
    self.prog = prog
    self.mapsClass = maps.Maps()

  def add_search_results_map(self, results):
    if results is not None:
      worker = multithreading.WorkerThread(self.mapsClass.homepage_add, results)
      worker.qt_signals.js_callback.connect(self.add_point)
      worker.qt_signals.homepage_end.connect(self.end_data_processing)
      worker.qt_signals.homepage_start.connect(self.start_data_processing)
      self.prog.threadpool.start(worker)
      self.prog.debugDialog.add_line("{0}: started geographical visualization thread".format(sys._getframe().f_code.co_name))

  def process_search_results(self, results, **kwargs):
    self.start_data_processing()
    # For each item of data
    for item in results['results']['bindings']:
      # Send message to main thread to pass data to JS instance
      self.mapsClass.add(item, kwargs['js_callback'])
    self.engine.page().runJavaScript('onFinishQuery(0)')

  def end_data_processing(self):
    # Tell JS instance that no more data will be sent
    self.engine.page().runJavaScript('onFinishQuery(0)')
    self.engine.show()
    self.prog.debugDialog.add_line("{0}: finished geographical visualization thread".format(sys._getframe().f_code.co_name))

  def start_data_processing(self):
    # Tell JS instance to prepare for data to be processed
    self.engine.page().runJavaScript('newDataSet(0)')

  def add_point(self, lat, lng, title):
    js = "addPoint(" + lat + "," + lng + ", 1, 0,`" + title + "`);"
    self.engine.page().runJavaScript(js)

class DebugDialog(QtWidgets.QTextEdit):
  def __init__(self):
    super().__init__()
    self.setFixedSize(700, 300)
    self.setWindowTitle('Debug Window')
    self.setReadOnly(True)

  def add_line(self, text):
    self.append(str(text))

    # Scroll to bottom
    self.verticalScrollBar().maximum()

  def clear(self):
    self.clear()

class NowPlaying():
  def __init__(self, prog):
    self.prog = prog

  def update_now_playing_view(self):
    artist = self.prog.sparql.get_artist_from_tracklist(self.prog.audioHandler.playlist[self.prog.audioHandler.playlist_index][2])

    # Update various GUI elements
    self.update_playlist_view()
    self.update_lastfm_tags(artist)
    self.update_similar_artists(artist)

  def update_playlist_view(self):
    # Clear contents of playlist view
    self.playlistViewModel = QtGui.QStandardItemModel()
    self.playlist = self.prog.audioHandler.playlist
    self.selectionModel = self.prog.playlist_view
    self.current_index = self.prog.audioHandler.playlist_index

    rowIndex = 0
    toBeSelected = None

    for item in self.playlist:
      qStandardItem = QtGui.QStandardItem(item[1])
      self.playlistViewModel.insertRow(rowIndex, qStandardItem)

      if rowIndex == self.prog.audioHandler.playlist_index:
        toBeSelected = qStandardItem

      rowIndex += 1

    self.prog.playlist_view.setModel(self.playlistViewModel)
    self.prog.playlist_view.setCurrentIndex(self.playlistViewModel.indexFromItem(toBeSelected))

  def update_similar_artists(self, artist):
    self.prog.similarArtistsList.clear()
    similarArtists = self.prog.lastfmHandler.get_similar_artists(artist)
    if 'error' in similarArtists:
      return
    else:
      rowIndex = 0

      for artist in similarArtists:
        self.prog.similarArtistsList.insertItem(rowIndex, artist)
        rowIndex += 1

  def update_lastfm_tags(self, artist):
    self.prog.artistTagsList.clear()
    tags = self.prog.lastfmHandler.get_tags_for_artist(artist)

    if 'error' in tags:
      return
    else:
      rowIndex = 0
      for tag in tags['artist']['tags']['tag']:
        self.prog.artistTagsList.insertItem(rowIndex, tag['name'].title())
        rowIndex += 1

# Python-side call handler for communicating between audio player / map and python
class CallHandler(QtCore.QObject):
  def __init__(self, app):
    super().__init__()
    self.app = app

  @QtCore.pyqtSlot(str, str)
  def map_tracklist_popup(self, link, label):
    self.app.searchHandler.view.move_focus(label)
    popup = "<bold>{0}</bold><br>".format(label)

    # Get venue information for this arg
    geoInfo = self.app.sparql.get_venue_information(label)
    if geoInfo['lastfm'] is not None:
      popup += geoInfo['lastfm'] # prog.lastfmHandler.get_venue_info(geoInfo['lastfm'])
    else:
      popup += "\n {0} <br>".format("<b> Last.FM data unavailable.")

    if geoInfo['geoname'] is not None:
      id = geoInfo['geoname'][geoInfo['geoname'].rfind('/') + 1:]
      popup += "\n {0}".format(self.generate_geoname_html(id))
    else:
      popup += "\n {0}".format("GeoNames data unavailable.")
    self.app.searchHandler.view.mapSearchDialog.page().runJavaScript("setPopup({0},`{1}`)".format(link, popup))
    self.app.debugDialog.add_line("{0}: pop-up generated from user click".format(sys._getframe().f_code.co_name))

  def generate_geoname_html(self, id):
    r = requests.get("http://api.geonames.org/getJSON?geonameId={0}&username={1}".format(id, "Masutatsu"))
    json = r.json()
    html = ""
    html += "<br><br> <b>Location:</b> {0} <br>".format(json['name'])
    html += "<b>Latitude:</b> {0} <br>".format(json['lat'])
    html += "<b>Longitude:</b> {0} <br>".format(json['lng'])
    html += "<b>Timezone:</b> {0} (GMT {1}) <br>".format(json['timezone']['timeZoneId'], json['timezone']['gmtOffset'])
    html += "<a href=geoNamesBounds({0},{1},{2},{3})>View GeoNames bounds</a>".format(json['bbox']['east'], json['bbox']['south'],
                                                                                      json['bbox']['north'], json['bbox']['west'])
    return html

class ErrorDialog(QtWidgets.QErrorMessage):
  def __init__(self, exception):
    super().__init__()
    if type(exception).__name__ == 'HTTPError':
      self.message = 'A HTTP error occurred, this could be due to the SPARQL end-point being unavailable'
    else:
      print('Error dialog recieved non-mapped error: {0}'.format(type(exception).__name__))
      self.message = str(Exception)
    self.setWindowTitle('Error')
    self.showMessage(self.message)
    self.show()

class Table(QtWidgets.QTableWidget):
  def __init__(self, parent):
    super().__init__(parent)

if __name__ == '__main__':
  # Create QApplication instance
  app = QtWidgets.QApplication(sys.argv)
  app.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd()) + "/img/icon.png"))

  # Create dialog to show this instance
  dialog = QtWidgets.QMainWindow()

  # Start main event loop
  prog = mainWindow(dialog)

  # Show the main dialog window to user
  dialog.show()

  # On user exit, stop the application
  sys.exit(app.exec_())
