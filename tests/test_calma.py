import sys
sys.path.append("..")
from unittest import TestCase
import pytest
import calma

class TestCalma(TestCase):
  @pytest.fixture(scope="function", autouse=True)
  def setup(self):
    self.calmaInstance = calma.Calma()

  def test_initial_state(self):
    assert(self.calmaInstance.keyInfo == None)
    assert(self.calmaInstance.loudnessValues == None)
    assert (self.calmaInstance.loudnessInfo == None)

  def test_get_features_track(self):
    # Check that an invalid URL does not return calma data
    assert(self.calmaInstance.get_features_track('http://InvalidURL.com') == False)

    # Check a valid URL, with no calma data, returns false
    assert(self.calmaInstance.get_features_track('http://ia601405.us.archive.org/8/items/mogwai1999-10-16.flac16/mogwai1999-10-16d1t04.mp3') == False)

    # Check that a correct URL returns true
    assert(self.calmaInstance.get_features_track('http://archive.org/download/dbt2004-05-08.4011s.flac16/dbt2004-05-08d1t02.flac') == True)

  def test_get_calma_data_key(self):
    # Check that we get a list returned from this information from a valid URL
    calmaData = self.calmaInstance.get_calma_data('http://calma.linkedmusic.org/data/9a/track_9a777890-c7be-4133-9e8a-d83c1347af51/', 'key')

    # Check that every sub-list contains 2 elements
    # Check that the 1st element in every sub-element in list is a float, and the second a string
    for item in calmaData:
      assert(len(item) == 2)

      assert(isinstance(item[0], float))
      assert(isinstance(item[1], str))

  # def test_tidy_key_change(self):
  #   # Check output type is list
  #   outputCorrect = self.calmaInstance.tidy_key_change(dict({
  #   'event1' : ['file:///home/cameron/PycharmProjects/Meta-Data/tests/#signal_timeline_0',
  #                                                                   'PT57.213968253S',
  #                                                                   'http://purl.org/NET/c4dm/timeline.owl#Instant',
  #                                                                   'C major',
  #                                                                   '1'],
  #   'event2' : ['file:///home/cameron/PycharmProjects/Meta-Data/tests/#signal_timeline_0',
  #                                                                   '2',
  #                                                                   'PT100.218478253S',
  #                                                                   'http://purl.org/NET/c4dm/timeline.owl#Instant',
  #                                                                   'D minor']
  #   }))
  #
  #   # Check all sub-elements in list have length 2 and have correct type
  #   assert(len(outputCorrect) == 2)
  #   for item in outputCorrect:
  #     assert(isinstance(item, list))
  #     assert(len(item) == 2)
  #
  #   # Check ordering is done correctly
  #   assert(outputCorrect[0][1] == 'C major')
  #   assert(outputCorrect[1][1] == 'D minor')
  #
  #   # Check each key has the correct time
  #   assert(outputCorrect[0][0] == 57.213968253)
  #   assert(outputCorrect[1][0] == 100.218478253)

  def test_get_key_at_time(self):
    # Assert we get None returned when no key change data is set within the class
    assert(self.calmaInstance.get_key_at_time(1) == None)
    assert(self.calmaInstance.get_key_at_time(-1) == None)
    assert(self.calmaInstance.get_key_at_time(100) == None)

    # Check our lambda function returns closest key change to inputted value
    self.calmaInstance.get_features_track('http://archive.org/download/dbt2004-05-08.4011s.flac16/dbt2004-05-08d1t02.flac')
    assert(self.calmaInstance.get_key_at_time(0) == 'G minor')
    assert(self.calmaInstance.get_key_at_time(1) == 'D minor')
    assert(self.calmaInstance.get_key_at_time(115) == 'G minor')
    assert(self.calmaInstance.get_key_at_time(135) == 'G minor')
    assert(self.calmaInstance.get_key_at_time(219) == 'Bb major')
    assert(self.calmaInstance.get_key_at_time(223) == 'D minor')

    # Check lower bounds for our function
    assert(self.calmaInstance.get_key_at_time(-1) == None)

  def test_extract_zip(self):
    # Check that returned object is of type string
    zipText = self.calmaInstance.extract_zip('http://calma.linkedmusic.org/data/ff/track_ffd10d11-e817-4ef8-84ce-f6d29b6341c9/analysis_blob_402a498d-ebbd'
                                     '-41b4-aaa6-ebe8145dc403.tar.bz2')
    assert(type(zipText) == str)

    # Provide GZIP file, assert that function returns False due to invalid URL extension type
    # incorrectZip = self.calmaInstance.extract_zip('incorrect_url')
