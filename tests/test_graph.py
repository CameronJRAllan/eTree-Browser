import sys
sys.path.append("..")
from unittest import TestCase
import export
import pytest
import graph
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.patches as mpatch
import matplotlib
import calma
import random
from PyQt5 import QtWidgets
import application

class TestGraph(TestCase):
  @pytest.fixture(scope="function", autouse=True)
  def setup(self):
    self.graphInstance = graph.CalmaPlot(600,600,100, True)
    self.calma = calma.Calma()

  def test_constructor_graph(self):
    assert(isinstance(self.graphInstance.fig, Figure))

  def test_has_no_calma_available(self):
    graphInstance = graph.CalmaPlot(600, 600, 100, False)
    assert(graphInstance.placeHolderText._text == 'No CALMA data available for this query')

  def test_has_calma_available(self):
    graphInstance = graph.CalmaPlot(600, 600, 100, True)
    assert(graphInstance.placeHolderText._text == 'Click on a performance track for CALMA data')

  def test_get_colour_map(self):
    assert(isinstance(self.graphInstance.get_colour_map(), dict))

  def test_pre_processing(self):
    randoms = random.sample(range(60000), 1000)
    duration = 300
    nploudnessValues, duration, xSpaced, average = self.graphInstance.pre_processing(randoms, duration)

  def test_calculate_graph_element_positions(self):
    keyInfo = [[0.0, 'G major'], [1.486077097, 'G minor'], [8.173424036, 'G major'], [10.402539682, 'D minor'], [19.319002267, 'G minor'],
               [30.464580498, 'G major'], [40.867120181, 'D minor'], [41.61015873, 'G minor']]

    duration = float(326)
    average = 8.130601759965474

    for index, key in enumerate(keyInfo):
      lx, ly, rec = self.graphInstance.calculate_graph_element_position(keyInfo, key, index, duration, average)
      assert(isinstance(rec, mpatch.Rectangle))

# class TestGraphPlotQt():
#   @pytest.fixture(scope="function", autouse=True)
#   def setup(self, qtbot):
#     # Create dialog to show this instance
#     self.dialog = QtWidgets.QMainWindow()
#
#     # Start main event loop
#     self.prog = application.mainWindow(self.dialog)
#     self.graphInstance = graph.CalmaPlot(600, 600, 100, True)
#
#   def test_plot_calma_data(self):
#     """
#     http://calma.linkedmusic.org/data/f3/track_f3d3321d-2ee3-49ab-9b9d-221d75ca4704
#     http://calma.linkedmusic.org/data/80/track_8002a966-fc65-4af6-897a-cdecd237f8f9
#     http://calma.linkedmusic.org/data/b3/track_b39b7800-193f-4196-ac41-c139599f97b3
#     http://calma.linkedmusic.org/data/c4/track_c4e3019f-bb86-4c7d-b5be-7827ef7e48c7
#     """
#
#     # Create a plot of the CALMA data
#     self.prog.calmaHandler.set_new_track_calma("http://calma.linkedmusic.org/data/80/track_8002a966-fc65-4af6-897a-cdecd237f8f9")
#     self.graphInstance.plot_calma_data(self.prog.calmaHandler.loudnessValues, self.prog.calmaHandler.keyInfo, self.prog.calmaHandler.duration)
