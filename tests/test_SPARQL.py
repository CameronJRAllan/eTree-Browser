import sys
sys.path.append("..")
from unittest import TestCase
import pytest
import sparql

# NOTE TO THE READER
# These tests are designed in mind to be run with Py.Test, the IDE used during programming was PyCharm
class TestSPARQL(TestCase):
  def test_getTracklist(self):
    sparqlInstance = sparql.SPARQL()
    validResults = sparqlInstance.getTracklist('Mogwai Live at The Forum on 1999-10-16')
    assert(type(validResults) == type(dict()))

  def test_getArtistReleases(self):
    sparqlInstance = sparql.SPARQL()

    # Test that a made up band has no results
    releasesByName = sparqlInstance.getArtistReleases('name', 'A Made up Band Name', '', '')
    assert(len(releasesByName['results']['bindings']) == 0)

    # Test that a real band has some results returned
    releasesByName = sparqlInstance.getArtistReleases('name', 'Mogwai', '', '')
    assert(type(releasesByName) == type(dict()))
    assert(len(releasesByName['results']['bindings']) > 0)

    # Test getting artists matching particular genre:
    releasesByName = sparqlInstance.getArtistReleases('genre', 'folktronica', '?genre', '?performer etree:mbTag ?genre.\n')
    assert(type(releasesByName) == type(dict()))
    assert(len(releasesByName['results']['bindings']) > 0)

  def test_executeString(self):
    sparqlInstance = sparql.SPARQL()
    with pytest.raises(TypeError):
      sparqlInstance.executeString('{{ }}')

  def test_dateRange(self):
    sparqlInstance = sparql.SPARQL()

    # Assert a range of 0 gives back an empty string
    assert(sparqlInstance.dateRange('2017-01-01', '2017-01-01') == '')

    # Assert a range of 5 gives an appropriate FILTER string
    rangeOfFive = sparqlInstance.dateRange('2017-01-01', '2017-01-06')
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
    sparqlInstance = sparql.SPARQL()

    # Check name filter parsing
    nameFilter = sparqlInstance.textParse(['My Favourite Band'], 1)
    assert(nameFilter.count('||') == 0)
    assert(nameFilter.count('?name') == 1)
    assert('My Favourite Band' in nameFilter)

    # Check genre filter parsing
    genreFilter = sparqlInstance.textParse(['Folk', 'Abstract Obscure Math-Rock'], 2)
    assert(genreFilter.count('||') == 1)
    assert(genreFilter.count('?genre') == 2)
    assert('Folk' in genreFilter)
    assert('Abstract Obscure Math-Rock' in genreFilter)

    # Check location filter parsing
    locationFilter = sparqlInstance.textParse(['Manchester, UK', 'New York, USA', 'Comrie, Perthshire, Scotland'], 3)
    assert(locationFilter.count('||') == 2)
    assert(locationFilter.count('?place') == 3)
    assert('Manchester, UK' in locationFilter)
    assert('New York, USA' in locationFilter)
    assert('Comrie, Perthshire, Scotland' in locationFilter)

    # Check that an empty input gives an appropriate response
    assert(sparqlInstance.textParse([], 1) is '')
    assert(sparqlInstance.textParse([], 2) is '')
    assert(sparqlInstance.textParse([], 3) is '')

  # def test_performSearch(self):
  #   self.fail()
