from unittest import TestCase
import pytest
import application
import sys
from PyQt5 import QtWidgets, QtCore
from unittest import TestCase

class TestSearchHandlerQt():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
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
    assert (isinstance(fieldCombo, QtWidgets.QComboBox))

  def test_update_auto_complete(self, qtbot):
    # Click on button to add new custom condition
    qtbot.mouseClick(self.prog.addConditionBtn, QtCore.Qt.LeftButton)

    # Check auto-complete
    try:
      self.prog.searchHandler.update_auto_complete()
    except Exception as e:
      pytest.fail()

  def test_load_saved_search(self):
    pytest.fail()

  def test_add_search_tab_contents(self):
    self.prog.searchHandler.add_search_tab_contents()
    assert(self.prog.searchTab.layout().count() == 1)

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
    qtbot.mouseClick(self.prog.addConditionBtn, QtCore.Qt.LeftButton)
    self.prog.advancedSearchLayout.itemAt(2).widget().setText("Jason Mraz")

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
    self.prog.locationRangeFilter.setText("500")
    self.prog.locationFilter.setText("Gettysburg, PA, USA")
    locations = self.prog.searchHandler.generate_mapped_locations()

    assert(len(locations)==14972)

  def test_get_mapped_countries(self):
    countries = self.prog.searchHandler.get_mapped_countries("Israel")
    assert(len(countries) == 7)

    countries = self.prog.searchHandler.get_mapped_countries("United Kingdom, USA, Israel")
    assert(len(countries) == 31208)

    countries = self.prog.searchHandler.get_mapped_countries("France, Germany")
    assert(len(countries) == 607)

  def test_perform_search(self):
    self.prog.artistFilter.setText("Jason Mraz")
    self.prog.artistFilter.setText("")

    try:
      self.prog.searchHandler.perform_search()
    except Exception as e:
      print(e)
      pytest.fail(e)

    # Check fields were reset
    assert(self.prog.artistFilter.text() == "")
    assert(self.prog.genreFilter.text() == "")
    assert(self.prog.venueFilter.text() == "")
    assert(self.prog.locationFilter.text() == "")

  def test_reset_search_form(self):
    # Add text to boxes
    self.prog.artistFilter.setText("Artist")
    self.prog.genreFilter.setText("Genre")
    self.prog.trackNameFilter.setText("Track Name")
    self.prog.dateFrom.setDate(QtCore.QDate(1952, 2, 12))
    self.prog.dateTo.setDate(QtCore.QDate(2014, 2, 12))
    self.prog.venueFilter.setText("Venue")
    self.prog.locationFilter.setText("New York City, NYC")
    self.prog.locationRangeFilter.setText("200")
    self.prog.countryFilter.setText("USA")

    # Call reset function
    self.prog.searchHandler.reset_search_form()

    # Assert they were reset as expected
    assert(len(self.prog.artistFilter.text()) == 0)
    assert(len(self.prog.genreFilter.text()) == 0)
    assert(len(self.prog.trackNameFilter.text()) == 0)
    assert(len(self.prog.venueFilter.text()) == 0)
    assert(len(self.prog.locationFilter.text()) == 0)
    assert(len(self.prog.locationRangeFilter.text()) == 0)
    assert(len(self.prog.countryFilter.text()) == 0)

    assert(self.prog.dateFrom.date() == QtCore.QDate(1950, 1, 1))
    assert(self.prog.dateTo.date() == QtCore.QDate(2017, 1, 1))

  def test_setup_views(self):
    requestedViews = ['map', 'timeline', 'table']
    results = {'results' : {'bindings' : [] },
               'head' : { 'vars' : []
               }}

    try:
      self.searchHandler.setup_views(requestedViews, results)
    except Exception as e:
      print(e)
      pytest.fail()

