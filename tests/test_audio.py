from unittest import TestCase
import audio
import alsaaudio
import pytest
import sparql
from PyQt5 import QtWidgets, QtCore
import application
import multithreading
import time
import qtawesome
import mock

class SignalStubs(QtCore.QObject):
  update_track_progress = QtCore.pyqtSignal(int)
  track_finished = QtCore.pyqtSignal()
  update_track_duration = QtCore.pyqtSignal(float)
  scrobble_track = QtCore.pyqtSignal()

  def __init__(self, parent=None):
    super().__init__()
    self.update_track_progress.connect(self.audio_success)
    self.track_finished.connect(self.signal_slot_stub)
    self.update_track_duration.connect(self.signal_slot_stub)
    self.scrobble_track.connect(self.signal_slot_stub)
    self.kwargs = {'update_track_progress': self.update_track_progress,
            'track_finished': self.track_finished,
            'update_track_duration': self.update_track_duration,
            'scrobble_track' : self.scrobble_track,
            'seek' : 0,
            'test' : True}
    self.startedPlaying = False

  def signal_slot_stub(self):
    return

  def audio_success(self):
    self.startedPlaying = True
    print('hit {0}'.format(self.startedPlaying))

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

class TestAudio():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    self.signalStubs = SignalStubs()
    self.applicationStubs = ApplicationStub()
    self.audioInstance = audio.Audio(self.applicationStubs)

    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

  def fake_audio_thread(self, arg):
    return

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

  @mock.patch('audio.Audio.ffmpeg_pipeline')
  def test_set_seek_success(self, arg):
    self.audioInstance.currentUrl = 'http://link.com/'
    assert(self.audioInstance.set_seek(15) == True)

  def test_extract_tracklist_single_format(self):
    sparqlHandler = sparql.SPARQL()
    tracklist = sparqlHandler.get_tracklist("Bad Label")
    audioList = self.audioInstance.extract_tracklist_single_format(tracklist)
    assert(len(audioList) == 0)

    tracklist = sparqlHandler.get_tracklist("Mogwai Live at The Forum on 1999-10-16")
    audioList = self.audioInstance.extract_tracklist_single_format(tracklist)
    assert(len(audioList) > 0)

  def test_ffmpeg_pipeline(self):
    url = "http://archive.org/download/abird1998-05-01/abird1998-05-01t13_vbr.mp3"
    startTime = time.time()

    self.prog.audioHandler.ffmpeg_pipeline(url, **self.signalStubs.kwargs)
    # worker = multithreading.WorkerThread(self.prog.audioHandler.ffmpeg_pipeline, url, seek=0)
    # worker.qtSignals.track_finished.connect(self.signalStubs.signal_slot_stub)
    # worker.qtSignals.update_track_progress.connect(self.signalStubs.audio_success)
    # worker.qtSignals.update_track_duration.connect(self.signalStubs.signal_slot_stub)
    # worker.qtSignals.scrobble_track.connect(self.signalStubs.signal_slot_stub)
    # self.prog.audioThreadpool.start(worker)

    while (time.time() - startTime < 15):
      if self.prog.audioHandler.isPlaying == True:
        self.prog.audioHandler.kill_audio_thread()

    if not self.prog.audioHandler.isPlaying:
      pytest.fail()

    # How to make it stop after successfully starts playing?

  def test_update_seekbar(self, qtbot):
    self.prog.audioHandler.duration = 350.00
    self.prog.audioHandler.update_seekbar(0)
    assert(self.prog.timeLbl.text() == "0:00 / 5:50")

    self.prog.audioHandler.update_seekbar(60)
    assert(self.prog.timeLbl.text() == "1:00 / 5:50")

    self.prog.audioHandler.duration = 60
    self.prog.audioHandler.update_seekbar(20)
    assert(self.prog.timeLbl.text() == "0:20 / 1:00")

  # def test_start_audio_thread(self):
  #   pytest.fail()

  def test_get_next_track_index(self):
    self.prog.audioHandler.playlist_index = 0
    self.prog.audioHandler.playlist = [['url', 'label'], ['url two', 'label 2']]

    # Repeat all
    index = self.prog.audioHandler.get_next_track_index()
    assert(index == 1)

    # Shuffle
    self.prog.repeatCombo.setCurrentIndex(2)
    index = self.prog.audioHandler.get_next_track_index()
    assert(index >= 0)
    assert(index <= len(self.prog.audioHandler.playlist))

  def test_play_pause(self):
    self.prog.audioHandler.isPlaying = True
    self.prog.audioHandler.play_pause()
    # assert(self.prog.playPauseBtn.icon() == QtGui.QIcon qtawesome.icon('fa.play'))
    assert(self.prog.audioHandler.isPlaying == False)

    # self.prog.audioHandler.isPlaying = False
    # self.prog.audioHandler.play_pause()
    # assert (self.prog.playPauseBtn.icon() == qtawesome.icon('fa.play'))

  def test_start_audio_single_link(self):
    self.prog.audioHandler.start_audio_single_link("http://url", 0, test=True)
    assert(self.prog.trackLbl.text() == "Track Name")
    assert(self.prog.audioHandler.isPlaying == True)

  @mock.patch('audio.Audio.fetch_next_track')
  def test_previous_click_positive(self, arg):
    self.prog.audioHandler.playlist_index = 3
    self.prog.audioHandler.previous_click()
    assert(self.prog.audioHandler.playlist_index == 1)

  @mock.patch('audio.Audio.start_audio_thread')
  def test_next_click(self, arg):
    self.prog.audioHandler.playlist_index = 0
    self.prog.audioHandler.playlist = [['http', 'title'], ['http','title']]
    self.prog.audioHandler.next_click()
    assert(self.prog.audioHandler.playlist_index == 1)

  @mock.patch('audio.Audio.start_audio_thread', side_effect=fake_audio_thread)
  def test_user_audio_clicked(self, arg):

    audioList = [{'audio': {'type': 'uri', 'value': 'http://archive.org/download/3df2008-01-10.The_Red_Square_Albany/3df2008-01-10t01.flac'},
                  'label': {'type': 'literal', 'value': 'ooh ooh'},
                  'num': {'type': 'typed-literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'value': '1'},
                  'tracklist': {'type': 'uri', 'value': 'http://etree.linkedmusic.org/track/3df2008-01-10.The_Red_Square_Albany-1'},
                  'name': {'type': 'literal', 'value': '3 Dimensional Figures'}}
                 ]

    self.prog.audioHandler.user_audio_clicked(audioList, 0)
    assert (self.prog.audioHandler.isPlaying == True)

  @mock.patch('audio.Audio.start_audio_thread', side_effect=fake_audio_thread)
  def test_fetch_next_track(self, arg):
    audioList = [{'audio': {'type': 'uri', 'value': 'http://archive.org/download/3df2008-01-10.The_Red_Square_Albany/3df2008-01-10t01.flac'},
                  'label': {'type': 'literal', 'value': 'ooh ooh'},
                  'num': {'type': 'typed-literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'value': '1'},
                  'tracklist': {'type': 'uri', 'value': 'http://etree.linkedmusic.org/track/3df2008-01-10.The_Red_Square_Albany-1'},
                  'name': {'type': 'literal', 'value': '3 Dimensional Figures'}},
                 {'audio': {'type': 'uri', 'value': 'http://archive.org/download/3df2008-01-10.The_Red_Square_Albany/3df2008-01-10t01.flac'},
                  'label': {'type': 'literal', 'value': 'ooh ooh'},
                  'num': {'type': 'typed-literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'value': '1'},
                  'tracklist': {'type': 'uri', 'value': 'http://etree.linkedmusic.org/track/3df2008-01-10.The_Red_Square_Albany-1'},
                  'name': {'type': 'literal', 'value': '3 Dimensional Figures'}}
                 ]

    self.prog.audioHandler.user_audio_clicked(audioList, 0)
    self.prog.audioHandler.fetch_next_track()
    assert (self.prog.audioHandler.playlist_index == 1)

  @mock.patch('audio.Audio.fetch_next_track')
  def test_previous_click_negative(self, arg):
    self.prog.audioHandler.playlist_index = 0
    self.prog.audioHandler.previous_click()
    assert(self.prog.audioHandler.playlist_index == -1)

  @mock.patch('audio.Audio.start_audio_thread')
  def test_track_seek(self, arg):
    self.prog.audioHandler.track_seek()
    assert(self.prog.audioHandler.userDragging == False)

  def test_lock_progress_user_drag(self):
    self.prog.audioHandler.lock_progress_user_drag()
    assert(self.prog.audioHandler.userDragging == True)

  def test_send_duration(self):
    self.prog.audioHandler.send_duration(100)
    assert (self.prog.trackProgress.maximum() == 100)
    assert (self.prog.audioHandler.duration == 100)
