import py.test
from unittest import TestCase
import cache
import os
import pathlib
class TestCache(TestCase):
  def test_save(self):
    dataStruct = {'Key' : 'Value'}

    try:
      cache.save(dataStruct, 'testSaveStruct')
      os.remove(os.path.abspath(str(pathlib.Path(__file__).parents[1]) + "/cache/testSaveStruct.pkl"))
    except Exception as e:
      self.fail()

  def test_load(self):
    dataStruct = {'Key' : 'Value'}
    cache.save(dataStruct, 'testSaveStruct')
    loadedDataStruct = cache.load('testSaveStruct')

    assert(dataStruct == loadedDataStruct)

    try:
      os.remove(os.path.abspath(str(pathlib.Path(__file__).parents[1]) + "/cache/testSaveStruct.pkl"))
    except Exception as e:
      self.fail()
