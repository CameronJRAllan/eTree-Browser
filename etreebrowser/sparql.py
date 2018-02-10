from SPARQLWrapper import SPARQLWrapper, JSON, POSTDIRECTLY
import datetime
import urllib
from PyQt5 import QtWidgets
import calma
import graph

class SPARQL():
  def __init__(self):
    """
    Initializes an instance of the SPARQL class.

    The SPARQL class is used for all interfacing with the SPARQL end-point provided from Sean Bechhofer's research and work.

    """
    self.sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
    self.sparql.setReturnFormat(JSON)
    self.sparql.setMethod("POST")

  def get_calma_reference_release(self, releaseName):
    queryString = """
            PREFIX etree:<http://etree.linkedmusic.org/vocab/>
            PREFIX mo:<http://purl.org/ontology/mo/>
            PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
            PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
            PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX calma: <http://calma.linkedmusic.org/vocab/>

            SELECT DISTINCT ?label ?calma {{
              ?perf event:hasSubEvent ?tracklist.
              ?tracklist skos:prefLabel ?label.
              ?tracklist etree:number ?num.
              ?perf rdf:type mo:Performance.
              ?perf skos:prefLabel "{0}".
              ?tracklist calma:data ?calma.
            }} ORDER BY ?num 
            """.format(releaseName)
    self.sparql.setQuery(queryString)
    return self.sparql.query().convert()

  def get_release_properties(self, releaseName):
    """
    Retrieves the properties of a given release.

    Parameters
    ----------
    releaseName : string
        Name of the release.

    Returns
    -------
    properties : dict
        The properties found.
    """
    try:
      queryGetURI = """
                      SELECT * {{
                        ?s ?p "{0}".
                      }}
                      """.format(releaseName)
      self.sparql.setQuery(queryGetURI)
      queryResults = self.sparql.query().convert()

      queryGetProperties = """
                              SELECT * {{
                                <{0}> ?p ?o.
                              }}
                           """.format(str(queryResults['results']['bindings'][0]['s']['value']))
      self.sparql.setQuery(queryGetProperties)
      return self.sparql.query().convert()
    except urllib.error.URLError as e:
      return e

  def get_release_subproperties(self, subject):
    """
    Retrieves the sub-properties of a given release.

    Parameters
    ----------
    subject : string
        The release for which we want to retrieve the sub-properties of.

    Returns
    -------
    results : dictionary
        A JSON dictionary of the properties returned.
    """
    queryGetProperties = """
                            SELECT * {{
                              <{0}> ?p ?o.
                            }}
                         """.format(str(subject))
    self.sparql.setQuery(queryGetProperties)
    try:
      return self.sparql.query().convert()
    except Exception as e:
      print(e)
      pass

  def get_tracklist(self, label):
    """
    Retrieves a track-list for a given recording.

    Parameters
    ----------
    label : string
        The label of the released used to identify the tracks which belong to it.

    Returns
    -------
    results : dict
        A JSON representation of the results returned by the end-point.
    """
    queryString = """
            PREFIX etree:<http://etree.linkedmusic.org/vocab/>
            PREFIX mo:<http://purl.org/ontology/mo/>
            PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
            PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
            PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

              SELECT DISTINCT ?audio ?label ?num ?tracklist ?name {{
                ?perf event:hasSubEvent ?tracklist.
                ?tracklist skos:prefLabel ?label.
                ?tracklist etree:number ?num.
                ?tracklist etree:audio ?audio.
                ?perf rdf:type mo:Performance.
                ?perf skos:prefLabel "{0}".
                ?perf mo:performer ?performer.
                ?performer foaf:name ?name.
            }} GROUP BY ?label ?audio ?num ORDER BY ?num 
          """.format(label)
    self.sparql.setQuery(queryString)
    return self.sparql.query().convert()

  def get_tracklist_grouped(self, label):

    queryString = """
            PREFIX etree:<http://etree.linkedmusic.org/vocab/>
            PREFIX mo:<http://purl.org/ontology/mo/>
            PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
            PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
            PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX calma: <http://calma.linkedmusic.org/vocab/>

            SELECT DISTINCT (group_concat(distinct ?audio; separator = "\\n") AS ?audio) (group_concat(distinct ?calma; separator = "\\n") AS 
            ?calma) ?label ?num ?tracklist {{
              ?perf event:hasSubEvent ?tracklist.
              ?tracklist skos:prefLabel ?label.
              ?tracklist etree:number ?num.
              ?tracklist etree:audio ?audio.
              ?perf rdf:type mo:Performance.
              ?perf skos:prefLabel "{0}".
              OPTIONAL {{?tracklist calma:data ?calma}}.
            }} ORDER BY ?num 
            """.format(label)
    self.sparql.setQuery(queryString)
    return self.sparql.query().convert()

  def get_artist_releases(self, filterField, filterStr, sparqlField, sparqlTriple):
    """
    Retrieves all the releases by a particular artist.

    Parameters
    ----------
    filterField : string
        The filter field.

    filterStr : string
        The filter string.

    sparqlField : string
        If a custom field is required (e.g genre), this is the field value required.

    sparqlTriple : string
        If a custom field is required (e.g genre), this is the triple required.

    Returns
    -------
    results : dictionary
        A JSON representation of the results returned by the end-point.
    """

    sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
    sparql.setReturnFormat(JSON)
    queryString = """
          PREFIX etree:<http://etree.linkedmusic.org/vocab/>
          PREFIX mo:<http://purl.org/ontology/mo/>
          PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
          PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
          PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

          SELECT DISTINCT ?performer ?name ?prefLabel ?place ?date {0}  WHERE 
          {{      
                ?art skos:prefLabel ?prefLabel.  
                ?art event:place ?location.
                ?location etree:location ?place.
                ?performer foaf:name ?name.
                ?art etree:date ?date.
                ?art mo:performer ?performer.
                ?art event:hasSubEvent ?tracklist.
                {1}
          """.format(sparqlField, sparqlTriple)

    # If we have multiple filters (hence type LIST)
    if type(filterStr) == list:
      # Add prefix
      queryString +='\nFILTER('

      # Add each filter statement
      for item in filterStr:
        queryString += """?{0}="{1}" ||\n""".format(filterField, item.strip())

      # Add suffix to be syntactically correct
      queryString = queryString[:-3]
      queryString += ')'

    # If we have a singlular filter (hence type STRING)
    else:
      if len(filterField) > 0:
        queryString +=  """FILTER(?{0}="{1}")""".format(filterField, filterStr)

    # Add ending line of query
    queryString += "\n}  GROUP BY (?name)"
    # Set and run query
    self.sparql.setQuery(queryString)
    return self.sparql.query().convert()

  def execute_string(self, queryString):
    """
    Executes a string representing a SPARQL query.

    Having a general purpose "execute whatever this query is" is quite useful.

    Parameters
    ----------
    queryString : string
        The SPARQL query string to be executed.

    Returns
    -------
    results : dictionary
        A JSON representation of the results returned by the end-point.
    """
    self.sparql.setReturnFormat(JSON)

    try:
      self.sparql.setQuery(queryString)
      return self.sparql.query().convert()
    except Exception as e:
      return e

  def date_range(self, start, end):
    """
    Creates a filter for a given range of dates.

    SPARQL supports filtering, and this may be used to provide more specific results for a given date range.

    Parameters
    ----------
    start : string
        The start date.

    end : string
        The end date.

    Returns
    -------
    dateRange : string
        A structured string that is inserted into the query to provide date filtering.
    """
    # Normalize dates
    startDate = datetime.datetime.strptime(start, "%d-%m-%Y").date()
    endDate = datetime.datetime.strptime(end, "%d-%m-%Y").date()
    delta = endDate - startDate

    # If there are days to be filtered
    if (delta.days > 0 and delta.days < 10000):
      dateRange = 'FILTER ('

      # Calculate date difference between start + end
      delta = endDate - startDate

      # If there are days to be filtered
      if (delta.days > 0):
        # Generate filter string
        for i in range(delta.days + 1):
          dateRange = dateRange + """ str(?date) = '""" + str(
            startDate + datetime.timedelta(days=i)) + """' \n                ||"""

        # Add suffix
        dateRange = dateRange[:-2]
        dateRange = dateRange + ')'

        return dateRange
    else:
      return ''

  def perform_search(self, dateFrom, dateTo, artists, genres, locations, limit, trackName, countries, customSearchString, venue, orderBy, onlyCalma):
    """
    Executes a basic search on the SPARQL end-point.

    Parameters
    ----------
    dateFrom : string
        Start date for our date range filter.

    dateTo : string
        End date for our date range filter.

    artists : string
        A list of artists, comma seperated.

    genres : string
        A list of genres, comma seperated.

    locations : string
        A list of locations, comma seperated.

    lineage : string
        A list of lineage steps, comma seperated.

    limit : int
        Number of results to be returned.

    distinct : boolean
        Represents whether or not results should be distinct (i.e. no duplicates).

    fields : string
      A list of fields, comma seperated.

    Returns
    -------
    q : string
        A string which may be executed as a SPARQL query.

    """
    artists = artists.split(',')
    genres = genres.split(',')

    artists = [a.strip() for a in artists]
    genres = [g.strip() for g in genres]

    fields = " ?label ?performer ?description ?location ?place ?date ?genre"
    whereString = """
     ?art skos:prefLabel ?label.
     ?art mo:performer ?performer. 
     ?art etree:description ?description.
     ?performer foaf:name ?name.
     ?art event:place ?location.
     ?art etree:date ?date.
     ?location etree:location ?place.
     ?art event:hasSubEvent ?subEvent
     OPTIONAL {?performer etree:mbTag ?genre}.
     """

    if onlyCalma:
      whereString += "\n ?subEvent calma:data ?calma."
    else:
      whereString += "\n OPTIONAL {?subEvent calma:data ?calma}."

    # if customConditionType == 'AND':
    if isinstance(customSearchString, list):
      customSearchString = "\n".join(item for item in customSearchString)
    # elif customConditionType == 'OR':
    #   customSearchString = "\n ||".join(item for item in customSearchString)
    # else:
    #   customSearchString = ''
    # print(customSearchString)

    # Calculate date filters
    dateString = self.date_range(dateFrom, dateTo)

    # If limit is 0
    if (limit == 0):
      limit = ''
    # If custom limit entered
    else:
      limit = 'LIMIT ' + str(limit)

    # Generate filters for artists, genres, locations
    artistString = self.text_parse(artists, 1)
    genreString = self.text_parse(genres, 2)
    locationString = self.text_parse(locations, 3)
    trackString = self.text_parse(trackName, 4)
    venueString = self.text_parse(venue, 5)
    countriesString = self.text_parse(countries, 3)
    orderByString = self.parse_order_by(orderBy)

    # Add extra triples if required
    #if len(genreString) > 2:
      #fields += ' ?genre'
      #whereString += '?performer etree:mbTag ?genre.'
    if len(trackString) > 2:
      fields += ' ?trackname'
      whereString += '?track skos:prefLabel ?trackname.'
    if len(venueString) > 2:
      fields += ' ?venue'
      whereString += '?location etree:name ?venue.'

    q = """
        PREFIX etree:<http://etree.linkedmusic.org/vocab/>
        PREFIX mo:<http://purl.org/ontology/mo/>
        PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
        PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX calma: <http://calma.linkedmusic.org/vocab/>
        
        SELECT DISTINCT ?label ?name ?place ?location ?date (group_concat(distinct ?calma; separator = "\\n") AS ?calma) WHERE {{
          {0}
          {1}
          {2}
          {3}
          {4}
          {5}
          {6}
          {7}
          {8}
        }}
        {9}
        {10}
        """.format(whereString, artistString, genreString, locationString, venueString, dateString, trackString, customSearchString,
                   countriesString, orderByString, limit)
    print(q)
    return q

  def get_venue_information(self, label):
    """
    Retrieves venue information for a particular release.

    Parameters
    ----------
    label : string
        The release for which we want to retrieve the venue info of.

    Returns
    -------
    resultsDict : dict
        A dictionary of a mixture of the GeoNames and LastFM data
    """
    self.sparql.setQuery("""
        PREFIX etree:<http://etree.linkedmusic.org/vocab/>
        PREFIX mo:<http://purl.org/ontology/mo/>
        PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
        PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX sim: <http://purl.org/ontology/similarity/>

        SELECT DISTINCT ?place ?location ?obj WHERE {{
                ?art skos:prefLabel "{0}".
                ?art event:place ?location.
                ?location sim:subjectOf ?external.
                ?external sim:object ?obj.
                ?location etree:location ?place.
        }} GROUP BY ?place ?location ?obj
                          """.format(label))

    results = self.sparql.query().convert()
    resultsDict = {'geoname' : None,
                   'lastfm' : None}

    for result in results['results']['bindings']:
      if 'geoname' in result['obj']['value']:
        resultsDict['geoname'] = result['obj']['value']
      elif 'last.fm' in result['obj']['value']:
        resultsDict['lastfm'] = result['obj']['value']

    return resultsDict

  def parse_order_by(self, orderBy):
    """
    Generates a filter string for ordering by a give field.

    Parameters
    ----------
    orderBy : str
      The input field.

    Returns
    -------
    filterString : string
        An ORDER-BY string relative to the input field.

    """

    translate = {'Artist' : '?name',
                 'Label' : '?label',
                 'Date' : '?date',
                 'Genre' : '?genre',
                 'Location' : '?place'
                  }

    return "ORDER BY {0}".format(translate[orderBy])

  def text_parse(self, inputList, intType):
    """
    Generates filter string for a given list, and type.

    A complex query may have several seperate filters applied, in which case it makes sense to move this into
    it's own class. The type is used to identify the attribute being filtered.

    Parameters
    ----------
    inputList : string[]
      A list of filter conditions

    type : int
      The attribute to be filtered

    Returns
    -------
    filterString : string
        A appropriate filter string for the inputs

    """
    # If no data to process, return
    if inputList == None : return ''

    # Determine correct field
    if intType == 1:
      fieldType = """?name=\""""
    elif intType == 2:
      fieldType = """?genre=\""""
    elif intType == 3:
      fieldType = """?place=\""""
    elif intType == 4:
      fieldType = """?trackname=\""""
    elif intType == 5:
      fieldType = """?venue=\""""
    else:
      raise ('No matching field type')

    if isinstance(inputList, str):
      inputList = [inputList]

    # Join all possible filter clauses
    temp = " ".join(str(x) for x in inputList)
    if len(temp.rstrip()) < 3:
      return ''
    # If matches requirement for filter string
    else:
      # Create filter string
      filterString = 'FILTER('
      for entry in list(set(inputList)):
        filterString = """    {0}{1}{2}" ||\n""".format(filterString, fieldType, entry.replace('"', '').replace("'",'').rstrip())
      filterString = filterString[:-3].strip()
      filterString += ')\n'
    return filterString

  def get_artist_from_tracklist(self, tracklistURL):
    """
    Retrieves the artist from a particular track-list.

    Parameters
    ----------
    tracklistURL : string
        A URL in the tracklist, for which we want to find the performer.

    Returns
    -------
    artistName : str
        The name of the artist found.
    """
    name = self.execute_string("""
          PREFIX etree:<http://etree.linkedmusic.org/vocab/>
          PREFIX mo:<http://purl.org/ontology/mo/>
          PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
          PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
          PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

          SELECT DISTINCT ?name WHERE 
          {{   
               <{0}> mo:performer ?performer.
               ?performer foaf:name ?name.
          }} LIMIT 1
           """.format(tracklistURL))

    return name['results']['bindings'][0]['name']['value']

  def get_label_tracklist(self, eventurl):
    label = self.execute_string("""
                                PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
                                PREFIX etree:<http://etree.linkedmusic.org/vocab/>

                                SELECT DISTINCT ?label WHERE 
                                {{   
                                     <{0}> etree:isSubEventOf ?event.
                                     ?event skos:prefLabel ?label.

                                }} LIMIT 1
                                 """.format(eventurl))

    return label['results']['bindings'][0]['label']['value']

  def get_audio_track(self, trackURI):
    label = self.execute_string("""
                                PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
                                PREFIX etree:<http://etree.linkedmusic.org/vocab/>

                                SELECT DISTINCT ?url ?num ?label WHERE 
                                {{   
                                     <{0}> etree:audio ?url.
                                     <{0}> etree:number ?num.
                                     <{0}> skos:prefLabel ?label.
                                }}
                                 """.format(trackURI))

    return label['results']['bindings']