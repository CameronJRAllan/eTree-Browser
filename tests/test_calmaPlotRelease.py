import calma
from unittest import TestCase
import pytest
import application
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from unittest import TestCase
import search
import mock

def mockCalmaPlot(height, width, dpi, hasCalma):
  return QtWidgets.QWidget()

class TestCalmaPlotRelease():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()
    qtbot.add_widget(self.dialog)

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

    # self.calmaPlotRelease = calma.CalmaPlotRelease()

  @mock.patch('calma.CalmaPlotRelease.calma_release')
  def test_constructor_calma_plot_release(self, calmaReleaseFunc):
    calmaPlotRelease = calma.CalmaPlotRelease(self.prog, 'Title', 'Segmentation')
    assert(isinstance(calmaPlotRelease.plotContainerWidget, QtWidgets.QWidget))
    assert(calmaReleaseFunc.called)

  @mock.patch('calma.Calma.set_new_track_calma')
  def test_calma_release(self, setNewTrackFunc):
    calmaPlotRelease = calma.CalmaPlotRelease(self.prog, 'Animal Liberation Orchestra Live at The Fillmore on 2014-02-21', 'Segmentation')
    assert(isinstance(calmaPlotRelease.calma, calma.Calma))
    assert(setNewTrackFunc.called)

  @mock.patch('calma.CalmaPlotRelease.calma_release')
  @mock.patch('graph.CalmaPlot.plot_calma_data')
  def test_callback_set_new_track(self, calmaReleaseFunc, plotCalmaDataFunc):
    features = ['key', 'segment']
    for feature in features:
      calmaPlotRelease = calma.CalmaPlotRelease(self.prog, 'Animal Liberation Orchestra Live at The Fillmore on 2014-02-21', 'Segmentation')
      calmaPlotRelease.plots = []
      calmaPlotRelease.max = 2
      calmaPlotRelease.numberCalmaDisplayed = 0
      calmaPlotRelease.plotLayout = QtWidgets.QVBoxLayout()

      calmaPlotRelease.callback_set_new_track(None, None, None, None, {'feature' : feature,
                                                                       'title' : 'Animal Liberation Orchestra Live at The Fillmore on 2014-02-21'})

      assert(len(calmaPlotRelease.plots) == 1)
      assert(plotCalmaDataFunc.called)

  # def test_callback_set_new_track(self):
  #   # callback_set_new_track(self, loudness, keys, segments, duration, trackInfo)
