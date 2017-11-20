import sys
from SPARQLWrapper import SPARQLWrapper, JSON, POSTDIRECTLY
import cache
import statistics as s

class AudioFormat():
  def __init__(self):
    self.sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
    self.sparql.setReturnFormat(JSON)
    self.sparql.setMethod("POST")

    performances = cache.load('list_all_performances')
    # performances = self.get_all_performances()
    # cache.save(performances, 'list_all_performances')
    print('Got perm')
    self.examine_tracklists(performances)

  def examine_tracklists(self, performances):
    count = {'mp3': 0, 'flac24': 0, 'flac16': 0, 'mp3_vbr': 0, 'shn' : 0, 'ogg': 0, 'wav' : 0}
    numSingleFormat = 0
    countUnique = {'mp3': 0, 'flac24': 0, 'flac16': 0, 'mp3_vbr': 0, 'shn' : 0, 'ogg': 0, 'wav' : 0}
    numFormatsFound = []

    for single in performances['results']['bindings']: # [:40]
      tracklist = self.get_tracklist(single['label']['value'])
      print(single['label']['value'])
      formatsFound = []
      for item in tracklist['results']['bindings']:

        extension = item['audio']['value'][item['audio']['value'].rfind('.') + 1:]

        if 'mp3' not in extension and 'flac' not in extension:
          formatsFound.append(extension)
        else:
          if 'mp3' in extension:
            formatsFound.append(self.subtype_mp3(item['audio']['value']))
          if 'flac' in extension:
            formatsFound.append(self.subtype_flac(item['audio']['value']))

      if len(list(set(formatsFound))) == 1:
        numSingleFormat += 1
        countUnique[formatsFound[0]] += 1

      numFormatsFound.append(len(list(set(formatsFound))))

      for format in list(set(formatsFound)):
        count[format] += 1

    for k in count.keys():
      print(str(k) + ': ' + str(count[k]))
    print('\n\nUnique count: ' + str(numSingleFormat))
    for k in countUnique.keys():
      print(str(k) + ': ' + str(countUnique[k]))
    print(s.mean(numFormatsFound))

  def subtype_mp3(self, url):
    final_7 = url[url.rfind('.') - 3:]
    if 'vbr' in final_7.lower():
      return 'mp3_vbr'
    if '64kb' in final_7.lower():
      return 'mp3_64kb'
    else:
      return 'mp3'

  def subtype_flac(self, url):
    filename = url[url.rfind('/') + 1:]
    if 'flac24' in url.lower():
      return 'flac24'
    else:
      return 'flac16'

  def get_all_performances(self):
    self.sparql.setQuery("""
          PREFIX etree:<http://etree.linkedmusic.org/vocab/>
          PREFIX mo:<http://purl.org/ontology/mo/>
          PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
          PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
          PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

          SELECT DISTINCT ?performer ?name ?label ?place WHERE 
          {      
                ?art skos:prefLabel ?label.  
                ?art event:place ?location.
                ?location etree:location ?place.
                ?performer foaf:name ?name.
                ?art mo:performer ?performer.
          }  GROUP BY (?name) LIMIT 2   
          """)

    return self.sparql.query().convert()

  def get_tracklist(self, label):
    self.sparql.setQuery("""
                          PREFIX etree:<http://etree.linkedmusic.org/vocab/>
                          PREFIX mo:<http://purl.org/ontology/mo/>
                          PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
                          PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
                          PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
              
                            SELECT DISTINCT ?audio ?label ?num {{
                              ?perf event:hasSubEvent ?tracklist.
                              ?tracklist skos:prefLabel ?label.
                              ?tracklist etree:number ?num.
                              ?tracklist etree:audio ?audio.
                              ?perf rdf:type mo:Performance.
                              ?perf skos:prefLabel "{0}".
                          }} GROUP BY ?label ?audio ?num ORDER BY ?num 
                          """.format(label))
    return self.sparql.query().convert()

if __name__ == '__main__':
  instance = AudioFormat()