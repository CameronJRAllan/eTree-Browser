from unittest import TestCase
import pytest
import application
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from unittest import TestCase
import search
import mock
import view

class TestSearchHandlerQt():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()
    qtbot.add_widget(self.dialog)

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

    # Search handler
    self.callHandler = application.CallHandler(self.prog)

  def test_generate_geoname_html(self):
    html = self.callHandler.generate_geoname_html(4709090)
    toBeIncluded = ['Location', 'Latitude', 'Longitude', 'Timezone', 'geoNamesBounds']
    for i in toBeIncluded:
      assert(i in html)

  @mock.patch('view.View.move_focus')
  def test_map_tracklist_popup(self, moveFocus):
    self.callHandler.map_tracklist_popup(3,"Acoustic Syndicate Live at Boulder Theatre on 2002-01-25")

    assert(moveFocus.called)

