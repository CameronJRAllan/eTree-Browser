from PyQt5 import QtCore
import maps
from unittest import TestCase
import pytest
class SignalStubs(QtCore.QObject):
  js_callback = QtCore.pyqtSignal(str, str, str)
  homepage_start = QtCore.pyqtSignal()
  homepage_end = QtCore.pyqtSignal()

  def __init__(self, parent=None):
    super().__init__()
    self.js_callback.connect(self.callback_slot)
    self.homepage_start.connect(self.start)
    self.homepage_end.connect(self.end)
    self.reached_end = False
    self.reached_start = False
    self.callback_recieved = False

    self.kwargs = {'js_callback': self.js_callback,
                   'homepage_start': self.homepage_start,
                   'homepage_end': self.homepage_end
                   }

  def callback_slot(self):
    self.callback_recieved = True

  def start(self):
    self.reached_start = True

  def end(self):
    self.reached_end = True

class TestMaps(TestCase):
  @pytest.fixture(scope="function", autouse=True)
  def setup(self):
    self.signalStubs = SignalStubs()
    self.mapInstance = maps.Maps()

    # results =
    self.emptyResults = {'results' : {'bindings' : []}}

  def test_constructor(self):
    assert(isinstance(self.mapInstance.keys, list))
    assert(isinstance(self.mapInstance.geoCache, dict))

  def test_add_points(self):
    assert(self.signalStubs.reached_start == False)
    assert(self.signalStubs.reached_end == False)
    assert(self.signalStubs.callback_recieved == False)

    result = {'results' : {'bindings' : [{'label': {'type': 'literal', 'value': 'Drive-By Truckers Live at The Fillmore @ TLA on 2008-03-27'},
                                          'name': {'type': 'literal', 'value': 'Drive-By Truckers'},
                                          'place': {'type': 'literal', 'value': 'Philadelphia, PA'}}]}}

    self.mapInstance.homepage_add(result, **self.signalStubs.kwargs)

    assert(self.signalStubs.reached_start == True)
    assert(self.signalStubs.reached_end == True)
    assert(self.signalStubs.callback_recieved == True)

  def test_add_empty_results(self):
    assert(self.signalStubs.reached_start == False)
    assert(self.signalStubs.reached_end == False)

    self.mapInstance.homepage_add(self.emptyResults, **self.signalStubs.kwargs)

    assert(self.signalStubs.reached_start == True)
    assert(self.signalStubs.reached_end == True)