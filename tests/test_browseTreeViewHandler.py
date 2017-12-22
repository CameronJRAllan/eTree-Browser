import pytest
import application
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import time
class TestBrowseTreeViewHandler():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

    # Search handler
    self.searchHandler = application.SearchHandler(self.prog)

  def test_tree_view_filter_update_artist(self, qtbot):
    # Emulate key-clicks into filter
    qtbot.addWidget(self.prog.quickFilter)
    qtbot.keyClicks(self.prog.quickFilter, "Grateful Dead")

    # Check correct result is at the top
    assert(self.prog.browseList.model().index(0, 0).data() == "Grateful Dead")

  # def test_expand_tree_item(self, qtbot):
  #   # Search for 3 Dimensional Figures
  #   qtbot.addWidget(self.prog.quickFilter)
  #   qtbot.keyClicks(self.prog.quickFilter, "3 Dimensional Figures")
  #
  #   # Click top result in filter
  #   self.prog.browseList.setFocus()
  #   viewRect = self.prog.browseList.visualRect(self.prog.browseList.model().index(0, 0))
  #   qtbot.mouseClick(self.prog.browseList, QtCore.Qt.LeftButton, pos=viewRect.center())
  #
  #   # Click on first performance
  #   print(type(self.prog.browseTreeView.model()))

    # Assert correct tracklist recieved (after wait)

  def test_add_tracks_tree(self, qtbot):
    self.fail()

  def test_play_tree_item(self):
    self.fail()

  def test_update_tree_view_artist(self, qtbot):
    # Search for 3 Dimensional Figures
    qtbot.addWidget(self.prog.quickFilter)
    qtbot.addWidget(self.prog.browseList)

    qtbot.keyClicks(self.prog.quickFilter, "3 Dimensional Figures")

    # Click top result in filter
    # self.prog.browseList.setFocus()
    # viewRect = self.prog.browseList.visualRect(self.prog.browseList.model().index(0, 0))
    # qtbot.mouseClick(self.prog.browseList, QtCore.Qt.LeftButton, pos=viewRect.center())

    # Call tree view function with artist
    self.prog.browseListHandler.browse_link_clicked(self.prog.browseList.model().index(0, 0))

    assert(self.prog.browseTreeView.model().itemData(self.prog.browseTreeView.model().index(0, 0))[0] == "3 Dimensional Figures Live at Red Square on "
                                                                                                      "2007-08-03")
    assert(isinstance(self.prog.browseTreeView.model(), QtGui.QStandardItemModel))

  def test_update_tree_view_genre(self, qtbot):
    self.prog.typeBrowseCombo.setCurrentIndex(1)

    # Search for "folk" genre
    qtbot.addWidget(self.prog.quickFilter)
    qtbot.addWidget(self.prog.browseList)

    qtbot.keyClicks(self.prog.quickFilter, "folk")

    # Call tree view function with genre
    self.prog.browseListHandler.browse_link_clicked(self.prog.browseList.model().index(0, 0))

    assert(self.prog.browseTreeView.model().itemData("Billy Bragg" in self.prog.browseTreeView.model().index(0, 0))[0])
    assert(isinstance(self.prog.browseTreeView.model(), QtGui.QStandardItemModel))

  def test_update_tree_view_location(self, qtbot):
    self.prog.typeBrowseCombo.setCurrentIndex(2)

    # Search for "New York City" location
    qtbot.addWidget(self.prog.quickFilter)
    qtbot.addWidget(self.prog.browseList)
    qtbot.keyClicks(self.prog.quickFilter, "New York City")

    # Call tree view function with genre
    self.prog.browseListHandler.browse_link_clicked(self.prog.browseList.model().index(0, 0))

    assert(self.prog.browseTreeView.model().itemData("Furthur Live" in self.prog.browseTreeView.model().index(0, 0))[0])
    assert(isinstance(self.prog.browseTreeView.model(), QtGui.QStandardItemModel))
