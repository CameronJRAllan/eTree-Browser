import sys
import pytest
import application
from PyQt5 import QtWidgets, QtGui, QtCore
import alsaaudio

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

      #
    # self.prog.change_type(1)
    # assert (self.prog.browseList.model() == self.prog.genreListModel)
    #
    # self.prog.change_type(2)
    # assert (self.prog.browseList.model() == self.prog.locationListModel)

