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

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

  def test_update_playlist_view(self):
    pytest.fail()

  @mock.patch('application.NowPlaying.update_playlist_view')
  @mock.patch('application.NowPlaying.update_lastfm_tags')
  @mock.patch('application.NowPlaying.update_similar_artists')
  def test_update_now_playing_view(self, updatePlaylistViewMock, lastFMTagsMock, similarArtistMocks):
    self.prog.nowPlayingHandler.update_now_playing_view()
    assert(updatePlaylistViewMock.called)
    assert(lastFMTagsMock.called)
    assert(similarArtistMocks.called)

  # @mock.patch('lastfm.lastfmAPI.get_similar_artists')
  def test_update_similar_artists(self):
    assert(self.prog.similarArtistsList.count() == 0)
    self.prog.nowPlayingHandler.update_similar_artists('Grateful Dead')
    assert(self.prog.similarArtistsList.count() > 0)

    self.prog.nowPlayingHandler.update_similar_artists('Completely Made Up Artist Not In Last.FM')
    assert(self.prog.similarArtistsList.count() == 0)

  # @mock.patch('lastfm.lastfmAPI.get_tags_for_artist')
  def test_update_lastfm_tags(self):
    assert(self.prog.similarArtistsList.count() == 0)
    self.prog.nowPlayingHandler.update_lastfm_tags('Grateful Dead')
    assert(self.prog.similarArtistsList.count() > 0)

    self.prog.nowPlayingHandler.update_lastfm_tags('Completely Made Up Artist Not In Last.FM')
    assert(self.prog.similarArtistsList.count() == 0)
