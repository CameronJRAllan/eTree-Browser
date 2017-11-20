import sys
sys.path.append("..")
from unittest import TestCase
import pytest
import sparql
import pytest_mock
from pytestqt import qtbot
# NOTE TO THE READER
# These tests are designed in mind to be run with Py.Test, the IDE used during programming was PyCharm
class TestSPARQL(TestCase):
  @pytest.fixture(scope="function", autouse=True)
  def setup(self):
    self.sparqlInstance = sparql.SPARQL()

  def test_getTracklist(self):
    validResults = self.sparqlInstance.get_tracklist('Mogwai Live at The Forum on 1999-10-16')
    assert(type(validResults) == type(dict()))

  def test_getArtistReleases(self):
    # Test that a made up band has no results
    releasesByName = self.sparqlInstance.get_artist_releases('name', 'A Made up Band Name', '', '')
    assert(len(releasesByName['results']['bindings']) == 0)

    # Test that a real band has some results returned
    releasesByName = self.sparqlInstance.get_artist_releases('name', 'Mogwai', '', '')
    assert(type(releasesByName) == type(dict()))
    assert(len(releasesByName['results']['bindings']) > 0)

    # Test getting artists matching particular genre:
    releasesByName = self.sparqlInstance.get_artist_releases('genre', 'folktronica', '?genre', '?performer etree:mbTag ?genre.\n')
    assert(type(releasesByName) == type(dict()))
    assert(len(releasesByName['results']['bindings']) > 0)

    releasesByName = self.sparqlInstance.get_artist_releases('name', ['Mogwai', 'Grateful Dead'], '', '')
    assert(type(releasesByName) == type(dict()))
    assert(len(releasesByName['results']['bindings']) > 0)

  def test_executeString(self):
    assert (isinstance(self.sparqlInstance.execute_string('{{ }}'), Exception))

  def test_dateRange(self):
    # Assert a range of 0 gives back an empty string
    assert(self.sparqlInstance.date_range('2017-01-01', '2017-01-01') == '')

    # Assert a range of 5 gives an appropriate FILTER string
    rangeOfFive = self.sparqlInstance.date_range('2017-01-01', '2017-01-06')
    assert('FILTER' in rangeOfFive)
    assert(str(rangeOfFive).count('str(?date)') == 6)

    # Check bounds of range calculated
    assert('2017-01-01' in rangeOfFive)
    assert('2017-01-02' in rangeOfFive)
    assert('2017-01-03' in rangeOfFive)
    assert('2017-01-04' in rangeOfFive)
    assert('2017-01-05' in rangeOfFive)
    assert('2017-01-06' in rangeOfFive)

    assert('2016-12-30' not in rangeOfFive)
    assert('2017-01-07' not in rangeOfFive)

  def test_textParse(self):
    # Check name filter parsing
    nameFilter = self.sparqlInstance.text_parse(['My Favourite Band'], 1)
    assert(nameFilter.count('||') == 0)
    assert(nameFilter.count('?name') == 1)
    assert('My Favourite Band' in nameFilter)

    # Check genre filter parsing
    genreFilter = self.sparqlInstance.text_parse(['Folk', 'Abstract Obscure Math-Rock'], 2)
    assert(genreFilter.count('||') == 1)
    assert(genreFilter.count('?genre') == 2)
    assert('Folk' in genreFilter)
    assert('Abstract Obscure Math-Rock' in genreFilter)

    # Check location filter parsing
    locationFilter = self.sparqlInstance.text_parse(['Manchester, UK', 'New York, USA', 'Comrie, Perthshire, Scotland'], 3)
    assert(locationFilter.count('||') == 2)
    assert(locationFilter.count('?place') == 3)
    assert('Manchester, UK' in locationFilter)
    assert('New York, USA' in locationFilter)
    assert('Comrie, Perthshire, Scotland' in locationFilter)

    # Check that an empty input gives an appropriate response
    assert(self.sparqlInstance.text_parse([], 1) is '')
    assert(self.sparqlInstance.text_parse([], 2) is '')
    assert(self.sparqlInstance.text_parse([], 3) is '')

  def test_get_artist_from_tracklist(self):
    name = self.sparqlInstance.get_artist_from_tracklist("http://etree.linkedmusic.org/track/mogwai1999-10-16.flac16-1")
    assert(name == 'Mogwai')

  def test_get_release_subproperties(self):
    subproperties = self.sparqlInstance.get_release_subproperties("http://etree.linkedmusic.org/performance/mogwai1999-10-16.flac16")

    # isCorrect = dict.fromkeys(["date", "label", "uploader"], False)

    for p in subproperties['results']['bindings']:
      if p['p']['value'] == 'http://etree.linkedmusic.org/vocab/uploader':
        assert(p['o']['value'] == 'iyiiki@gmail.com')
      if p['p']['value'] == 'http://etree.linkedmusic.org/vocab/date':
        assert (p['o']['value'] == '1999-10-16')
      if p['p']['value'] == 'http://www.w3.org/2004/02/skos/core#prefLabel':
        assert (p['o']['value'] == 'Mogwai Live at The Forum on 1999-10-16')

  def test_get_venue_information(self):

    resultsDict = self.sparqlInstance.get_venue_information("Mogwai Live at The Forum on 1999-10-16")
    assert(isinstance(resultsDict, dict))
    assert(isinstance(resultsDict['geoname'], str))
    assert(isinstance(resultsDict['lastfm'], str))

  def test_parse_order_by(self):
    artistTest = self.sparqlInstance.parse_order_by("Artist")
    assert(isinstance(artistTest, str))
    assert(artistTest == "ORDER BY ?name")

    locationTest = self.sparqlInstance.parse_order_by("Location")
    assert(isinstance(locationTest, str))
    assert(locationTest == "ORDER BY ?place")

    dateTest = self.sparqlInstance.parse_order_by("Date")
    assert(isinstance(dateTest, str))
    assert(dateTest == "ORDER BY ?date")

    labelTest = self.sparqlInstance.parse_order_by("Label")
    assert(isinstance(labelTest, str))
    assert(labelTest == "ORDER BY ?label")

  def test_get_tracklist_grouped(self):
    validResults = self.sparqlInstance.get_tracklist_grouped('Mogwai Live at The Forum on 1999-10-16')
    assert(type(validResults) == type(dict()))

  # assert(subproperties['results']['bindings'][0]['http://etree.linkedmusic.org/vocab/date']['value'] == "1999-10-16")
  # def test_performSearch(self):
  #   self.fail()
