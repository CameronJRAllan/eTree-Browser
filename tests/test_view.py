from unittest import TestCase
import pytest
import application
import sys
from PyQt5 import QtWidgets, QtCore
from unittest import TestCase
import view
class TetViewQt():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

    # Search handler
    self.view = view.View(self.prog, {'results' : {'bindings' : []}}, ['map', 'timeline', 'table'], None, False, self.main.searchTabWidget)

  def test_save_search(self):
    pytest.fail()

  def test_change_proportions(self):
    pytest.fail()
