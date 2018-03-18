import py.test
from unittest import TestCase
import cache
import os
import pathlib
import pytest
class TestCache(TestCase):
  def test_save(self):
    dataStruct = {'Key' : 'Value'}
    cacheInstance = cache.Cache()
    try:
      cacheInstance.save(dataStruct, 'testSaveStruct')
      os.remove(os.path.abspath(str(pathlib.Path(__file__).parents[1]) + "/etreebrowser/cache/testSaveStruct.pkl"))
    except Exception as e:
      self.fail()

  def test_load(self):
    dataStruct = {'Key' : 'Value'}
    cacheInstance = cache.Cache()
    cacheInstance.save(dataStruct, 'testSaveStruct')
    loadedDataStruct = cacheInstance.load('testSaveStruct')

    assert(dataStruct == loadedDataStruct)

    try:
      os.remove(os.path.abspath(str(pathlib.Path(__file__).parents[1]) + "/etreebrowser/cache/testSaveStruct.pkl"))
    except Exception as e:
      self.fail()

  def test_file_not_found(self):
    cacheInstance = cache.Cache()
    with pytest.raises(FileNotFoundError):
      self.failedFile = cacheInstance.load('NonExistentFile')
