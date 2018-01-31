from unittest import TestCase
import os
import mock
import pytest
from PyQt5 import QtWidgets
import application
import audio

def fake_audio_thread(self, arg):
  return

class TestApplication():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

  @mock.patch('audio.Audio.start_audio_thread', side_effect=fake_audio_thread)
  def test_user_audio_clicked(self, arg):

    audioList = [{'audio': {'type': 'uri', 'value': 'http://archive.org/download/3df2008-01-10.The_Red_Square_Albany/3df2008-01-10t01.flac'},
                       'label': {'type': 'literal', 'value': 'ooh ooh'},
                       'num': {'type': 'typed-literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'value': '1'},
                       'tracklist': {'type': 'uri', 'value': 'http://etree.linkedmusic.org/track/3df2008-01-10.The_Red_Square_Albany-1'},
                       'name': {'type': 'literal', 'value': '3 Dimensional Figures'}}
                      ]

    self.prog.audioHandler.user_audio_clicked(audioList, 0)
    assert(self.prog.audioHandler.isPlaying == True)

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
    assert(self.prog.audioHandler.playlist_index == 1)
