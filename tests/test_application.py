import sys
import pytest
import application
from PyQt5 import QtWidgets, QtGui, QtCore
import alsaaudio
import mock
import export
import lastfm
from PyQt5.QtWebEngineWidgets import QWebEngineView

# NOTE TO THE READER
# These tests are designed in mind to be run with Py.Test, the IDE used during programming was PyCharm
class TestApplication():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

  def test_volumeSlider(self):
    # Check default value
    assert(self.prog.volumeSlider.value() == 50)

    # Set value
    self.prog.volumeSlider.setValue(60)
    nameOfMixer = alsaaudio.mixers()[0]
    mixer = alsaaudio.Mixer(nameOfMixer)
    assert(mixer.getvolume() == [60,60])

    # Check lower bound
    self.prog.volumeSlider.setValue(-1)
    nameOfMixer = alsaaudio.mixers()[0]
    mixer = alsaaudio.Mixer(nameOfMixer)
    assert(mixer.getvolume() == [0,0])

    # Check upper bound
    self.prog.volumeSlider.setValue(101)
    nameOfMixer = alsaaudio.mixers()[0]
    mixer = alsaaudio.Mixer(nameOfMixer)
    assert(mixer.getvolume() == [99,99])

    self.prog.volumeSlider.setValue(50)

  def test_music_player_icons(self):
    # Check all music player buttons have icons
    assert isinstance(self.prog.playPauseBtn.icon(), QtGui.QIcon)
    assert isinstance(self.prog.prevBtn.icon(), QtGui.QIcon)
    assert isinstance(self.prog.nextBtn.icon(), QtGui.QIcon)
    assert isinstance(self.prog.lastfmBtn.icon(), QtGui.QIcon)

  def test_kill_audio_thread(self):
    # No flag should exist before any threads created
    with pytest.raises(AttributeError):
      self.prog.thread_flag

  def test_initialize_web_channel(self):
    try:
      self.prog.mapChannel
      self.prog.mapHandler
    except NameError as e:
      self.fail()

  def test_debug_window_state_changed(self):
    assert(self.prog.debugDialog.isHidden() == True)

    self.prog.debug_window_state_changed(1)

    assert(self.prog.debugDialog.isHidden() == True)

    self.prog.debug_window_state_changed(2)

    assert(self.prog.debugDialog.isHidden() == False)

    # Hide after testing
    self.prog.debugDialog.hide()

  def test_send_duration(self):
    self.prog.audioHandler.send_duration(0)
    assert(self.prog.trackProgress.maximum() == 0)
    assert(self.prog.audioHandler.duration == 0)

    self.prog.audioHandler.send_duration(25)
    assert(self.prog.trackProgress.maximum() == 25)
    assert(self.prog.audioHandler.duration == 25)

    self.prog.audioHandler.send_duration(156)
    assert(self.prog.trackProgress.maximum() == 156)
    assert(self.prog.audioHandler.duration == 156)

  def test_preferred_format_changed(self):
    self.prog.preferred_format_changed('FLAC')
    assert(self.prog.formats[0] == 'FLAC')

    self.prog.preferred_format_changed('SHN')
    assert(self.prog.formats[0] == 'SHN')

    self.prog.preferred_format_changed('OGG')
    assert(self.prog.formats[0] == 'OGG')

  def test_change_type(self):
    self.prog.browseListHandler.change_type(0)
    assert (self.prog.browseList.model() == self.prog.browseListHandler.artistListModel)

  def test_auto_comp(self):
    autoComp = self.prog.auto_comp(['Item 1', 'Item 2', 'Item 3'])
    assert(isinstance(autoComp, QtWidgets.QCompleter))
    assert(autoComp.caseSensitivity() == QtCore.Qt.CaseInsensitive)

  def test_clickable(self):
    clickable = self.prog.clickable(QtWidgets.QWidget())
    assert(isinstance(clickable, QtCore.pyqtBoundSignal))

  def test_quickfilter(self, qtbot):
    assert (self.prog.treeViewFilter.text() == "")
    qtbot.keyClicks(self.prog.quickFilter, "Test")
    assert (self.prog.quickFilter.text() == "Test")

  def test_open_tree_menu(self, qtbot):
    qtbot.addWidget(self.prog.quickFilter)
    qtbot.addWidget(self.prog.browseList)
    qtbot.keyClicks(self.prog.quickFilter, "3 Dimensional Figures")
    self.prog.browseListHandler.browse_link_clicked(self.prog.browseList.model().index(0, 0))
    self.prog.browseTreeView.setCurrentIndex(self.prog.browseTreeView.model().index(0, 0))

    try:
      self.prog.open_tree_menu(QtCore.QPoint(1,0))
      assert(isinstance(self.prog.menu, QtWidgets.QMenu))
      self.prog.menu.close()
    except Exception as e:
      pytest.fail()

  @mock.patch('export.Export.export_data')
  def test_tree_browse_menu_click(self, arg):
    item = QtGui.QStandardItem('Collapse')
    self.prog.menu_on_item = QtCore.QPoint(1,0)
    self.prog.tree_browse_menu_click(QtWidgets.QAction("JSON"))
    self.prog.tree_browse_menu_click(QtWidgets.QAction("CSV"))
    self.prog.tree_browse_menu_click(QtWidgets.QAction("M3U"))
    self.prog.tree_browse_menu_click(QtWidgets.QAction("XML"))

  @mock.patch('lastfm.lastfmAPI.logout')
  def test_lastfm_deauthenticate(self, arg):
    self.prog.lastfm_deauthenticate()
    assert(self.prog.lastfmBtn.styleSheet() == '')
    assert(self.prog.lastfmStatus.text() == 'Connect to Last.FM')

  def test_change_type_order_ZA_locations(self):
    self.prog.typeBrowseCombo.setCurrentIndex(2)
    self.prog.typeOrderByCombo.setCurrentIndex(1)

    assert(self.prog.typeBrowseCombo.currentText() == 'Location')
    assert(self.prog.typeOrderByCombo.currentText() == 'Desc')

  def test_retrieve_properties_subwindow(self):

    # Set-up initial release data
    self.prog.browseTreeProperties.retrieve_release_info("3 Dimensional Figures Live at The Red Square on 2008-01-10")

    asserted = False

    for i in range(1,self.prog.browseTreeProperties.model().rowCount()):
      if self.prog.browseTreeProperties.model().index(i, 0).data() == 'Has Sub Event':
        index = self.prog.browseTreeProperties.model().index(i, 0).child(0, 0)

        self.prog.browseTreeProperties.retrieve_properties_subwindow(index)
        assert(self.prog.browseTreeProperties.model().index(i, 0).child(0, 0).data() == 'ooh ooh')
        asserted = True

    if not asserted : pytest.fail()

  def test_add_tracks_audiolist(self):
    # Get release data
    release = self.prog.sparql.get_tracklist_grouped("Mogwai Live at The Forum on 1999-10-16")

    # Call function and check values returned
    audioList = self.prog.treeViewHandler.add_tracks_audiolist(release['results']['bindings'], 0, '.flac')

    assert(type(audioList) == type([]))
    assert(len(audioList) == 11)

  def test_get_track_index_and_format(self):
    # Get release data
    release = self.prog.sparql.get_tracklist_grouped("Mogwai Live at The Forum on 1999-10-16")
    self.model = QtGui.QStandardItemModel()
    self.item = QtGui.QStandardItem("4. Summer.")
    self.model.appendRow(self.item)
    trackIndex, prefFormat = self.prog.treeViewHandler.get_track_index_and_format(self.model.index(0, 0), release['results']['bindings'])

    assert(trackIndex == 4)
    assert(prefFormat == '.flac')

  def test_check_lastfm_status_has_session(self):
    self.prog.lastfmHandler.sessionKey = 'STUBKEY'
    self.prog.check_lastfm_status()
    assert(self.prog.lastfmBtn.styleSheet() == """QPushButton {
                                      background-color: #BA2024;
                                    }""")

  def test_check_lastfm_status_no_session(self):
    self.prog.lastfmHandler.sessionKey = None
    self.prog.check_lastfm_status()
    assert(isinstance(self.prog.browserDialog, QWebEngineView))
    self.prog.browserDialog.hide()

  @mock.patch('lastfm.lastfmAPI.update_now_playing')
  def test_scrobble_track_lastfm(self, nowPlaying):
    self.prog.audioHandler.playlist = ['http://archive.org/download/3df2008-01-10.The_Red_Square_Albany/3df2008-01-10t02.flac',
                                       'reverb',
                                       'http://etree.linkedmusic.org/track/3df2008-01-10.The_Red_Square_Albany-2']
    self.prog.audioHandler.playlist_index = 0
    self.prog.scrobble_track_lastfm()
    assert(nowPlaying)