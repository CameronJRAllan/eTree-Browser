from unittest import TestCase
import pytest
import application
import sys
from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)

class TestSearchHandler(TestCase):
  @pytest.fixture(scope="function", autouse=True)
  def setup(self):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

    # Search handler
    self.searchHandler = application.SearchHandler(self.prog)

  def test_add_custom_condition(self):
    # Check is zero
    assert (self.prog.advancedSearchLayout.count() == 0)

    # Check is 3
    self.searchHandler.add_custom_condition()
    assert (self.prog.advancedSearchLayout.count() == 3)

    # Check is 6
    self.searchHandler.add_custom_condition()
    assert (self.prog.advancedSearchLayout.count() == 6)

  def test_remove_custom_condition(self):
    # Check is zero
    assert (self.prog.advancedSearchLayout.count() == 0)

    self.searchHandler.add_custom_condition()
    self.searchHandler.remove_custom_condition()
    assert (self.prog.advancedSearchLayout.count() == 0)

    self.searchHandler.add_custom_condition()
    self.searchHandler.add_custom_condition()
    self.searchHandler.remove_custom_condition()
    assert (self.prog.advancedSearchLayout.count() == 3)
    self.searchHandler.remove_custom_condition()
    assert (self.prog.advancedSearchLayout.count() == 0)

  def test_generate_field_combo(self):
    fieldCombo = self.searchHandler.generate_field_combo()
    assert(isinstance(fieldCombo, QtWidgets.QComboBox))

  def test_generate_condition_combo(self):
    conditionCombo = self.searchHandler.generate_field_combo()
    assert (isinstance(conditionCombo, QtWidgets.QComboBox))

  # def test_generate_advanced_search(self):
  #   self.searchHandler.generate_advanced_search('Artist', 'Contains', 'Grateful Dead')
