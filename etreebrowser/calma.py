from SPARQLWrapper import SPARQLWrapper, JSON, POSTDIRECTLY
import requests
from urlextract import URLExtract
import tarfile
import rdflib
import urllib.request
import traceback

class Calma():
  def __init__(self):
    """
    Initializes an instance of the Calma class.

    The Calma class is used for all interfacing with the feature extraction tools available at the end-point provided by Sean Bechhofer's research and work.

    """
    self.sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
    self.sparql.setReturnFormat(JSON)
    self.sparql.setMethod("POST")
    self.extractURL = URLExtract()
    self.keyInfo = None
    self.loudnessValues = None
    self.loudnessInfo = None

  def get_features_track(self, trackAudioURL):
    self.keyInfo = None
    self.loudnessValues = None
    self.loudnessInfo = None

    # http://archive.org/download/dbt2004-05-08.4011s.flac16/dbt2004-05-08d1t02.flac
    # Get parent sub-event for this track
    self.sparql.setQuery("""
                            PREFIX etree:<http://etree.linkedmusic.org/vocab/>
                            PREFIX calma: <http://calma.linkedmusic.org/vocab/>
                            
                            SELECT * {{
                            ?s etree:audio <{0}>.
                            }} LIMIT 1
                         """.format(trackAudioURL))

    subEvent = self.sparql.query().convert()
    if len(subEvent['results']['bindings']) > 0:
      trackURL = self.sparql.query().convert()['results']['bindings'][0]['s']['value']
    else:
      print('Returning false, not found')
      return False

    self.sparql.setQuery("""
                            PREFIX etree:<http://etree.linkedmusic.org/vocab/>
                            PREFIX calma: <http://calma.linkedmusic.org/vocab/>
                            
                            SELECT * {{
                            <{0}> calma:data ?o.
                            }}
                         """.format(trackURL))
    calmaURL = self.sparql.query().convert()

    # If no calma data found for this URL
    if len(calmaURL['results']['bindings']) == 0:
      print('Returning false, not found')
      return False
    else:
      self.set_new_track_calma(calmaURL['results']['bindings'][0]['o']['value'])
      return True

  def set_new_track_calma(self, calmaURL):
    self.keyInfo = self.get_calma_data(calmaURL, 'key')
    self.segmentInfo = self.get_calma_data(calmaURL, 'segmentation')
    self.loudnessInfo = self.get_calma_data(calmaURL, 'loudness')

  def get_calma_data(self, calmaURL, feature):
    if feature == "key":
      featureURL = "http://vamp-plugins.org/rdf/plugins/qm-vamp-plugins#qm-keydetector"
    elif feature == "loudness":
      featureURL = "http://vamp-plugins.org/rdf/plugins/vamp-libxtract#loudness"
    elif feature == "segmentation":
      featureURL = "http://vamp-plugins.org/rdf/plugins/qm-vamp-plugins#qm-segmenter_output_segmentation"
    else:
      raise("feature variable / parameter error")

    # Get top-level analysis information
    url = calmaURL + '/analyses.ttl'
    self.duration = self.retrieve_duration_from_analyses(url)

    r = requests.get(url, stream=True)
    g = rdflib.Graph()
    g.parse(r.raw, format="n3")

    # Get blob information for key changes
    for subject, predicate, obj in g:
      if str(obj) == featureURL:
        r = requests.get(str(subject), stream=True)
        g = rdflib.Graph()
        g.parse(r.raw, format="n3")
        for subject, predicate, obj in g:
          if str(predicate) == 'http://calma.linkedmusic.org/vocab/feature_blob':
            # Get blob contents
            g = rdflib.Graph()
            blobContents = self.extract_zip(obj)

            if feature == "key":
              return self.retrieve_events_blob(blobContents, "key")
            if feature == "segmentation":
              return self.retrieve_events_blob(blobContents, "segment")
            elif feature == "loudness":
              self.retrieve_loudness_from_blob(blobContents)

  def retrieve_events_blob(self, blob, featureType):
    g = rdflib.Graph()
    g.parse(data=blob, format="n3")

    # List of predicates to fetch
    tripleList = ['event:time', 'rdfs:label']
    events = []

    # Iterate over subjects
    for subject in g.subjects():
      # If event found
      if "event" in subject:
        # Truncate to remove local file reference
        subject = subject[subject.find("event"):]
        dictKey = {}
        for index in tripleList:
          # Fetch predicate information
          q = """
              PREFIX timeline:<http://purl.org/NET/c4dm/timeline.owl#>
              SELECT DISTINCT ?o ?p
               WHERE {{
                  :{0} {1} ?o.
                  OPTIONAL {{?o timeline:at ?p}} .
               }}""".format(subject, index)

          qres = g.query(q)
          for i, e in qres:
            # If label found
            if not e:
              dictKey[featureType] = str(i)
            # If time reference found
            else:
              dictKey['time'] = float(e.replace("S", "").replace("PT", ""))

        sublist = [dictKey['time'], dictKey[featureType]]

        # Append dict of key info to events list
        if sublist not in events: events.append(sublist)

    # Sort by time and remove duplicates
    events.sort(key=lambda sublist: sublist[0])

    return events

    # Extract relevant information in blob
    # eventList = {}
    # for subject in g.subjects():
    #   for object in g.objects(subject=subject):
    #
    #     # Add to dictionary of events, times and labels
    #     if str(subject) not in eventList and 'file://' in str(subject):
    #       eventList[str(subject)] = []
    #     if 'file://' in str(subject):
    #       if type(object) == rdflib.term.BNode:
    #         for obj_2 in g.objects(subject=object): eventList[str(subject)].append(str(obj_2))
    #       else:
    #         eventList[str(subject)].append(str(object))
    #
    # return self.tidy_key_change(eventList)

  def retrieve_duration_from_analyses(self, analysesURL):
    blob = requests.get(analysesURL).text
    g = rdflib.Graph()
    g.parse(data=blob, format="n3")

    q = """
        PREFIX mo:<http://purl.org/ontology/mo/>
        SELECT DISTINCT ?o
        WHERE {{
          ?s mo:encodes ?o
        }}
        """

    qres = g.query(q)

    for q in qres:

      url = str(q).replace("(rdflib.term.URIRef('", '').replace("'),)", '')

      # Parse signal TTL file into graph
      signal = requests.get(url).text
      g = rdflib.Graph()
      g.parse(data=signal, format="n3")

      q = """
        PREFIX mo:<http://purl.org/ontology/mo/>
        PREFIX timeline:<http://purl.org/NET/c4dm/timeline.owl#>
        SELECT DISTINCT ?p
        WHERE {{
          track:signal_0 mo:time ?signal.
          ?signal timeline:duration ?p.
        }}
        """

      qres = g.query(q)
      for q in qres:
        q = str(q)
        return float(q[q.find('PT') + 2:q.find('S')])

        # analysesURL = requests.get(analysesURL).text
    # analysesURL = analysesURL[analysesURL.find("mo:encodes ")+len("mo:encodes \""):]
    # analysesURL = analysesURL[:analysesURL.find('>')+1:]
    #
    # ttl = requests.get(analysesURL).text
    #
    # startIndex = ttl.find("tl:duration \"PT")+len("tl:duration \"PT")
    # endIndex = ttl.find("\"^^xsd:duration")+len("\"^^xsd:duration")
    #
    # self.duration = ttl[startIndex:endIndex].replace("""S"^^xsd:duration""",'')
    # self.duration = float(self.duration)
    # return self.duration

  def retrieve_loudness_from_blob(self, blob):
    try:
      self.loudnessValues = blob[blob.find("af:value \"")+11:-4].strip().split(" ")
      self.loudnessValues = [float(l) for l in self.loudnessValues]
      return True
    except Exception as e:
      traceback.print_exc()
      return False

  # def tidy_key_change(self, dict):
  #   # Remove duplicates
  #   for key in dict.keys():
  #     dict[key] = list(set(dict[key]))
  #     temp = list(set(dict[key]))
  #     temp = [x for x in temp if not '://' in x]
  #     dict[key] = temp
  #
  #   finalList = []
  #   # Re-create list using consistent formatting
  #   for key in dict.keys():
  #     # If sub-list has a length we were expecting
  #     if len(dict[key]) == 3:
  #       subList = []
  #       # For each item in the sub-list
  #       for subItem in list(set(dict[key])):
  #         # If this is a time of a key change
  #         if subItem[:2] == 'PT':
  #           subList.insert(0, float(subItem.replace('PT', '').replace('S', '')))
  #         # If this is the key change label
  #         if 'minor' in subItem or 'major' in subItem:
  #           subList.insert(1, subItem)
  #       # If correct length
  #       if len(subList) == 2:
  #         finalList.append(subList)
  #
  #   # Sort by time
  #   finalList.sort(key=lambda x: x[0])
  #   return finalList

  def get_key_at_time(self, time):
    if self.keyInfo and time >= 0:
      return (min(self.keyInfo, key=lambda x:abs(x[0]-time))[1])
    else:
      return None

  def extract_zip(self, zipURL):
    # Download .bz2 file to tmp directory
    file_name, headers = urllib.request.urlretrieve(zipURL)

    # Load into memory
    tar = tarfile.open(mode='r:bz2', fileobj=file_name)

    # Extract file and read into file object
    f = tar.extractfile(tar.next())
    contents = f.read()

    # Return the contents of the file, decoding the byte stream to UTF-8
    return contents.decode("utf-8")

if __name__ == "__main__":
    calma = Calma()