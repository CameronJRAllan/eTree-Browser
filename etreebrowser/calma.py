from SPARQLWrapper import SPARQLWrapper, JSON, POSTDIRECTLY
import requests
import tarfile
import rdflib
import urllib.request
import cache
from PyQt5 import QtWidgets, QtCore, QtGui
import graph
import multithreading

class Calma():
  def __init__(self):
    """
    Initializes an instance of the Calma class.

    The Calma class is used for all interfacing with the feature extraction tools available at the end-point provided by Sean Bechhofer's research and work.

    """
    self.sparql = SPARQLWrapper("https://etree.linkedmusic.org/sparql")
    self.sparql.setReturnFormat(JSON)
    self.sparql.setMethod("POST")
    self.keyInfo = None
    self.loudnessValues = None
    self.segmentInfo = None
    self.calmaCache = cache.load('calmaCache')

  def get_features_track(self, trackAudioURL):
    """
    Take a URL to a audio track, and retrieves any feature analyses information available.
    Example URL input: http://archive.org/download/dbt2004-05-08.4011s.flac16/dbt2004-05-08d1t02.flac

    Parameters
    ----------
    trackAudioURL : string
        Audio URL of track we wish to examine.
    """
    # self.keyInfo = None
    # self.loudnessValues = None
    # self.loudnessInfo = None

    # Get parent sub-event for this track
    self.sparql.setQuery("""
                            PREFIX etree:<http://etree.linkedmusic.org/vocab/>
                            PREFIX calma: <http://calma.linkedmusic.org/vocab/>
                            
                            SELECT * {{
                            ?s etree:audio <{0}>.
                            }} LIMIT 1
                         """.format(trackAudioURL))

    subEvent = self.sparql.query().convert()

    # If parent track found, retrieve parent event for said track
    if len(subEvent['results']['bindings']) > 0:
      trackURL = self.sparql.query().convert()['results']['bindings'][0]['s']['value']
    else:
      return False

    # Try and retrieve CALMA reference
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
      return False
    else:
      # Extract feature analyses for visualization
      self.set_new_track_calma(calmaURL['results']['bindings'][0]['o']['value'])
      return True

  def set_new_track_calma(self, calmaURL, **kwargs):
    """
    Takes a CALMA reference in the data-set and stores all relevant features locally.

    Parameters
    ----------
    calmaURL : string
        CALMA link reference to some feature analyses.
    """
    self.keyInfo = self.get_calma_data(calmaURL, 'key')
    self.segmentInfo = self.get_calma_data(calmaURL, 'segmentation')
    self.loudnessValues = self.get_calma_data(calmaURL, 'loudness')
    self.duration = self.get_duration_track(calmaURL)

    try:
      kwargs['finished_set_new_track'].emit(self.loudnessValues, self.keyInfo, self.segmentInfo, self.duration, kwargs)
    except KeyError as k:
      return

  def get_duration_track(self, calmaURL):
    # Check cache for duration
    try:
      self.duration = self.calmaCache[calmaURL]['duration']
    # If not in cache, continue to retrieve duration
    except (ValueError, KeyError) as v:
      self.duration = self.retrieve_duration_from_analyses(calmaURL + '/analyses.ttl')
      self.save_new_calma_cache(calmaURL, 'duration', self.duration)

    return self.duration

  def get_calma_data(self, calmaURL, feature):
    """
    Takes a CALMA reference in the data-set and stores all relevant features locally.

    Parameters
    ----------
    calmaURL : string
        CALMA link reference to some feature analyses.
    feature : string
        Desired feature, i.e. loudness, key changes or segmentation.
    """

    # Check cache first for cache
    try:
      data = self.calmaCache[calmaURL][feature]
      print('in cache')
      return data
    # If not in cache, continue to retrieve CALMA data
    except (ValueError, KeyError) as v:
      print('exception: {0}'.format(v))
      pass

    return self.iterate_graph_for_feature(calmaURL, feature)

  def iterate_graph_for_feature(self, calmaURL, feature):
    """
    Iterates a feature URI for events stored.

    Parameters
    ----------
    calmaURL : string
        CALMA link reference to some feature analyses.
    feature : string
        Desired feature, i.e. loudness, key changes or segmentation.
    """

    featureURL = self.get_feature_url(feature)

    # Get top-level analysis information
    url = calmaURL + '/analyses.ttl'
    r = requests.get(url, stream=True)
    g = rdflib.Graph()
    g.parse(r.raw, format="n3")

    # Iterate graph
    for subject, predicate, obj in g:

      # If matching object reference found
      if str(obj) == featureURL:

        # Retrieve URL referenced in this object
        r = requests.get(str(subject), stream=True)
        g = rdflib.Graph()
        g.parse(r.raw, format="n3")

        # Iterate to find BLOB for this feature
        for subject, predicate, obj in g:
          if str(predicate) == 'http://calma.linkedmusic.org/vocab/feature_blob':
            # Get blob contents
            g = rdflib.Graph()
            blobContents = self.extract_zip(obj)

            events = self.get_feature_events(blobContents, feature)

            self.save_new_calma_cache(calmaURL, feature, events)

            return events

  def get_feature_events(self, blob, feature):
    """
    Takes a blob for analyses and a feature, and returns that feature events.

    Parameters
    ----------
    blob : string
        Blob contained within .bz2 file.
    feature : string
        Desired feature, i.e. loudness, key changes or segmentation.
    """

    # Pass blob contents in event extractor function
    if feature == "key":
      return self.retrieve_events_blob(blob, "key")
    elif feature == "segmentation":
      return self.retrieve_events_blob(blob, "segment")
    elif feature == "loudness":
      return self.retrieve_loudness_from_blob(blob)
    else:
      raise ("Feature name error")

  def get_feature_url(self, feature):
    """
    Takes a feature and returns the object for that feature in the .TTL file.

    Parameters
    ----------
    feature : string
        Desired feature, i.e. loudness, key changes or segmentation.
    """

    if feature == "key":
      return "http://vamp-plugins.org/rdf/plugins/qm-vamp-plugins#qm-keydetector"
    elif feature == "loudness":
      return "http://vamp-plugins.org/rdf/plugins/vamp-libxtract#loudness"
    elif feature == "segmentation":
      return "http://vamp-plugins.org/rdf/plugins/qm-vamp-plugins#qm-segmenter_output_segmentation"
    else:
      raise("Feature variable / parameter error")

  def save_new_calma_cache(self, calmaURL, feature, events):
    """
    Saves a new entry in the cache for CALMA data.

    Parameters
    ----------
    calmaURL : string
        URL of the CALMA:DATA link for future reference.
    feature : list
        Feature, i.e. loudness, key changes or segmentation.
    events : list
        The events to be saved, related with this feature.
    """

    if events == None:
      return

    # If no previous features set, create data structure
    if calmaURL not in self.calmaCache:
      self.calmaCache[calmaURL] = {}
      print('calaURL set for {0}'.format(calmaURL))
    else:
      print('url already in cache')

    # Add to cache and save
    self.calmaCache[calmaURL][feature] = events
    cache.save(self.calmaCache, 'calmaCache')
    # print('Saved for {0}, {1}'.format(calmaURL, feature))

  def retrieve_events_blob(self, blob, featureType):
    """
    Takes a blob of CALMA data, and a feature desired, and returned a structured set of
    chronological events for that feature.

    Parameters
    ----------
    blob : string
        RDF data for some feature.
    featureType : string
        Desired feature, i.e. loudness, key changes or segmentation.

    Returns
    ----------
    events : list
      List of events in chronological order.
    """
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

  def retrieve_duration_from_analyses(self, analysesURL):
    """
    Takes an analyses URL and returns the duration of that track as specified within the
    feature data.

    Parameters
    ----------
    analysesURL : string
        URl of a given CALMA feature set
    """

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

  def retrieve_loudness_from_blob(self, blob):
    """
    Takes an analyses URL and returns the loudness of that track as specified within the
    feature data.

    Parameters
    ----------
    blob : string
        Blob contents as a string, typically RDF format.

    Returns
    ----------
    hasLoudness : boolean
        Boolean indicating whether the track has valid loudness values available.
    """

    try:
      loudnessGraph = rdflib.Graph()
      q = """
        PREFIX mo:<http://purl.org/ontology/mo/>
        PREFIX timeline:<http://purl.org/NET/c4dm/timeline.owl#>
        SELECT DISTINCT ?loudness
        WHERE {{
          ?signal af:value ?loudness.
        }}
        """
      loudnessGraph.parse(data=blob, format="n3")
      qres = loudnessGraph.query(q)

      loudnessSet = False
      for q in qres:
        if not loudnessSet:
          q = str(q)
          q = q.replace("(rdflib.term.Literal('", "").replace(" '),)", "").split(" ")
          self.loudnessValues = [float(l) for l in q]
          loudnessSet = True
          return self.loudnessValues

        # self.loudnessValues = blob[blob.find("af:value \"")+11:-4].strip().split(" ")
        # self.loudnessValues = [float(l) for l in self.loudnessValues]
    except Exception as e:
      print('Exception: {0}'.format(e))
      return None

  def get_key_at_time(self, time):
    """
    Takes as input a time, and checks to see whether a key is available at this time.

    Parameters
    ----------
    time : int
        Current time of track played.

    Returns
    ----------
    key : string
      Key in event closest to this input time.
    """
    if self.keyInfo and time >= 0:
      return (min(self.keyInfo, key=lambda x:abs(x[0]-time))[1])
    else:
      return None

  def extract_zip(self, zipURL):
    """
    Takes a blob of CALMA data, and a feature desired, and returned a structured set of
    chronological events for that feature.

    Parameters
    ----------
    zipURL : string
        URL of a .zip of .bz2 file containing blob information.

    Returns
    ----------
    contents : string
      Contents of first file in ZIP URL provided.
    """

    # Download .bz2 file to tmp directory
    file_name, headers = urllib.request.urlretrieve(zipURL)

    # Load into memory
    tar = tarfile.open(mode='r:bz2', fileobj=file_name)

    # Extract file and read into file object
    f = tar.extractfile(tar.next())
    contents = f.read()

    # Return the contents of the file, decoding the byte stream to UTF-8
    return contents.decode("utf-8")

