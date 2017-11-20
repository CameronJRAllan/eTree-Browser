#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
  import sys
  sys.path.append("..")
  import time
  import os
  from math import sin, cos, sqrt, atan2, radians
  from PyQt5 import QtCore, QtWidgets, QtGui, QtMultimedia
  from UI import UI
  import sys
  import lastfm
  import maps
  import gi
  import traceback
  import json
  import sparql
  import re
  import cache
  import json
  import multithreading
  import audio
  import requests
  import calma
  import export
  import view
  import qtawesome as qta
  from PyQt5.QtWebChannel import QWebChannel
  from PyQt5.QtWebEngineWidgets import QWebEngineView
  import hashlib
except (ImportError, ModuleNotFoundError) as e:
  print('You are missing package: ' + str(e)[15:])
  exit(1)

class mainWindow(UI):
  def __init__(self, dialog):
    UI.__init__(self)

    # UI
    self.setupUi(dialog)
    self.set_tooltips()
    # self.set_window_css()

    # Set-up handlers for classes
    self.searchHandler = SearchHandler(self)
    self.audioHandler = audio.Audio(self)
    self.sparql = sparql.SPARQL()
    self.exporter = export.Export()
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
    self.format_dict = {'FLAC' : '.flac', 'MP3 (64Kbps)' : '.64.mp3', 'SHN' : '.shn', 'WAV' : '.wav', 'OGG' : '.ogg',
                        'MP3 (VBR)' : 'vbr.mp3'}

    self.playlists = [{'name': 'Playlist 1', 'items': QtGui.QStandardItemModel()}]

    # Set-up multi-threading pools
    self.threadpool = QtCore.QThreadPool()
    self.audioThreadpool = QtCore.QThreadPool()

    # self.currentDateLabel.setText(str("On this day in history: " + str(time.strftime("%A %dth of %B"))))

    # Create map handler and class
    #self.mapHomeHandler = MapHandler(self, self.homeMapView)
    #self.homeMapView.loadFinished.connect(self.mapHomeHandler.get_on_this_day)
    self.mapsPath = os.path.join(os.getcwd()) + "/html/map.htm"

    # os.path.join(os.path.dirname(__file__) + "/html/map.htm")
    #self.homeMapView.setUrl(QtCore.QUrl("file://" + self.mapsPath))
    self.latlng = cache.load('locationLatLng')

    # Initialize playlists
    #self.initialize_playlists()

    # If we already have a session key stored for Last.FM
    if self.lastfmHandler.hasSession() == True:
      # Set button to red to indicate this
      self.lastfmBtn.setStyleSheet("""QPushButton {
                                      background-color: #BA2024;
                                      }""")
      self.lastfmStatus.setText("Connected to Last.FM")
    else:
      # Set text to indicate user to connect to Last.FM
      self.lastfmStatus.setText("Connect to Last.FM")

    # Create data structure for storing search results
    self.searchResults = []
    self.searchesExecuted = 0
    self.searchTabElements = []

    # Set-up signals for message passing
    #self.newPlaylistBtn.clicked.connect(self.new_playlist)
    self.trackProgress.sliderReleased.connect(self.audioHandler.track_seek)
    self.browseTreeView.clicked.connect(self.treeViewHandler.expand_tree_item)
    self.browseTreeView.doubleClicked.connect(self.treeViewHandler.play_tree_item)
    self.clickable(self.lastfmStatus).connect(self.check_lastfm_status)
    self.clickable(self.playPauseBtn).connect(self.audioHandler.play_pause)
    self.clickable(self.nextBtn).connect(self.audioHandler.next_click)
    self.clickable(self.prevBtn).connect(self.audioHandler.previous_click)
    self.typeBrowseCombo.currentIndexChanged.connect(self.browseListHandler.change_type)
    self.typeOrderByCombo.currentIndexChanged.connect(self.browseListHandler.change_type_order)
    self.quickFilter.textChanged.connect(self.browseListHandler.quick_filter_update)
    self.treeViewFilter.textChanged.connect(self.treeViewHandler.tree_view_filter_update)
    self.browseList.clicked.connect(self.browseListHandler.browse_link_clicked)
    self.searchBtn.clicked.connect(self.searchHandler.perform_search)
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

    # Initialize map web channel (message passing between JS + Python)
    #self.initialize_web_channel(self.homeMapView)

    # Set-up advanced search signals
    self.addConditionBtn.pressed.connect(self.searchHandler.add_custom_condition)
    self.removeConditionBtn.pressed.connect(self.searchHandler.remove_custom_condition)

    # Set-up search auto-complete
    self.artistFilter.setCompleter(self.auto_comp(cache.load('artistList')))
    self.genreFilter.setCompleter(self.auto_comp(cache.load('genreList')))
    self.locationFilter.setCompleter(self.auto_comp(cache.load('newReversedGroupedLocations')))
    self.countryFilter.setCompleter(self.auto_comp(cache.load('countries')))

    # Create menu
    self.browseTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.browseTreeView.customContextMenuRequested.connect(self.open_tree_menu)
    self.browseTreeView.setStyleSheet("QTreeView::item { height: 50px;}")

    # Set our model to the browsing list
    self.browseList.setModel(self.browseListHandler.artistListModel)

    # Create history table
    self.initialize_history_table()

    self.searchHandler.add_search_tab_contents()

  def debug_window_state_changed(self, state):
    if state == 2:
      self.debugDialog.show()
    else:
      self.debugDialog.hide()

  def nowplaying_playlist_clicked(self, item):
    self.audioHandler.start_audio_single_link(self.audioHandler.playlist[item.row()][1], 0)

  def initialize_web_channel(self, widget):
    # Set-up web channel between python + JS components
    self.mapChannel = QWebChannel()
    self.mapHandler = CallHandler()
    self.mapChannel.registerObject('mapHandler', self.mapHandler)
    widget.page().setWebChannel(self.mapChannel)

  def preferred_format_changed(self, item):
    # Change format to new preferred
    index = self.formats.index(item) # self.format_dict[item]
    self.formats[index], self.formats[0] = self.formats[0], self.formats[index]
    self.debugDialog.add_line('{0}: set new preferred format to {1}'.format(sys._getframe().f_code.co_name, self.formats[0]))

  def append_history_table(self, track, artist, label, url):
    self.track_history.append([track, artist, time.strftime('%Y-%m-%d %H:%M:%S'), label, url])
    cache.save(self.track_history, 'play_history')
    self.initialize_history_table()

  def initialize_history_table(self):
    self.savedSearchesList.clear()
    self.savedSearches = cache.load('savedSearches')
    for item in reversed(self.savedSearches):
      self.savedSearchesList.addItem(item[0])

    self.historyTableWidget.clear()
    self.historyTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    self.historyTableWidget.doubleClicked.connect(self.history_table_clicked)

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

    # Format table nicely
    self.historyTableWidget.setVisible(False)
    self.historyTableWidget.resizeColumnsToContents()
    self.historyTableWidget.setSortingEnabled(True)
    self.historyTableWidget.setVisible(True)

  def history_table_clicked(self, index):
    row = self.historyTableWidget.row(self.historyTableWidget.itemFromIndex(index))

    for x in reversed(self.track_history):
      if (x[2] == self.historyTableWidget.item(row, 2).data(2)):
        self.audioHandler.start_audio_single_link(x[4], 0)

  def scrobble_track_lastfm(self):
    try:
      artist = self.sparql.get_artist_from_tracklist(self.audioHandler.playlist[self.audioHandler.playlist_index][2])
      self.lastfmHandler.update_now_playing(artist, self.audioHandler.playlist[self.audioHandler.playlist_index][1])
    except Exception as e:
      print(e)
      return

  #
  # def playlist_clicked(self, index):
  #   for item in self.playlists:
  #     if item['name'] == index.data():
  #       items = item['items']
  #
  #       # self.selectedPlaylistModel = QtGui.QStandardItemModel(self.playlistTreeView)
  #       # self.generateModels(items, self.selectedPlaylistModel)
  #
  #       # Set our model to the browsing list
  #       items.appendRow(QtGui.QStandardItem('Test Item'))
  #       self.playlistTreeView.setModel(items)
  #       # with open('data/playlists.mmd', 'w') as outfile:
  #       #   json.dump(self.playlists, outfile)
  #       print(str(items))

  def auto_comp(self, inputList):
    """
    Creates and returns an auto-completer with the input list.

    Parameters
    ----------
    self : instance
        Class instance.
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

    # Return to be set to the relevant GUI text-box
    return lineEditCompleter

  # def initialize_playlists(self):
  #   # Create model for our playlist view
  #   self.playlistModel = QtGui.QStandardItemModel(self.playlistTreeView)
  #
  #   # Append each to model
  #   for playlist in self.playlists:
  #     item = QtGui.QStandardItem(playlist['name'])
  #     self.playlistModel.appendRow(item)
  #
  #   # Set our list model to our new created model
  #   self.playlistList.setModel(self.playlistModel)
  #
  # def new_playlist(self):
  #   # self.playlists.append(["New Playlist", []])
  #
  #   with open('data/playlists.mmd', 'w') as outfile:
  #     json.dump(self.playlists, outfile)

  def set_tooltips(self):
    """
    Sets up help tooltips which appear when the user hovers over a particular widget.

    Parameters
    ----------
    self : instance
        Class instance.
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
    self : instance
        Class instance.

    pos : QStandardItem
        The item the user right clicked on
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
      menu = QtWidgets.QMenu()
      exportFormatMenu = QtWidgets.QMenu("Export Data")
      menu.triggered.connect(self.tree_browse_menu_click)

      # If performance
      if level == 0:
        menu.addAction(QtCore.QT_TR_NOOP("Expand Item"))
        menu.addAction(QtCore.QT_TR_NOOP("Collapse Item"))
        menu.addMenu(exportFormatMenu)
        exportFormatMenu.addAction('JSON')
        exportFormatMenu.addAction('CSV')
        exportFormatMenu.addAction('XML')
        exportFormatMenu.addAction('M3U')
      # If track
      elif level == 1:
        menu.addAction(QtCore.QT_TR_NOOP("Expand Item"))
        menu.addAction(QtCore.QT_TR_NOOP("Collapse Item"))
        menu.addAction(QtCore.QT_TR_NOOP("Play All Renditions"))
        menu.addMenu(exportFormatMenu)
        exportFormatMenu.addAction('JSON')
        exportFormatMenu.addAction('CSV')
        exportFormatMenu.addAction('XML')
        exportFormatMenu.addAction('M3U')

      # Map menu to the view-port
      menu.exec_(self.browseTreeView.viewport().mapToGlobal(pos))

  def tree_browse_menu_click(self, index):
    """
    Processes use of the menu in the tree view.

    Parameters
    ----------
    self : instance
        Class instance.

    index : int
    """

    contextRow = self.browseTreeView.indexAt(self.menu_on_item)

    # Process menu options
    if 'Collapse' in index.text():
      self.browseTreeView.setExpanded(contextRow, False)
    elif 'Expand' in index.text():
      self.browseTreeView.setExpanded(contextRow, True)
    elif 'JSON' == index.text():
      self.exporter.export_data(self.sparql.get_release_properties(contextRow.data()), self.get_translation_uri(), 'JSON')
    elif 'CSV' == index.text():
      self.exporter.export_data(self.sparql.get_release_properties(contextRow.data()), self.get_translation_uri(), 'CSV')
    elif 'XML' == index.text():
      self.exporter.export_data(self.sparql.get_release_properties(contextRow.data()), self.get_translation_uri(), 'XML')
    elif 'M3U' == index.text():
      self.exporter.export_data(self.sparql.get_release_properties(contextRow.data()), self.get_translation_uri(),  'M3U')
    else:
      print('No matching menu item')

  def clickable(self, associatedWidget):
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

    filterOfWidget = Filter(associatedWidget)
    associatedWidget.installEventFilter(filterOfWidget)
    return filterOfWidget.clickedSignal

  def check_lastfm_status(self):
    """
    Checks whether we have an existing Last.FM session, and if not,
    initiates authentication with the API.

    Parameters
    ----------
    self : instance
        Class instance.
    """
    # If we do not have a Last.FM session key already
    if self.lastfmHandler.hasSession() == False:
      # Generate token
      token = self.lastfmHandler.request_auth_token()

      # Create browser dialog for user authentication
      self.browserDialog = QWebEngineView()
      self.browserDialog.setWindowTitle("Connect to Last.FM")
      self.browserDialog.setUrl(QtCore.QUrl("https://last.fm/api/auth/?api_key="
                                            + str(self.lastfmHandler.getAPIKey()) + "&token=" + str(token)))
      self.browserDialog.urlChanged.connect(self.lastfmHandler.request_session_key)
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
    self : instance
        Class instance.
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

    Parameters
    ----------
    self : instance
        Class instance.
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

  def browse_link_clicked(self, item):
    """
    Adds items relative to the clicked browse item, to the tree view.

    Parameters
    ----------
    self : instance
        Class instance.

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
    self : instance
        Class instance.
    list : str[]
        The input list of items for the model
    model : QStandardItemModel
        An empty model for QStandardItems
    """

    for item in list:
      item = QtGui.QStandardItem(item.title())
      model.appendRow(item)

  def generate_location_model(self, dict, model):
    """
    Takes an input dict of locations and an empty model, and fills said model.

    Parameters
    ----------
    self : instance
        Class instance.
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
    self : instance
        Class instance.
    index : int
        The index corresponding to the new type order
    """

    types = {}

    # Set the appropriate list and model relative to the
    # browsing model
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
    return

  def get_translation_uri(self):
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

  def retrieve_properties_subwindow(self, index, model):
    """
    Provides a properties view for a given performance.

    Parameters
    ----------
    self : instance
        Class instance.

    index : int
    """

    # Get labels dictionary for translation to human-readable formats
    labels = self.get_translation_uri()

    # Retrieve properties for this release
    properties = self.sparql.get_release_subproperties(index.data())

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
          model.itemFromIndex(index).setChild(i, labelItem)
          i += 1

          # Put children in a tree-esque format
          e = 0
          for property in treeViewPropertiesDict[key]:
            propertyItem = QtGui.QStandardItem(property)
            labelItem.setChild(e, propertyItem)
            e += 1

  def retrieve_release_info(self, release):
    properties = self.app.sparql.get_release_properties(release)
    #self.TreeViewProperties = QtWidgets.QTreeView(self.additionalInfoFrame)
    self.setParent(self.app.additionalInfoFrame)
    self.treePropertiesModel = QtGui.QStandardItemModel(self)
    self.fill_properties_tree_view(self.treePropertiesModel, properties)

    self.header().hide()
    self.setFixedHeight(800)
    self.setFixedWidth(400)

    # Set our model to the browsing list
    self.setModel(self.treePropertiesModel)
    self.doubleClicked.connect(lambda: self.retrieve_properties_subwindow(self.app.browseTreeView.currentIndex(),  self.treePropertiesModel))
    self.show()

  def fill_properties_tree_view(self, model, properties):
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
    treeViewPropertiesDict = {}
    for property in properties['results']['bindings']:
      if property['p']['value'] not in treeViewPropertiesDict:
        treeViewPropertiesDict[property['p']['value']] = []
      treeViewPropertiesDict[property['p']['value']].append(property['o']['value'])
    return treeViewPropertiesDict

