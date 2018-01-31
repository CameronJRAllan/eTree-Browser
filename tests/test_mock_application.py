
import sys
sys.path.append("..")
import application
from PyQt5 import QtWidgets, QtCore
from pytestqt import qtbot
# Create QApplication instance
app = QtWidgets.QApplication(sys.argv)

# Create dialog to show this instance
dialog = QtWidgets.QMainWindow()

# Start main event loop
prog = application.mainWindow(dialog)

def test_mock_change_type_order(mocker):
  mocker.spy(prog.browseListHandler, 'generate_browse_models')
  assert(prog.browseListHandler.generate_browse_models.call_count == 0)

  # Artist model
  prog.browseListHandler.change_type_order(0)
  assert(prog.browseListHandler.generate_browse_models.call_count == 1)

  # Genre model
  prog.browseListHandler.change_type_order(1)
  assert(prog.browseListHandler.generate_browse_models.call_count == 2)

def test_mock_change_type(mocker):
  mocker.spy(prog.browseListHandler, 'change_type_order')
  assert(prog.browseListHandler.change_type_order.call_count == 0)

  prog.browseListHandler.change_type(0)
  assert(prog.browseListHandler.change_type_order.call_count == 1)
  prog.browseListHandler.change_type(1)
  assert(prog.browseListHandler.change_type_order.call_count == 2)

def test_mock_retrieve_release_info(mocker):
  mocker.spy(prog.browseTreeProperties, 'fill_properties_tree_view')
  prog.browseTreeProperties.retrieve_release_info("3 Dimensional Figures Live at The Red Square on 2008-01-10")
  assert(prog.browseTreeProperties.fill_properties_tree_view.call_count == 1)

def test_advanced_search_fields(qtbot):
  assert(prog.searchForm.advancedSearchLayout.count() == 0)

  qtbot.mouseClick(prog.searchForm.addConditionBtn, QtCore.Qt.LeftButton)
  assert(prog.searchForm.advancedSearchLayout.count() == 3)

  qtbot.mouseClick(prog.searchForm.addConditionBtn, QtCore.Qt.LeftButton)
  assert(prog.searchForm.advancedSearchLayout.count() == 6)

  qtbot.mouseClick(prog.searchForm.removeConditionBtn, QtCore.Qt.LeftButton)
  assert(prog.searchForm.advancedSearchLayout.count() == 3)

  qtbot.mouseClick(prog.searchForm.removeConditionBtn, QtCore.Qt.LeftButton)
  assert(prog.searchForm.advancedSearchLayout.count() == 0)

def test_browse_search_artist(qtbot):
  qtbot.keyClicks(prog.quickFilter, '3 Dimensional Figures')

  assert(prog.quickFilter.text() == '3 Dimensional Figures')
  assert(prog.browseList.model().item(0,0).text() == '3 Dimensional Figures')

  prog.quickFilter.clear()
  qtbot.keyClicks(prog.quickFilter, 'Grateful Dead')
  assert (prog.browseList.model().item(0, 0).text() == 'Grateful Dead')

def test_get_translation_uri():
  uri = prog.browseTreeProperties.get_translation_uri()
  for key in uri.keys():
    assert(key.startswith('http://'))

