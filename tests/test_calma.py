import sys
sys.path.append("..")
from unittest import TestCase
import pytest
import calma
import cache
import mock
import cache
from PyQt5 import QtCore

class SignalsMock(QtCore.QObject):
  finishedSetTrackSignal = QtCore.pyqtSignal(object, object, object, float, dict)

class TestCalma(TestCase):
  @pytest.fixture(scope="function", autouse=True)
  def setup(self):
    self.cache = cache.Cache()
    self.calmaInstance = calma.Calma(self.cache)

  def test_initial_state(self):
    assert(self.calmaInstance.keyInfo == None)
    assert(self.calmaInstance.loudnessValues == None)

  @mock.patch('calma.Calma.set_new_track_calma')
  def test_get_features_track(self, setNewTrackMock):
    # Check that an invalid URL does not return calma data
    assert(self.calmaInstance.get_features_track('http://InvalidURL.com') == False)

    # Check a valid URL, with no calma data, returns false
    assert(self.calmaInstance.get_features_track('http://ia601405.us.archive.org/8/items/mogwai1999-10-16.flac16/mogwai1999-10-16d1t04.mp3') == False)

    # Check that a correct URL returns true
    assert(self.calmaInstance.get_features_track('http://archive.org/download/dbt2004-05-08.4011s.flac16/dbt2004-05-08d1t02.flac') == True)
    assert(setNewTrackMock.called)

  def test_get_calma_data_key(self):
    # Check that we get a list returned from this information from a valid URL
    calmaData = self.calmaInstance.get_calma_data('http://calma.linkedmusic.org/data/9a/track_9a777890-c7be-4133-9e8a-d83c1347af51/', 'key')

    # Check that every sub-list contains 2 elements
    # Check that the 1st element in every sub-element in list is a float, and the second a string
    for item in calmaData:
      assert(len(item) == 2)

      assert(isinstance(item[0], float))
      assert(isinstance(item[1], str))

  def test_get_key_at_time(self):
    # Assert we get None returned when no key change data is set within the class
    assert(self.calmaInstance.get_key_at_time(1) == None)
    assert(self.calmaInstance.get_key_at_time(-1) == None)
    assert(self.calmaInstance.get_key_at_time(100) == None)

    signals = SignalsMock()
    # Check our lambda function returns closest key change to inputted value
    kwargs = {'finished_set_new_track' : signals.finishedSetTrackSignal}
    self.calmaInstance.set_new_track_calma('http://calma.linkedmusic.org/data/0a/track_0a6cee42-9e00-4ecd-a11e-ce163eeb2ed5', **kwargs)
    assert(self.calmaInstance.get_key_at_time(0) == 'E minor')
    assert(self.calmaInstance.get_key_at_time(1) == 'C major')
    assert(isinstance(self.calmaInstance.get_key_at_time(1), str))
    # Check lower bounds for our function
    assert(self.calmaInstance.get_key_at_time(-1) == None)

  def test_extract_zip(self):
    # Check that returned object is of type string
    zipText = self.calmaInstance.extract_zip('http://calma.linkedmusic.org/data/ff/track_ffd10d11-e817-4ef8-84ce-f6d29b6341c9/analysis_blob_402a498d-ebbd'
                                     '-41b4-aaa6-ebe8145dc403.tar.bz2')
    assert(type(zipText) == str)

    # Provide GZIP file, assert that function returns False due to invalid URL extension type
    # incorrectZip = self.calmaInstance.extract_zip('incorrect_url')

  def test_retrieve_duration_from_analyses(self):
    url = 'http://calma.linkedmusic.org/data/1a/track_1ae4d52e-92f8-4a46-b594-b71e60eea5c1/analyses.ttl'
    duration = self.calmaInstance.retrieve_duration_from_analyses(url)
    assert(duration == 468.55)

  def test_retrieve_loudness_from_blob(self):
    blob = """@prefix dc: <http://purl.org/dc/elements/1.1/> .
              @prefix mo: <http://purl.org/ontology/mo/> .
              @prefix af: <http://purl.org/ontology/af/> .
              @prefix foaf: <http://xmlns.com/foaf/0.1/> . 
              @prefix event: <http://purl.org/NET/c4dm/event.owl#> .
              @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
              @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
              @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
              @prefix tl: <http://purl.org/NET/c4dm/timeline.owl#> .
              @prefix vamp: <http://purl.org/ontology/vamp/> .
              @prefix : <#> .
              
              <file:///import/c4dm-01/calma/temp/ALO2014-02-21.flac16/ALO2014-02-21.flac16/ALO2014-02-21d1T04.wav> a mo:AudioFile ;
                  mo:encodes :signal_0.
              
              :signal_0 a mo:Signal ;
                  mo:time [
                      a tl:Interval ;
                      tl:onTimeLine :signal_timeline_0
                  ] .
              
              :signal_timeline_0 a tl:Timeline .
              
              :transform_1_loudness a vamp:Transform ;
                  vamp:plugin <http://vamp-plugins.org/rdf/plugins/vamp-libxtract#loudness> ;
                  vamp:step_size "1024"^^xsd:int ; 
                  vamp:block_size "1024"^^xsd:int ; 
                  vamp:sample_rate "44100"^^xsd:float ; 
                  vamp:output <http://vamp-plugins.org/rdf/plugins/vamp-libxtract#loudness_output_loudness> .
              
              :signal_type_2 rdfs:subClassOf af:Signal ;
                  dc:title "Loudness" ;
                  dc:format "" ;
                  dc:description "Extract the loudness of an audio signal from its spectrum" .
              
              
              :feature_timeline_3 a tl:DiscreteTimeLine .
              
              :feature_timeline_map_3 a tl:UniformSamplingWindowingMap ;
                  tl:rangeTimeLine :feature_timeline_3 ;
                  tl:domainTimeLine :signal_timeline_0 ;
                  tl:sampleRate "44100"^^xsd:int ;
                  tl:windowLength "1024"^^xsd:int ;
                  tl:hopSize "1024"^^xsd:int .
              
              :signal_0 af:signal_feature :feature_3 .
              
              :feature_3 a :signal_type_2 ;
                  mo:time [
                      a tl:Interval ;
                      tl:onTimeLine :feature_timeline_3 ;
                  ] ;
                  vamp:computed_by :transform_1_loudness ;
                  af:dimensions "1 0" ;
                  af:value "4.03164 4.34237 4.23068 4.14483 3.98553 4.86882 5.20035 5.17655 4.50689 4.15754 4.13334 4.09556 4.06728 3.99344 4.90712 5.1524 5.05974 4.92569 4.68533 4.72865 4.55484 4.63155 4.42642 4.12528 4.16671 " .
              """
    loudness = self.calmaInstance.retrieve_loudness_from_blob(blob)
    assert(type(loudness) is list)
    assert(len(loudness) == 25)

  @mock.patch('cache.Cache.save')
  def test_save_new_calma_cache(self, cache):
    self.calmaInstance.save_new_calma_cache('url', 'feature', 'events')
    # assert(self.calmaInstance.)
    assert(cache)

  def test_get_feature_url(self):
    assert(self.calmaInstance.get_feature_url('key') == "http://vamp-plugins.org/rdf/plugins/qm-vamp-plugins#qm-keydetector")
    assert(self.calmaInstance.get_feature_url('loudness') == "http://vamp-plugins.org/rdf/plugins/vamp-libxtract#loudness")
    assert(self.calmaInstance.get_feature_url('segmentation') == "http://vamp-plugins.org/rdf/plugins/qm-vamp-plugins#qm-segmenter_output_segmentation")

  @mock.patch('calma.Calma.retrieve_events_blob')
  def test_get_feature_events_key(self, retrieveEvents):
    blobContents = self.calmaInstance.extract_zip('http://calma.linkedmusic.org/data/75/track_75297d06-741b-448f-a32e-ee07e1b6bd72/analysis_blob_e20b428d-8eef-4b13-897a-6b1e8734f702.tar.bz2')
    self.calmaInstance.get_feature_events(blobContents, 'key')
    assert(retrieveEvents.called)

  @mock.patch('calma.Calma.retrieve_events_blob')
  def test_get_feature_events_segment(self, retrieveEvents):
    blobContents = self.calmaInstance.extract_zip('http://calma.linkedmusic.org/data/75/track_75297d06-741b-448f-a32e-ee07e1b6bd72/analysis_blob_e20b428d-8eef-4b13-897a-6b1e8734f702.tar.bz2')
    self.calmaInstance.get_feature_events(blobContents, 'segmentation')
    assert(retrieveEvents.called)

  @mock.patch('calma.Calma.retrieve_loudness_from_blob')
  def test_get_feature_events_loudness(self, retrieveEvents):
    blobContents = self.calmaInstance.extract_zip('http://calma.linkedmusic.org/data/75/track_75297d06-741b-448f-a32e-ee07e1b6bd72/analysis_blob_e20b428d-8eef-4b13-897a-6b1e8734f702.tar.bz2')
    self.calmaInstance.get_feature_events(blobContents, 'loudness')
    assert(retrieveEvents.called)

  def test_retrieve_events_blob(self):
    blobContents = self.calmaInstance.extract_zip('http://calma.linkedmusic.org/data/75/track_75297d06-741b-448f-a32e-ee07e1b6bd72/analysis_blob_e20b428d-8eef-4b13-897a-6b1e8734f702.tar.bz2')
    events = self.calmaInstance.retrieve_events_blob(blobContents, 'key')
    assert(len(events) == 40)
    for e in events:
      assert(type(e[0]) == float)
      assert(type(e[1]) == str)

  def test_retrieve_loudness_from_blob_invalid(self):
    blob = """Invalid input"""

    loudness = self.calmaInstance.retrieve_loudness_from_blob(blob)
    assert(loudness == None)

  def test_get_calma_data(self):
    events = self.calmaInstance.get_calma_data('http://calma.linkedmusic.org/data/f3/track_f3dfeae5-fa57-42b2-8ede-3446438b5067/', 'key')

    assert(len(events) == 24)
    for e in events:
      assert(type(e[0]) == float)
      assert(type(e[1]) == str)

  def test_get_calma_data_no_cache(self):
    events = self.calmaInstance.iterate_graph_for_feature('http://calma.linkedmusic.org/data/f3/track_f3dfeae5-fa57-42b2-8ede-3446438b5067/', 'key')

    assert(len(events) == 24)
    for e in events:
      assert(type(e[0]) == float)
      assert(type(e[1]) == str)