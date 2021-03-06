from unittest import TestCase
import pytest
import application
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from unittest import TestCase
import search

class TestSearchHandlerQt():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()
    qtbot.add_widget(self.dialog)

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

    # Search handler
    self.searchHandler = search.SearchHandler(self.prog)

  def test_add_custom_condition(self):
    # Check is zero
    assert (self.prog.searchForm.advancedSearchLayout.count() == 0)

    # Check is 3
    self.searchHandler.add_custom_condition()
    assert (self.prog.searchForm.advancedSearchLayout.count() == 3)

    # Check is 6
    self.searchHandler.add_custom_condition()
    assert (self.prog.searchForm.advancedSearchLayout.count() == 6)

  def test_remove_custom_condition(self):
    # Check is zero
    assert (self.prog.searchForm.advancedSearchLayout.count() == 0)

    self.searchHandler.add_custom_condition()
    self.searchHandler.remove_custom_condition()
    assert (self.prog.searchForm.advancedSearchLayout.count() == 0)

    self.searchHandler.add_custom_condition()
    self.searchHandler.add_custom_condition()
    self.searchHandler.remove_custom_condition()
    assert (self.prog.searchForm.advancedSearchLayout.count() == 3)
    self.searchHandler.remove_custom_condition()
    assert (self.prog.searchForm.advancedSearchLayout.count() == 0)

  def test_generate_field_combo(self):
    fieldCombo = self.searchHandler.generate_field_combo()
    assert (isinstance(fieldCombo, QtWidgets.QComboBox))

  def test_update_auto_complete(self, qtbot):
    # Click on button to add new custom condition
    qtbot.mouseClick(self.prog.searchForm.addConditionBtn, QtCore.Qt.LeftButton)

    # Check auto-complete
    try:
      self.prog.searchHandler.update_auto_complete()
    except Exception as e:
      pytest.fail()

  def test_load_saved_search(self):
    model = QtGui.QStandardItemModel()
    item = QtGui.QStandardItem("Grateful Dead")
    model.appendRow(item)
    self.prog.searchHandler.load_saved_search(model.index(0, 0))
    assert(self.prog.topMenuTabs.currentIndex() == 2)

  def test_generate_condition_combo(self):
    combo = self.searchHandler.generate_condition_combo()

    assert(isinstance(combo, QtWidgets.QComboBox))
    assert(combo.count() == 8)

  def test_generate_advanced_search(self):
    result = self.searchHandler.generate_advanced_search("Artist", "is", "Grooveshire")
    assert(result=='FILTER(?name="Grooveshire") ')

    result = self.searchHandler.generate_advanced_search("Artist", "is not", "Grooveshire")
    assert(result=='FILTER(?name!="Grooveshire") ')

    result = self.searchHandler.generate_advanced_search("Artist", "starts with", "Grooveshire")
    assert(result=='FILTER(STRSTARTS(?name,"Grooveshire")) ')

    result = self.searchHandler.generate_advanced_search("Artist", "ends with", "Grooveshire")
    assert(result=='FILTER(STRENDS(?name,"Grooveshire")) ')

    result = self.searchHandler.generate_advanced_search("Artist", "contains", "Grooveshire")
    assert(result=='FILTER(CONTAINS(?name,"Grooveshire")) ')

    result = self.searchHandler.generate_advanced_search("Artist", "does not contain", "Grooveshire")
    assert(result=='FILTER(!CONTAINS(?name,"Grooveshire") ')

    result = self.searchHandler.generate_advanced_search("Artist", "matches RegEx", "Grooveshire")
    assert(result=='FILTER(regex(?name, "Grooveshire", "i")) ')

    result = self.searchHandler.generate_advanced_search("Genre", "does not match RegEx", "Grooveshire")
    assert(result=='FILTER(!regex(?genre, "Grooveshire", "i")) ')

    result = self.searchHandler.generate_advanced_search("Genre", "contains", "folk")
    assert(result=='FILTER(CONTAINS(?genre,"folk")) ')

    result = self.searchHandler.generate_advanced_search("Location", "contains", "New York City, USA")
    assert(result=='FILTER(CONTAINS(?place,"New York City, USA")) ')

  def test_custom_search(self, qtbot):
    # Setup custom search boxes
    qtbot.mouseClick(self.prog.searchForm.addConditionBtn, QtCore.Qt.LeftButton)
    self.prog.searchForm.advancedSearchLayout.itemAt(2).widget().setText("Jason Mraz")

    customConditions = self.prog.searchHandler.custom_search()
    assert(isinstance(customConditions, list))
    assert(customConditions[0] == """FILTER(?name="Jason Mraz") """)


  def test_change_condition_or(self):
    customConditions = ['FILTER(?name="Grateful Dead") ', 'FILTER(?name!="Jason Mraz") ']
    result = self.searchHandler.change_condition_or(customConditions)
    assert("||" in result[0])
    assert("||" not in result[1])

    customConditions = ['FILTER(?name="Grateful Dead") ', 'FILTER(?name!="Jason Mraz") ']
    result = self.searchHandler.change_condition_or(customConditions)
    assert("||" in result[0])
    assert("||" not in result[1])

  def test_ensure_matching_parentheses(self):
    customConditions = ['FILTER(?name="Grateful Dead") ', 'FILTER(?name!="Jason Mraz") ']
    result = self.searchHandler.ensure_matching_parentheses(customConditions)
    assert(result.count('(') == result.count(')'))

    customConditions = ['FILTER(?name="Grateful Dead") ', 'FILTER(?name!="Jason Mraz")) ']
    result = self.searchHandler.ensure_matching_parentheses(customConditions)
    assert(result.count('(') == result.count(')'))
    #
    # customConditions = ['FILTER(?name="Grateful Dead") ', 'FILTER(?name!="Jason Mraz")) ']
    # result = self.searchHandler.ensure_matching_parentheses(customConditions)
    # assert(result.count('(') == result.count(')'))

  def test_generate_mapped_locations(self):
    self.prog.searchForm.locationRangeFilter.setText("500")
    self.prog.searchForm.locationFilter.setText("Gettysburg, PA, USA")
    locations = self.prog.searchHandler.generate_mapped_locations()

    assert(len(locations)==11404)

  def test_get_mapped_countries(self):
    countries = self.prog.searchHandler.get_mapped_countries("Israel")
    assert(len(countries) == 7)

    countries = self.prog.searchHandler.get_mapped_countries("United Kingdom, USA, Israel")
    assert(len(countries) == 31208)

    countries = self.prog.searchHandler.get_mapped_countries("France, Germany")
    assert(len(countries) == 607)

  def test_perform_search(self):
    self.prog.searchForm.artistFilter.setText("Jason Mraz")
    self.prog.searchForm.artistFilter.setText("")

    try:
      self.prog.searchHandler.perform_search()
    except Exception as e:
      print(e)
      pytest.fail(e)

    # Check fields were reset
    assert(self.prog.searchForm.artistFilter.text() == "")
    assert(self.prog.searchForm.genreFilter.text() == "")
    assert(self.prog.searchForm.venueFilter.text() == "")
    assert(self.prog.searchForm.locationFilter.text() == "")

  def test_reset_search_form(self):
    # Add text to boxes
    self.prog.searchForm.artistFilter.setText("Artist")
    self.prog.searchForm.genreFilter.setText("Genre")
    self.prog.searchForm.trackNameFilter.setText("Track Name")
    self.prog.searchForm.dateFrom.setDate(QtCore.QDate(1952, 2, 12))
    self.prog.searchForm.dateTo.setDate(QtCore.QDate(2014, 2, 12))
    self.prog.searchForm.venueFilter.setText("Venue")
    self.prog.searchForm.locationFilter.setText("New York City, NYC")
    self.prog.searchForm.locationRangeFilter.setText("200")
    self.prog.searchForm.countryFilter.setText("USA")

    # Call reset function
    self.prog.searchHandler.reset_search_form()

    # Assert they were reset as expected
    assert(len(self.prog.searchForm.artistFilter.text()) == 0)
    assert(len(self.prog.searchForm.genreFilter.text()) == 0)
    assert(len(self.prog.searchForm.trackNameFilter.text()) == 0)
    assert(len(self.prog.searchForm.venueFilter.text()) == 0)
    assert(len(self.prog.searchForm.locationFilter.text()) == 0)
    assert(len(self.prog.searchForm.locationRangeFilter.text()) == 0)
    assert(len(self.prog.searchForm.countryFilter.text()) == 0)

    assert(self.prog.searchForm.dateFrom.date() == QtCore.QDate(1950, 1, 1))
    assert(self.prog.searchForm.dateTo.date() == QtCore.QDate(2017, 1, 1))

  def test_setup_views(self):
  #   pytest.fail()
    requestedViews = ['map', 'timeline', 'table']
    results = {'results' : {'bindings' : [] },
               'head' : { 'vars' : []
               }}

    try:
      self.searchHandler.setup_views(requestedViews, results)
    except Exception as e:
      print(e)
      pytest.fail()

