from unittest import TestCase
import pytest
import application
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from unittest import TestCase
import mock

def set_updated_table():
  tableUpdated = True
  print(tableUpdated)

class TestTableHandler():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

    # Search handler
    self.tableHandler = application.TableHandler(self.prog)
    self.signalStubs = SignalStubs()
    self.results = self.prog.sparql.get_tracklist('Mogwai Live at the Forum on 16-10-1999')

    # Setup a default view in the table
    self.prog.searchHandler.setup_views(['table'], self.results)

    # self.TableHandler.generate_results_table(results, **self.signalStubs.kwargs)

  def test_on_table_scroll(self):
    try:
      self.prog.searchHandler.view.tableHandler.resultsTable.scrollToBottom()
    except Exception as e:
      print(e)
      pytest.fail()

  @mock.patch('application.TableHandler.get_label_for_URI')
  def test_retrieve_labels_scroll(self, workerThread):
    assert(not workerThread.called)

    for rowIndex in range(0, self.prog.searchHandler.view.tableHandler.resultsTable.rowCount() - 1):
      for columnIndex in range(0, self.prog.searchHandler.view.tableHandler.resultsTable.columnCount() - 1):
        self.prog.searchHandler.view.tableHandler.resultsTable.item(rowIndex, columnIndex).setText("http://etree.linkedmusic.org/venue/akashic2005-02-04.c4.flac16")

    signals = SignalStubs()
    self.prog.searchHandler.view.tableHandler.retrieve_labels_scroll(0, kwargs=signals.kwargs)
    assert(workerThread.called)


  def test_get_table(self):
    assert(isinstance(self.prog.searchHandler.view.tableHandler.resultsTable, QtWidgets.QTableWidget))

  def test_generate_table_start(self):
    self.tableHandler.generate_table_start(2, 2, ["Column Name 1", "Column Name 2"])
    table = self.tableHandler.get_table()

    assert(table.horizontalHeaderItem(0).text() == "Column Name 1")
    assert(table.horizontalHeaderItem(1).text() == "Column Name 2")

  def test_generate_table_end(self):
    self.tableHandler.generate_table_end()
    assert(self.tableHandler.get_table().EditTriggers() == QtWidgets.QAbstractItemView.NoEditTriggers)

  def test_change_focus(self):
    # Add example items to table
    self.tableHandler.get_table().setColumnCount(2)
    self.tableHandler.get_table().setHorizontalHeaderLabels(["Label", "Location"])
    self.tableHandler.get_table().setItem(0, 0, QtWidgets.QTableWidgetItem("Item 1"))
    self.tableHandler.get_table().setItem(0, 1, QtWidgets.QTableWidgetItem("Item 2"))
    self.tableHandler.get_table().setItem(1, 0, QtWidgets.QTableWidgetItem("Item 3"))
    self.tableHandler.get_table().setItem(1, 1, QtWidgets.QTableWidgetItem("Item 4"))

    try:
      self.tableHandler.change_focus(0)
      self.tableHandler.change_focus("Label")
    except Exception as e:
      print(e)
      pytest.fail()

  def test_check_is_number_true(self):
    assert(self.tableHandler.check_is_number(0) == True)
    assert(self.tableHandler.check_is_number(999) == True)
    assert(self.tableHandler.check_is_number(5) == True)
    assert(self.tableHandler.check_is_number(1.25) == True)

  def test_check_is_number_false(self):
    assert(self.tableHandler.check_is_number("String") == False)

  def test_generate_results_table(self):
    results = {'head': {'link': [],
                        'vars': ['label', 'name', 'place', 'location', 'date', 'calma']},
                        'results': {'distinct': False,
                                    'ordered': True,
                                    'bindings': [{'label': {'type': 'literal', 'value': 'Grateful Dead Live at Nassau Coliseum on 1982-04-11'}, 'name': {'type': 'literal', 'value': 'Grateful Dead'}, 'place': {'type': 'literal', 'value': 'Uniondale, NY'}, 'location': {'type': 'uri', 'value': 'http://etree.linkedmusic.org/venue/gd1982-04-11.nak300.morris.102037.sbeok.flac16'}, 'date': {'type': 'literal', 'value': '1982-04-11'}, 'calma': {'type': 'literal', 'value': ''}}, {'label': {'type': 'literal', 'value': 'Grateful Dead Live at Community War Memorial Auditorium on 1980-09-02'}, 'name': {'type': 'literal', 'value': 'Grateful Dead'}, 'place': {'type': 'literal', 'value': 'Rochester, NY'}, 'location': {'type': 'uri', 'value': 'http://etree.linkedmusic.org/venue/gd1980-09-02.nak300.friend.andrewf.102775.flac24'}, 'date': {'type': 'literal', 'value': '1980-09-02'}, 'calma': {'type': 'literal', 'value': ''}}, {'label': {'type': 'literal', 'value': 'Grateful Dead Live at Uptown Theater on 1978-05-16'}, 'name': {'type': 'literal', 'value': 'Grateful Dead'}, 'place': {'type': 'literal', 'value': 'Chicago, IL'}, 'location': {'type': 'uri', 'value': 'http://etree.linkedmusic.org/venue/gd1978-05-16.part.s2.sbd.miller.117206.flac16'}, 'date': {'type': 'literal', 'value': '1978-05-16'}, 'calma': {'type': 'literal', 'value': ''}}, {'label': {'type': 'literal', 'value': 'Grateful Dead Live at Riverfront Arena on 1989-04-08'}, 'name': {'type': 'literal', 'value': 'Grateful Dead'}, 'place': {'type': 'literal', 'value': 'Cincinnati, OH'}, 'location': {'type': 'uri', 'value': 'http://etree.linkedmusic.org/venue/gd89-04-08.beyer-fob.conner.7857.sbeok.shnf'}, 'date': {'type': 'literal', 'value': '1989-04-08'}, 'calma': {'type': 'literal', 'value': ''}}, {'label': {'type': 'literal', 'value': 'Grateful Dead Live at Boutwell Auditorium on 1980-04-28'}, 'name': {'type': 'literal', 'value': 'Grateful Dead'}, 'place': {'type': 'literal', 'value': 'Birmingham, AL'}, 'location': {'type': 'uri', 'value': 'http://etree.linkedmusic.org/venue/gd1980-04-28.fob.glassberg.motb.0040.88858.sbeok.flac16'}, 'date': {'type': 'literal', 'value': '1980-04-28'}, 'calma': {'type': 'literal', 'value': ''}}]}}

    self.tableHandler.generate_results_table(results, **self.signalStubs.kwargs)

  def test_get_label_for_URI(self):
    label = self.tableHandler.get_label_for_URI("http://etree.linkedmusic.org/artist/422aecc0-4aac-012f-19e9-00254bd44c28")
    assert(label == "Mogwai")

    label = self.tableHandler.get_label_for_URI("http://etree.linkedmusic.org/performance/mogwai2011-03-06.soundman.flacf")
    assert(label == "Mogwai Live at Mousonturm on 2011-03-06")

    label = self.tableHandler.get_label_for_URI("http://etree.linkedmusic.org/track/mogwai2011-03-06.soundman.flacf-3")
    assert(label == "Killing All the Flies")

  def test_set_location_width(self):
    self.prog.searchHandler.view.tableHandler.set_location_width()
    for c in range(0, self.prog.searchHandler.view.tableHandler.resultsTable.columnCount() - 1):
      if self.prog.searchHandler.view.tableHandler.horizontalHeaderItem(c).text() == 'Location':
        assert(self.prog.searchHandler.view.tableHandler.columnWidth(c) == 400)

  def test_open_table_menu(self, qtbot):
    self.prog.searchHandler.view.tableHandler.resultsTable.setRowCount(2)
    item = QtWidgets.QTableWidgetItem("Item")
    self.prog.searchHandler.view.tableHandler.resultsTable.setItem(0,0,item)
    index = self.prog.searchHandler.view.tableHandler.resultsTable.indexFromItem(item)
    self.prog.searchHandler.view.tableHandler.resultsTable.setCurrentIndex(index)
    qpoint = QtCore.QPoint(1,0)
    self.prog.searchHandler.view.tableHandler.open_table_menu(qpoint)
    assert (isinstance(self.prog.searchHandler.view.tableHandler.menu, QtWidgets.QMenu))
    self.prog.searchHandler.view.tableHandler.menu.close()

  @mock.patch('export.Export.export_data')
  def test_table_browse_menu_click(self, exportData):
    self.prog.searchForm.artistFilter.setText('Grateful Dead')
    self.prog.searchForm.numResultsSpinbox.setValue(5)
    results = self.prog.searchHandler.perform_search()
    self.prog.searchHandler.view.tableHandler.menuOnItem = QtCore.QPoint(1,0)
    self.prog.searchHandler.view.tableHandler.table_browse_menu_click(QtWidgets.QAction("JSON"))
    self.prog.searchHandler.view.tableHandler.table_browse_menu_click(QtWidgets.QAction("CSV"))
    self.prog.searchHandler.view.tableHandler.table_browse_menu_click(QtWidgets.QAction("M3U"))
    self.prog.searchHandler.view.tableHandler.table_browse_menu_click(QtWidgets.QAction("XML"))
    assert(exportData)

class SignalStubs(QtCore.QObject):
  update_table_item = QtCore.pyqtSignal(int, int, QtWidgets.QTableWidgetItem)
  add_table_item = QtCore.pyqtSignal(int, int, QtWidgets.QTableWidgetItem)
  fin_table_callback = QtCore.pyqtSignal()
  start_table_callback = QtCore.pyqtSignal(int, int, list)

  def __init__(self, parent=None):
    super().__init__()
    self.update_table_item.connect(self.signal_slot_stub)
    self.add_table_item.connect(self.signal_slot_stub)
    self.fin_table_callback.connect(self.signal_slot_stub)
    self.start_table_callback.connect(self.signal_slot_stub)

    self.kwargs = {'update_table_item': self.update_table_item,
                   'add_table_item': self.add_table_item,
                   'fin_table_callback': self.fin_table_callback,
                   'start_table_callback': self.start_table_callback}

  def signal_slot_stub(self):
    return

