from unittest import TestCase
import pytest
import application
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from unittest import TestCase
import view
import mock
import cache
import graph
import multithreading

def fake_get_label_current_row():
  return "Mogwai Live at The Forum on 1999-10-16"

def fake_table_change_focus(arg):
  return

def get_save_name(none, title, start_dir):
  return ['filename']

def get_save_name_invalid(none, title, start_dir):
  return ['']

def fake_thread(arg1, arg2):
  return None

class TestViewQt():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

  @mock.patch('cache.save')
  @mock.patch('application.mainWindow.initialize_history_table')
  def test_save_search(self, arg, arg2):
    prev = len(self.prog.savedSearches)

    self.prog.searchForm.artistFilter.setText('Grateful Dead')
    self.prog.searchForm.numResultsSpinbox.setValue(1)
    self.prog.searchHandler.perform_search()
    self.prog.searchForm.infoWindowWidgets['saveEdit'].setText('My Test Search')
    self.prog.searchHandler.view.save_search()

    assert(len(self.prog.savedSearches) == prev + 1)

  def test_change_proportions(self):
    self.prog.searchForm.infoWindowWidgets['tableSpan'].setValue(5)
    self.prog.searchForm.infoWindowWidgets['timelineSpan'].setValue(2)
    self.prog.searchForm.infoWindowWidgets['mapSpan'].setValue(3)
    self.prog.searchForm.change_proportions()

    # DO SOME ASSERTIONS HERE

  @mock.patch('application.TableHandler.change_focus', side_effect=fake_table_change_focus)
  def test_move_focus_str(self, arg):
    self.prog.searchHandler.view.move_focus("0")
    # DO SOME ASSERTIONS HERE

  @mock.patch('application.TableHandler.change_focus', side_effect=fake_table_change_focus)
  def test_move_focus_qitem(self, arg):
    qTableItem = QtWidgets.QTableWidgetItem("Test")
    self.prog.searchHandler.view.tableHandler.resultsTable.insertRow(0)
    self.prog.searchHandler.view.tableHandler.resultsTable.setItem(0, 0, qTableItem)
    self.prog.searchHandler.view.move_focus(qTableItem)
    # DO SOME ASSERTIONS HERE

  @mock.patch('calma.Calma.get_calma_data')
  @mock.patch('graph.CalmaPlot.plot_calma_data')
  def test_calma_set_track_callback_signal(self, getCalmaMock, plotCalmaMock):
    self.prog.calmaHandler.calmaCache = {}
    self.prog.searchHandler.view.calma.calmaCache = {}
    self.prog.searchHandler.view.calma.duration = 100
    self.prog.searchHandler.view.calma_set_track_callback_signal([], [], [], 100.00)
    assert(plotCalmaMock)
    assert(getCalmaMock)

  @mock.patch('calma.Calma.get_calma_data')
  @mock.patch('graph.CalmaPlot.plot_calma_data')
  def test_calma_set_track_callback_signal_segment(self, getCalmaMock, plotCalmaMock):
    self.prog.calmaHandler.calmaCache = {}
    self.prog.searchHandler.view.calma.calmaCache = {}
    self.prog.searchHandler.view.calma.duration = 100
    self.prog.searchForm.infoWindowWidgets['toggleKeysSegments'].setCurrentText("Segmentation")
    self.prog.searchHandler.view.calma_set_track_callback_signal([], [], [], 100.00)
    assert(plotCalmaMock)
    assert(getCalmaMock)

  @mock.patch('view.View.get_label_current_row', side_effect=fake_get_label_current_row)
  def test_update_tracklist(self, arg):
    self.prog.searchHandler.view.update_tracklist()
    assert(self.prog.searchForm.tracklistView.count() > 0)

  @mock.patch('multithreading.WorkerThread.__init__', side_effect=fake_thread)
  def test_graph_calma(self, graphCalmaMock):
    self.prog.searchHandler.view.tracklistCalma = {'test track' : 'http://calma.linkedmusic.org/data/f3/track_f3dfeae5-fa57-42b2-8ede-3446438b5067'}

    self.model = QtGui.QStandardItemModel()
    self.model.appendRow(QtGui.QStandardItem('test track'))

    self.prog.searchHandler.view.graph_calma(self.model.index(0, 0))

    assert(graphCalmaMock.called == True)

    self.prog.searchForm.infoWindowWidgets['toggleKeysSegments'].setCurrentIndex(1)
    self.prog.searchHandler.view.graph_calma(self.model.index(0, 0))

    assert(graphCalmaMock.called == True)

  def test_graph_calma_keyerror(self):
    self.model = QtGui.QStandardItemModel()
    self.model.appendRow(QtGui.QStandardItem('Invalid Item'))
    self.prog.searchHandler.view.tracklistCalma = {'test track' : 'http://calma.linkedmusic.org/data/f3/track_f3dfeae5-fa57-42b2-8ede-3446438b5067'}

    result = self.prog.searchHandler.view.graph_calma(self.model.index(0, 0))
    assert(result == None)

  @mock.patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName', side_effect=get_save_name)
  @mock.patch('matplotlib.figure.Figure.savefig')
  def test_save_calma_plot(self, getSaveFileName, saveFig):
    self.prog.searchHandler.view.save_calma_plot()
    assert(getSaveFileName.called)
    assert(saveFig.called)

  def test_search_table(self):
    item = QtWidgets.QTableWidgetItem('Melbourne')
    self.prog.searchHandler.view.tableHandler.resultsTable.setRowCount(5)
    self.prog.searchHandler.view.tableHandler.resultsTable.setItem(1, 1, item)
    self.prog.searchHandler.view.search_table('Melbourne')

  def test_view_results_invalid(self):
    self.view = view.View(self.prog, None, [], ValueError(), False)
    assert(isinstance(self.view.errorDialog, application.ErrorDialog))

  # @mock.patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName', side_effect=get_save_name_invalid)
  # @mock.patch('matplotlib.figure.Figure.savefig')
  # def test_save_calma_plot_no_path(self, getSaveFileName, saveFig):
  #   self.prog.searchHandler.view.save_calma_plot()
  #   assert(getSaveFileName.called)

  def test_constructor_two_views(self):
    results = """{'head': {'link': [], 'vars': ['label', 'name', 'place', 'location', 'date', 'calma']}, 'results': {'distinct': False, 'ordered': True, 'bindings': [{'label': {'type': 'literal', 'value': 'Grateful Dead Live at Nassau Coliseum on 1982-04-11'}, 'name': {'type': 'literal', 'value': 'Grateful Dead'}, 'place': {'type': 'literal', 'value': 'Uniondale, NY'}, 'location': {'type': 'uri', 'value': 'http://etree.linkedmusic.org/venue/gd1982-04-11.nak300.morris.102037.sbeok.flac16'}, 'date': {'type': 'literal', 'value': '1982-04-11'}, 'calma': {'type': 'literal', 'value': ''}}]}}"""
    self.view = view.View(self.prog, self.prog.searchHandler, ['timeline', 'table'], results, False)
    assert(self.view.viewLayout.count() == 2)

  def test_constructor_three_views(self):
    results = """{'head': {'link': [], 'vars': ['label', 'name', 'place', 'location', 'date', 'calma']}, 'results': {'distinct': False, 'ordered': True, 'bindings': [{'label': {'type': 'literal', 'value': 'Grateful Dead Live at Nassau Coliseum on 1982-04-11'}, 'name': {'type': 'literal', 'value': 'Grateful Dead'}, 'place': {'type': 'literal', 'value': 'Uniondale, NY'}, 'location': {'type': 'uri', 'value': 'http://etree.linkedmusic.org/venue/gd1982-04-11.nak300.morris.102037.sbeok.flac16'}, 'date': {'type': 'literal', 'value': '1982-04-11'}, 'calma': {'type': 'literal', 'value': ''}}]}}"""
    self.view = view.View(self.prog, self.prog.searchHandler, ['timeline', 'map', 'table'], results, False)
    assert(self.view.viewLayout.count() == 3)

  def test_constructor_four_views(self):
    results = """{'head': {'link': [], 'vars': ['label', 'name', 'place', 'location', 'date', 'calma']}, 'results': {'distinct': False, 'ordered': True, 'bindings': [{'label': {'type': 'literal', 'value': 'Grateful Dead Live at Nassau Coliseum on 1982-04-11'}, 'name': {'type': 'literal', 'value': 'Grateful Dead'}, 'place': {'type': 'literal', 'value': 'Uniondale, NY'}, 'location': {'type': 'uri', 'value': 'http://etree.linkedmusic.org/venue/gd1982-04-11.nak300.morris.102037.sbeok.flac16'}, 'date': {'type': 'literal', 'value': '1982-04-11'}, 'calma': {'type': 'literal', 'value': ''}}]}}"""
    self.view = view.View(self.prog, self.prog.searchHandler, ['timeline', 'map', 'today in history', 'table'], results, False)
    assert(self.view.viewLayout.count() == 4)