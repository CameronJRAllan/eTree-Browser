# Get list of all performer URLs

# For each performer URL

# Calculate query

# Execute query

# Iterate to fetch MusicBrainz link and weight

# Threshold value?

# Store in hash table

class GroupArtists():
  def __init__(self):
    self.sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
    self.sparql.setReturnFormat(JSON)

    self.performer_urls = fetch_performer_urls()
    self.fetch_musicbrainz_urls(self.performer_urls)
    self.grouped_artists = {}

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

      sparql.setQuery(queryString)

      return sparql.query().convert()

  def fetch_musicbrainz_urls(self, performer_urls):
    for result in performer_urls['results']['bindings']:
        generate_musicbrainz_query(result['performer']['value'])
    return

  def generate_musicbrainz_query(self, performer_url):
    queryString = """
                    PREFIX sim: <http://purl.org/ontology/similarity/>

                    SELECT DISTINCT ?s ?weight ?musicbrainz {
                    ?s <http://purl.org/ontology/similarity/subject> <%s>.
                    ?s sim:weight ?weight.
                    ?s sim:object ?musicbrainz
                    } GROUP BY ?s ?weight ?musicbrainz
              """ % performer_url

    sparql.setQuery(queryString)

    results = sparql.query().convert()

    for result in results:
        for value in result:
            print(str(value) + ': ' + str(result[value]['value']))