class SearchHandler():
  def __init__(self, main):
    self.main = main

    # Create layout for search tab
    self.searchTabWidgetLayout = QtWidgets.QHBoxLayout()
    self.searchTabWidgetLayout.addWidget(self.main.searchTabWidget)
    self.main.searchTab.setLayout(self.searchTabWidgetLayout)

  def load_saved_search(self, index):
    for s in reversed(self.main.savedSearches):
      if index.data() == s[0]:
        self.setup_views(['timeline', 'map', 'table'], self.main.sparql.execute_string(s[1]))
        self.main.topMenuTabs.setCurrentIndex(2)
        return

  def add_search_tab_contents(self):
    # Add search there by default
    self.main.searchTabWidget.hide()

    # Create view
    self.view = view.View(self.main, {'results' : {'bindings' : []}}, ['map', 'timeline', 'table'], None, False, self.main.searchTabWidget)
    self.main.searchTab.layout().takeAt(0)
    self.main.searchTab.layout().addWidget(self.view.get_layout())

    # self.view.infoWindowWidgets
    # self.view = view.View(self.main, self, ['map', 'timeline', 'table'], self.main.mapHandler.get_on_this_day(), False, self.main.searchTabWidget)

  def add_custom_condition(self):
    # Each custom condition consists of groups of 3 widgets
    if self.main.advancedSearchLayout.count() == 0:
      count = 0
    else:
      count = self.main.advancedSearchLayout.count() / 3

    # Add to appropriate indexes our new row of widgets
    self.main.advancedSearchLayout.addWidget(self.generate_field_combo(), count + 1, 1, 1, 2)
    self.main.advancedSearchLayout.addWidget(self.generate_condition_combo(), count + 1, 2, 1, 2)
    self.main.advancedSearchLayout.addWidget(QtWidgets.QLineEdit(), count + 1, 3, 1, 2)

    # Add auto-completion where appropriate
    self.update_auto_complete()
  def remove_custom_condition(self):
    # Get 3 last items in the layout and remove them
    self.main.advancedSearchLayout.itemAt(self.main.advancedSearchLayout.count() - 1).widget().setParent(None)
    self.main.advancedSearchLayout.itemAt(self.main.advancedSearchLayout.count() - 1).widget().setParent(None)
    self.main.advancedSearchLayout.itemAt(self.main.advancedSearchLayout.count() - 1).widget().setParent(None)

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

    for i in range(0, self.main.advancedSearchLayout.count(), 3):
      self.main.advancedSearchLayout.itemAt(i + 2).widget().setCompleter(None)
      widgetText = self.main.advancedSearchLayout.itemAt(i).widget().currentText()
      textEditWidget = self.main.advancedSearchLayout.itemAt(i + 2).widget()

      if widgetText == 'Artist':
        textEditWidget.setCompleter(self.main.auto_comp(cache.load('artistList')))
      elif widgetText == 'Location':
        textEditWidget.setCompleter(self.main.auto_comp(cache.load('newReversedGroupedLocations')))
      elif widgetText == 'Genre':
        textEditWidget.setCompleter(self.main.auto_comp(cache.load('genreList')))

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
      filterString = """FILTER({0}="{1}") """.format(field_to_sparql[field], condition)
    elif operator == 'is not':
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
    for i in range(0, self.main.advancedSearchLayout.count(), 3):
      if len(self.main.advancedSearchLayout.itemAt(i + 2).widget().text()) > 0:
        customConditions.append(self.generate_advanced_search(self.main.advancedSearchLayout.itemAt(i).widget().currentText(),
                                                              self.main.advancedSearchLayout.itemAt(i + 1).widget().currentText(),
                                                              self.main.advancedSearchLayout.itemAt(i + 2).widget().text()))

    if 'OR' in self.main.matchingPolicyCombo.currentText():
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
    if len(self.main.locationRangeFilter.text()) > 0 and len(self.main.locationFilter.text()) > 0:
      locations = []

      # If p-to-p distance is within our range
      words = self.main.browseListHandler.locationList[self.main.locationFilter.text()]['latlng'].split()
      centerLat = radians(float(words[0]))
      centerLon = radians(float(words[1]))
      radius = 6373.0
      filter = ''

      # Find all locations within the range specified by the user
      for key, value in sorted(self.main.browseListHandler.locationList.items()):
        keyLat, keyLon = value['latlng'].split(' ')

        # Convert to floats from strings, then convert to radians
        keyLat = radians(float(keyLat))
        keyLon = radians(float(keyLon))

        # Calculate delta between pairs of lat / lngs
        deltaLon = keyLat - centerLon
        deltaLat = keyLon - centerLat

        # Perform point-to-point distance calculation
        a = sin(deltaLat / 2) ** 2 + cos(centerLat) * cos(centerLon) * sin(deltaLon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = radius * c

        # If location is within our distance radius
        if distance < float(self.main.locationRangeFilter.text()):
          self.prog.debugDialog.add_line("{0}: {1}".format(sys._getframe().f_code.co_name, str(key)
                                                           + ' by a distance of ' + str(float(self.main.locationRangeFilter.text()) - distance)))

          # Append all mapped locations for this key to our requested locations
          for location in value['locations']:
            locations.append(location)

      return locations
    # If only 1 location requested
    elif len(self.main.locationFilter.text()) > 0:
      # Return all mapped locations
      return self.main.browseListHandler.locationList[self.main.locationFilter.text()]['locations']
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
    artists = self.main.artistFilter.text()
    genres = self.main.genreFilter.text().lower()
    orderBy = self.main.orderByFilter.currentText()
    limit = self.main.numResultsSpinbox.value()
    venue = self.main.venueFilter.text()
    trackName = self.main.trackNameFilter.text()

    if len(self.main.countryFilter.text()) > 0:
      countries = self.get_mapped_countries(self.main.countryFilter.text())
    else:
      countries = ''

    # Custom search conditions
    if self.main.advancedSearchLayout.count() > 0:
      customSearchString = self.custom_search()
    else:
      customSearchString = ''

    # Generate SPARQL query
    query = self.main.sparql.perform_search(self.main.dateFrom.text(), self.main.dateTo.text(), artists, genres, locations, limit, trackName,
                                            countries, customSearchString, venue, orderBy)

    self.lastQueryExecuted = query

    # Execute SPARQL query
    results = self.main.sparql.execute_string(query)

    # Collect requested views
    requestedViews = []
    if self.main.mapViewChk.isChecked() : requestedViews.append('map')
    if self.main.timelineViewChk.isChecked() : requestedViews.append('timeline')
    if self.main.tableViewChk.isChecked() : requestedViews.append('table')

    # Create views
    self.setup_views(requestedViews, results)

  def setup_views(self, requestedViews, results):
    # Check for availability of CALMA data
    if 'calma' in results['head']['vars']:
      hasCalma = True
    else:
      hasCalma = False

    self.view = view.View(prog, self, requestedViews, results, hasCalma, self.main.searchTabWidget)
    removed = self.main.searchTab.layout().takeAt(0)
    self.main.searchTab.layout().addWidget(self.view.get_layout())
    self.view.infoWidget.setTabEnabled(1, True)

class BrowseTreeViewHandler():
  def __init__(self, main):
    self.main = main

  def tree_view_filter_update(self):
    """
    Provides filter functionality for the the tree view.

    Parameters
    ----------
    self : instance
        Class instance.
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
    except AttributeError as e:
      # If no model set, return
      return

  def expand_tree_item(self, index):
    """
    Expands a performance, adding its tracklist as children in the tree.

    Parameters
    ----------
    self : instance
        Class instance.
    index : QModelIndex
        The index in the treeview (i.e. the performance), clicked.
    """
    if self.main.treeViewModel.itemFromIndex(index).parent() == None:
      # Get name of selected item
      tracklist = self.main.sparql.get_tracklist(str(index.data()))
      preferredFormats = ['FLAC', 'VBR.MP3', 'SHN', 'OGG', 'WAV', '64.MP3']
      foundFormat = False
      formatIndex = 0

      while foundFormat == False and formatIndex < len(preferredFormats):
        if self.add_tracks_tree(self.main.formats[formatIndex], tracklist, index) != -1:
          foundFormat = True
          self.main.debugDialog.add_line('{0}: found matching format {1}'.format(sys._getframe().f_code.co_name, self.main.formats[formatIndex]))
        else:
          formatIndex += 1
      if foundFormat == False:
        self.main.debugDialog.add_line('{0}: failed to find matching format'.format(sys._getframe().f_code.co_name))
        self.main.debugDialog.add_line('{0}: tracklist for debugging: {1}'.format(sys._getframe().f_code.co_name), tracklist)
      else:
        self.main.browseTreeView.setModel(self.main.treeViewModel)

      self.main.browseTreeProperties.retrieve_release_info(index.data())

  def add_tracks_tree(self, extension_type, tracklist, index):
    """
    Adds a tracklist to the tree view.

    Parameters
    ----------
    self : instance
        Class instance.
    extension_type : str
        The requested format for the audio association.
    tracklist : dict
        The tracklist for the performance.
    index : QModelIndex
        The index in the treeview (i.e. the performance), clicked.
    """

    i = 0

    # For each item in tracklist
    for item in tracklist['results']['bindings']:

      # If desired extension matches a track
      if item['audio']['value'].lower().endswith(extension_type.lower()):

        # Add to treeView
        listItem = QtGui.QStandardItem(str(item['num']['value']) + '. ' + item['label']['value'])
        self.main.treeViewModel.itemFromIndex(index).setChild(i, listItem)

        # Store audio
        self.main.childrenFetched[listItem.text()] = str(item['audio']['value'])
        i += 1

    # If no tracks were added (i.e. the format provided failed)
    if i == 0:
      return -1
    else:
      return 1

  def play_tree_item(self, index):
    """
    Called when an item in the browse tab treeview is double-clicked, starting audio playback

    Parameters
    ----------
    self : instance
        Class instance.
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
      tracklist = self.main.sparql.get_tracklist(index.parent().data())
      self.main.debugDialog.add_line("{0}: retrieved tracklist for release {1}".format(sys._getframe().f_code.co_name, index.data()))
      audio = self.main.childrenFetched[index.data()]

      # Get correct extension
      audioList = self.main.audioHandler.extract_tracklist_single_format(tracklist)
      i = 0
      trackIndex = -1

      foundIndex = False
      v = -1
      for item in audioList:
        if not foundIndex:
          v += 1
          if item['audio']['value'] == audio:
            trackIndex = v
            foundIndex = True

            # Start process of playing audio
            self.main.audioHandler.user_audio_clicked(audioList, trackIndex)

    # Update icons
    self.main.audioHandler.isPlaying = True
    self.main.playPauseBtn.setIcon(qta.icon('fa.pause'))

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
    self.resultsTable = QtWidgets.QTableWidget(self.widget)

  def on_table_scroll(self, value):
    """
    Starts a new thread for replacing URIs with location labels.

    Parameters
    ----------
    self : instance
        Class instance.
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
    self : instance
        Class instance.
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
      return

  def update_table_item(self, row, col, text):
    """
    Updates a particular table item.

    This function is mainly used for replacing URIs with human-readable labels.

    Parameters
    ----------
    self : instance
        Class instance.
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

    Parameters
    ----------
    self : instance
        Class instance.
    """
    return self.widget

  def get_table(self):
    """
    Returns the table element instance.

    Parameters
    ----------
    self : instance
        Class instance.
    """
    return self.resultsTable

  def fill_table(self, results):
    """
    Starts a thread to fill the table with the data returned from a search.

    Parameters
    ----------
    self : instance
        Class instance.
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
    self : instance
        Class instance.
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

  def generate_table_start(self, c, col, columnNames):
    """
    Adds an item to the table view.

    Parameters
    ----------
    self : instance
        Class instance.
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
    header.setStretchLastSection(True)
    vHeader = self.resultsTable.verticalHeader()
    vHeader.setVisible(False)

    self.prog.debugDialog.add_line("{0}: set initial table properties".format(sys._getframe().f_code.co_name))

  def generate_table_end(self):
    """
    Perform post-processing on table after all the data has been entered.

    Parameters
    ----------
    self : instance
        Class instance.
    """

    # Set final properties for the table
    self.resultsTable.setVisible(False)
    self.resultsTable.resizeColumnsToContents()
    self.resultsTable.setVisible(True)
    self.resultsTable.setSortingEnabled(True)
    self.resultsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    self.resultsTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
    self.resultsTable.itemDoubleClicked.connect(self.search_table_clicked)
    self.resultsTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    # Add focus signal handlers
    self.resultsTable.itemClicked.connect(self.prog.searchHandler.view.move_focus)
    self.resultsTable.verticalScrollBar().valueChanged.connect(self.on_table_scroll)

    # Get first 5 URI replacements
    self.on_table_scroll(0)

    # Add widget to the data view
    self.resultsTable.setParent(self.widget)
    self.layout.addWidget(self.resultsTable, 0, 0, 1, 1)

    self.set_location_width()
    self.prog.debugDialog.add_line("{0}: set final table properties".format(sys._getframe().f_code.co_name))
    self.widget.show()

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
          if self.resultsTable.horizontalHeaderItem(c).text() == 'Label':
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
    for property in properties['results']['bindings']:
      if property['p']['value'] == "http://www.w3.org/2004/02/skos/core#prefLabel":
        label = property['o']['value']

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

  def get_on_this_day(self):
    homePageSPARQL = """PREFIX etree:<http://etree.linkedmusic.org/vocab/>
                        PREFIX mo:<http://purl.org/ontology/mo/>
                        PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
                        PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
                        PREFIX timeline:<http://purl.org/NET/c4dm/timeline.owl#>
                        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                        SELECT DISTINCT ?performer ?name ?label  ?place  ?date  WHERE 
                        {    
                              ?art skos:prefLabel ?label.  
                              ?art event:place ?location. 
                              ?location etree:location ?place.
                              ?performer foaf:name ?name. 
                              ?art etree:date ?date.
                              ?art mo:performer ?performer.
                              FILTER (regex(?date,'""" + time.strftime('-%m-%d') + """',
                              'i'))
                        }  GROUP BY (?prefLabel) LIMIT 100"""

    homepageResults = self.prog.sparql.execute_string(homePageSPARQL)
    return homepageResults

  def add_search_results_map(self, results):
    if results is not None:
      worker = multithreading.WorkerThread(self.mapsClass.homepage_add, results)
      worker.qt_signals.js_callback.connect(self.add_point)
      worker.qt_signals.homepage_end.connect(self.end_data_processing)
      worker.qt_signals.homepage_start.connect(self.start_data_processing)
      self.prog.threadpool.start(worker)

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
    # Update various GUI elements
    self.update_playlist_view()

  def get_image(self, artist):
    return

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

class TimelineHandler():
  def __init__(self, webEngine, main):
    self.main = main
    self.webEngine = webEngine

  def add_points(self, results):
    i = 1
    for result in results['results']['bindings']:
      self.webEngine.page().runJavaScript("""addPoint(`{0}`,`{1}`,`{2}`)""".format(i, result['label']['value'], result['date']['value']))
      i += 1

    self.webEngine.page().runJavaScript("""addTimeline()""")

# Python-side call handler for communicating between audio player / map and python
class CallHandler(QtCore.QObject):
  @QtCore.pyqtSlot(str)
  def mapLinkClicked(self, link):
    tracklist = sparql.getTracklist(link)
    prog.user_audio_clicked(tracklist, 0)

  @QtCore.pyqtSlot(str, str)
  def map_tracklist_popup(self, link, label):
    print("{0}, {1}".format(link, label))

    prog.searchHandler.view.move_focus(label)
    popup = "<bold>{0}</bold><br>".format(label)

    # Get venue information for this arg
    geoInfo = prog.sparql.get_venue_information(label)
    if geoInfo['lastfm'] is not None:
      print(geoInfo['lastfm'])
      popup += geoInfo['lastfm'] # prog.lastfmHandler.get_venue_info(geoInfo['lastfm'])
    else:
      popup += "\n {0}".format("<b> Last.FM data unavailable.")

    if geoInfo['geoname'] is not None:
      id = geoInfo['geoname'][geoInfo['geoname'].rfind('/') + 1:]
      popup += "\n {0}".format(self.generate_geoname_html(id))
    else:
      popup += "\n {0}".format("GeoNames data unavailable.")
    prog.searchHandler.view.mapSearchDialog.page().runJavaScript("setPopup({0},`{1}`)".format(link, popup))

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
      message = 'A HTTP error occurred, this could be due to the SPARQL end-point being unavailable'
    else:
      print('Error dialog recieved non-mapped error: {0}'.format(type(exception).__name__))
      message = str(Exception)
    self.setWindowTitle('Error')
    self.showMessage(message)
    self.show()

if __name__ == '__main__':
  # Create QApplication instance
  app = QtWidgets.QApplication(sys.argv)

  # Create dialog to show this instance
  dialog = QtWidgets.QMainWindow()

  # Start main event loop
  prog = mainWindow(dialog)

  # Show the main dialog window to user
  dialog.show()

  # On user exit, stop the application
  sys.exit(app.exec_())
