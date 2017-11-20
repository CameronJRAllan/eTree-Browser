import sys
sys.path.append("..")
import os
import calma
from SPARQLWrapper import SPARQLWrapper, JSON, POSTDIRECTLY
import sparql
class keySummaries():
  def __init__(self, artist):
    self.sparqlInstance = sparql.SPARQL()
    self.calmaHandler = calma.Calma()

    # Get releases for this artist
    releases = self.sparqlInstance.get_artist_releases('name', artist, '', '')

    # Get tracks for this release with relevant calma data
    for release in releases['results']['bindings']:
      keyInfo = self.get_calma(release['prefLabel']['value'])

      # If valid data resulted
      if keyInfo != False:
        self.process_data(keyInfo['results']['bindings'])

  def get_calma(self, label):
    calmaResults = self.sparqlInstance.execute_string("""
            PREFIX etree:<http://etree.linkedmusic.org/vocab/>
            PREFIX mo:<http://purl.org/ontology/mo/>
            PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
            PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
            PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX calma: <http://calma.linkedmusic.org/vocab/>

              SELECT DISTINCT ?audio ?label ?num ?tracklist ?calma {{
                ?perf event:hasSubEvent ?tracklist.
                ?tracklist calma:data ?calma.
                ?tracklist skos:prefLabel ?label.
                ?tracklist etree:number ?num.
                ?tracklist etree:audio ?audio.
                ?perf rdf:type mo:Performance.
                ?perf skos:prefLabel "{0}".
            }} 
          """.format(label))

    # If no calma data found for this URL
    if len(calmaResults['results']['bindings']) == 0:
      return False
    else:
      # Start generating new JSON here
      for track in calmaResults['results']['bindings']:
        track['key_changes'] = self.calmaHandler.get_calma_data(track['calma']['value'])
      return calmaResults

  def process_data(self, tracks):
    return

    # Get most common keys (in first, second and third quadrants?)
    # Get most common key overall
    # Store eTree link in each as well
    # Graph the data


if __name__ == "__main__":
  keySummaries = keySummaries('Drive-By Truckers')