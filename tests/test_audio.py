from unittest import TestCase
import audio
import alsaaudio
import pytest
from PyQt5 import QtCore
from pytestqt import qtbot
import sparql

class SignalStubs(QtCore.QObject):
  update_track_progress = QtCore.pyqtSignal(int)
  track_finished = QtCore.pyqtSignal()
  update_track_duration = QtCore.pyqtSignal(float)
  scrobble_track = QtCore.pyqtSignal()

  def __init__(self, parent=None):
    super().__init__()
    self.update_track_progress.connect(self.signal_slot_stub)
    self.track_finished.connect(self.signal_slot_stub)
    self.update_track_duration.connect(self.signal_slot_stub)
    self.scrobble_track.connect(self.signal_slot_stub)
    self.kwargs = {'update_track_progress': self.update_track_progress,
            'track_finished': self.track_finished,
            'update_track_duration': self.update_track_duration,
            'seek': 0,
            'scrobble_track' : self.scrobble_track}

  def signal_slot_stub(self):
    return

  def signal_update_progress(self):
    self.hasReadChunk = True

class ApplicationStub():
  def __init__(self, parent=None):
    self.thread_flag = True
    self.formats = ['flac', 'vbr.mp3', 'shn']

  def set_thread_flag(self, flag):
    self.thread_flag = flag

  class debugDialog():
    def add_line(self):
      return

class TestAudio(TestCase):
  @pytest.fixture(scope="function", autouse=True)
  def setup(self):
    self.signalStubs = SignalStubs()
    self.applicationStubs = ApplicationStub()
    self.audioInstance = audio.Audio(self.applicationStubs)

  # def test_ffmpeg_pipeline(self):
  #   # Set-up key-word arguments
  #   url = 'http://archive.org/download/dbt2004-05-08.4011s.flac16/dbt2004-05-08d1t02.flac'
  #   self.audioInstance.ffmpeg_pipeline(url, **self.signalStubs.kwargs)

  def test_get_url(self):
    assert(self.audioInstance.get_url() == None)

  def test_change_play_state(self):
    # Changing the play state with no stream should not change the is_playing flag
    assert(self.audioInstance.isPlaying == False)
    self.audioInstance.change_play_state()
    assert(self.audioInstance.isPlaying == False)

  def test_set_volume(self):
    nameOfMixer = alsaaudio.mixers()[0]

    assert(self.audioInstance.set_volume(0) == True)
    mixer = alsaaudio.Mixer(nameOfMixer)
    assert(mixer.getvolume() == [0,0])

    assert(self.audioInstance.set_volume(25) == True)
    mixer = alsaaudio.Mixer(nameOfMixer)
    assert(mixer.getvolume() == [25,25])

    assert(self.audioInstance.set_volume(50) == True)
    mixer = alsaaudio.Mixer(nameOfMixer)
    assert(mixer.getvolume() == [50,50])

    assert(self.audioInstance.set_volume(100) == True)
    mixer = alsaaudio.Mixer(nameOfMixer)
    assert(mixer.getvolume() == [100,100])

    assert(self.audioInstance.set_volume(101) == False)
    mixer = alsaaudio.Mixer(nameOfMixer)
    assert(mixer.getvolume() == [100,100])

    assert(self.audioInstance.set_volume(-1) == False)
    mixer = alsaaudio.Mixer(nameOfMixer)
    assert(mixer.getvolume() == [100,100])

    # To prevent my ears from being blasted after running the test suite
    assert(self.audioInstance.set_volume(35) == True)

  def test_set_seek(self):
    # Assert failure when no current URL set
    assert(self.audioInstance.set_seek(15) == False)

    # Set URL and now ensure is set correctly

  def test_extract_tracklist_single_format(self):
    sparqlHandler = sparql.SPARQL()
    tracklist = sparqlHandler.get_tracklist("Bad Label")
    audioList = self.audioInstance.extract_tracklist_single_format(tracklist)
    assert(len(audioList) == 0)

    tracklist = sparqlHandler.get_tracklist("Mogwai Live at The Forum on 1999-10-16")
    audioList = self.audioInstance.extract_tracklist_single_format(tracklist)
    assert(len(audioList) > 0)
