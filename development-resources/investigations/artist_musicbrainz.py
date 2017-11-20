# Get list of all performer URLs

# For each performer URL

# Calculate query

# Execute query

# Iterate to fetch MusicBrainz link and weight

# Threshold value?

# Store in hash table
from SPARQLWrapper import SPARQLWrapper, JSON
import sys, pickle, os
import numpy
import matplotlib.pyplot as plt

class GroupArtists():
  def __init__(self):
    self.sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
    self.sparql.setReturnFormat(JSON)
    self.sparql.setTimeout(120)

    # self.similarity_list = []
    # self.grouped_artists = {} # self.load()
    # # print('Length upon load ' + str(len(self.grouped_artists)))
    # self.performer_urls = self.fetch_performer_urls()
    # self.fetch_musicbrainz_urls(self.performer_urls)

    # Generate histogram of MusicBrainz similarities
    # self.hist, self.bin_edges = numpy.histogram(self.similarity_list, bins='auto')
    #
    # plt.bar(self.bin_edges[:-1], self.hist, width=1)
    #
    # plt.xlim(min(self.bin_edges), max(self.bin_edges))
    # plt.show()

  def fetch_performer_urls(self):
      queryString = """
                PREFIX etree:<http://etree.linkedmusic.org/vocab/>
                PREFIX mo:<http://purl.org/ontology/mo/>
                PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
                PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
                PREFIX timeline:<http://purl.org/NET/c4dm/timeline.owl#>
                PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                SELECT DISTINCT ?performer ?name  WHERE
                {
                      ?performer foaf:name ?name.
                      ?art mo:performer ?performer.
                } GROUP BY ?performer ?name
              """

      self.sparql.setQuery(queryString)

      return self.sparql.query().convert()

  def fetch_musicbrainz_urls(self, performer_urls):
    for result in performer_urls['results']['bindings']:
      self.generate_musicbrainz_query(result['performer']['value'], result['name']['value'])
    return

  def generate_musicbrainz_query(self, performer_url, performer_name):
    queryString = """
                    PREFIX sim: <http://purl.org/ontology/similarity/>

                    SELECT DISTINCT ?s ?weight ?musicbrainz {
                    ?s <http://purl.org/ontology/similarity/subject> <%s>.
                    ?s sim:weight ?weight.
                    ?s sim:object ?musicbrainz
                    } GROUP BY ?s ?weight ?musicbrainz
              """ % performer_url

    self.sparql.setQuery(queryString)

    results = self.sparql.query().convert()

    for result in results['results']['bindings']:
        if 'musicbrainz' in result['musicbrainz']['value']:
          if result['musicbrainz']['value'] not in self.grouped_artists:
            self.grouped_artists[result['musicbrainz']['value']] = []
          if performer_name not in self.grouped_artists[result['musicbrainz']['value']]:
            print(performer_name)
            self.grouped_artists[result['musicbrainz']['value']].append(performer_name)
          self.save()
    return

  def save(self):
    dir = os.path.join(os.path.dirname(__file__), 'grouped_musicbrainz_no_threshold.pkl')
    with open(dir, 'wb') as f:
      pickle.dump(self.grouped_artists, f, pickle.HIGHEST_PROTOCOL)

  def load(self):
    dir = os.path.join(os.path.dirname(__file__), 'grouped_musicbrainz_no_threshold.pkl')
    with open(dir, 'rb') as f:
      return pickle.load(f)

if __name__ == '__main__':
  instance = GroupArtists()
