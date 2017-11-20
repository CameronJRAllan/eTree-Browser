import os
import sparql
def test_mock_get_tracklist(mocker):
  sparqlInstance = sparql.SPARQL()
  mocker.spy(sparqlInstance, 'get_tracklist')

  sparqlInstance.get_tracklist('test')
  assert(sparqlInstance.get_tracklist.call_count == 1)
