from unittest import TestCase
import os
import mock
import pytest
from PyQt5 import QtWidgets
import application
import audio


class TestApplication():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)


