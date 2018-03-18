from unittest import TestCase
import pytest
import lastfm
from PyQt5 import QtWidgets, QtCore
import application
import mock

class TestNowPlaying():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()
    qtbot.add_widget(self.dialog)

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

  def test_update_playlist_view(self):
    self.prog.audioHandler.playlist =  [['http://archive.org/download/3df2008-01-10.The_Red_Square_Albany/3df2008-01-10t01.flac',
                                         'ooh ooh',
                                         'http://etree.linkedmusic.org/track/3df2008-01-10.The_Red_Square_Albany-1'],
                                         ['http://archive.org/download/3df2008-01-10.The_Red_Square_Albany/3df2008-01-10t05.flac',
                                          'in/the beginning -> bweep',
                                          'http://etree.linkedmusic.org/track/3df2008-01-10.The_Red_Square_Albany-5'],
                                          ['http://archive.org/download/3df2008-01-10.The_Red_Square_Albany/3df2008-01-10t06.flac',
                                          'the electrioc soil',
                                          'http://etree.linkedmusic.org/track/3df2008-01-10.The_Red_Square_Albany-6'],
                                          ['http://archive.org/download/3df2008-01-10.The_Red_Square_Albany/3df2008-01-10t07.flac',
                                          'curry', 'http://etree.linkedmusic.org/track/3df2008-01-10.The_Red_Square_Albany-7']]

    self.prog.audioHandler.playlist_index = 0
    self.prog.nowPlayingHandler.update_playlist_view()
    assert(self.prog.playlist_view.model().rowCount() == 4)

  @mock.patch('application.NowPlaying.update_playlist_view')
  @mock.patch('application.NowPlaying.update_lastfm_tags')
  @mock.patch('application.NowPlaying.update_similar_artists')
  def test_update_now_playing_view(self, updatePlaylistViewMock, lastFMTagsMock, similarArtistMocks):
    self.prog.audioHandler.playlist =  [['http://archive.org/download/3df2008-01-10.The_Red_Square_Albany/3df2008-01-10t01.flac',
                                         'ooh ooh',
                                         'http://etree.linkedmusic.org/track/3df2008-01-10.The_Red_Square_Albany-1'],
                                         ['http://archive.org/download/3df2008-01-10.The_Red_Square_Albany/3df2008-01-10t05.flac',
                                          'in/the beginning -> bweep',
                                          'http://etree.linkedmusic.org/track/3df2008-01-10.The_Red_Square_Albany-5'],
                                          ['http://archive.org/download/3df2008-01-10.The_Red_Square_Albany/3df2008-01-10t06.flac',
                                          'the electrioc soil',
                                          'http://etree.linkedmusic.org/track/3df2008-01-10.The_Red_Square_Albany-6'],
                                          ['http://archive.org/download/3df2008-01-10.The_Red_Square_Albany/3df2008-01-10t07.flac',
                                          'curry', 'http://etree.linkedmusic.org/track/3df2008-01-10.The_Red_Square_Albany-7']]

    self.prog.audioHandler.playlist_index = 0
    self.prog.nowPlayingHandler.update_now_playing_view()
    assert(updatePlaylistViewMock.called)
    assert(lastFMTagsMock.called)
    assert(similarArtistMocks.called)

  def test_update_similar_artists(self):
    assert(self.prog.similarArtistsList.count() == 0)
    self.prog.nowPlayingHandler.update_similar_artists('Grateful Dead')
    assert(self.prog.similarArtistsList.count() > 0)

    self.prog.nowPlayingHandler.update_similar_artists('Completely Made Up Artist Not In Last.FM')
    assert(self.prog.similarArtistsList.count() == 0)

  # @mock.patch('lastfm.lastfmAPI.get_tags_for_artist')
  def test_update_lastfm_tags(self):
    assert(self.prog.artistTagsList.count() == 0)
    self.prog.nowPlayingHandler.update_lastfm_tags('Grateful Dead')
    assert(self.prog.artistTagsList.count() > 0)

    self.prog.nowPlayingHandler.update_lastfm_tags('Completely Made Up Artist Not In Last.FM')
    assert(self.prog.artistTagsList.count() == 0)