class CalmaPlotRelease(QtWidgets.QDialog):
  def __init__(self, app, title, feature):
    super().__init__()
    self.app = app
    self.calma_release(title, feature)
    self.setWindowTitle("{0} Analysis of {1}".format(feature.title(), title.title()))
    self.plotContainerWidget = QtWidgets.QWidget()

  def calma_release(self, title, feature):
    # Get CALMA references for release
    calmaLinks = self.app.sparql.get_calma_reference_release(title)

    # Create dialog and layout
    self.plotLayout = QtWidgets.QVBoxLayout()

    # Create list to store plot objects, and instance variables for looping
    self.numberCalmaDisplayed = 0
    self.max = len(calmaLinks['results']['bindings'])
    self.plots = []

    for track in calmaLinks['results']['bindings']:
      # Create a CALMA instance, and a new thread to get CALMA + plot
      self.calma = Calma()
      kwargs = {'title': track['label']['value'], 'feature': feature, 'release' : True}
      worker = multithreading.WorkerThread(self.calma.set_new_track_calma, track['calma']['value'], **kwargs)
      worker.qt_signals.finished_set_new_track.connect(self.callback_set_new_track)
      self.app.threadpool.start(worker)

  def callback_set_new_track(self, loudness, keys, segments, duration, trackInfo):
    # If not exceeded number of tracks
    if self.numberCalmaDisplayed < self.max:
      # Set correct feature
      if trackInfo['feature'] == 'key':
        features = keys
      else:
        features = segments

      # Create a new plot and add widget to dialog
      self.plots.append(graph.CalmaPlot(600, 600, 100, True))
      self.plots[self.numberCalmaDisplayed].plot_calma_data(loudness, features, duration, trackInfo['feature'], title=trackInfo['title'],
                                                            release=True)
      self.plotLayout.addWidget(self.plots[self.numberCalmaDisplayed])
      self.numberCalmaDisplayed += 1

      # If last track
      if self.numberCalmaDisplayed == self.max - 1:
        # Set final properties for dialog & show to user
        self.plotContainerWidget.setLayout(self.plotLayout)

        # Create scroll area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(self.plotContainerWidget)
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(1280)
        scroll.setMinimumHeight(720)

        # Create scroll layout and add plots
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(scroll)
        self.setLayout(self.layout)
        scroll.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.show()