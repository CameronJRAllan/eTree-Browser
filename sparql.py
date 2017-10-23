from SPARQLWrapper import SPARQLWrapper, JSON, POSTDIRECTLY
import datetime

class SPARQL():
  def __init__(self):
    """
    Initializes an instance of the SPARQL class.

    The SPARQL class is used for all interfacing with the SPARQL end-point provided by Sean Bechhofer's research and work.

    """
    self.sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")
    self.sparql.setReturnFormat(JSON)
    self.sparql.setMethod("POST")

  def get_release_properties(self, releaseName):
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

  def get_release_subproperties(self, subject):
    queryGetProperties = """
                            SELECT * {{
                              <{0}> ?p ?o.
                            }}
                         """.format(str(subject))
    self.sparql.setQuery(queryGetProperties)
    return self.sparql.query().convert()

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

              SELECT DISTINCT ?audio ?label ?num {{
                ?perf event:hasSubEvent ?tracklist.
                ?tracklist skos:prefLabel ?label.
                ?tracklist etree:number ?num.
                ?tracklist etree:audio ?audio.
                ?perf rdf:type mo:Performance.
                ?perf skos:prefLabel "{0}".
            }} GROUP BY ?label ?audio ?num ORDER BY ?num 
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
    print('\n\n')
    print(queryString)
    print('\n\n')
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
    print(queryString)
    self.sparql.setReturnFormat(JSON)

    try:
      self.sparql.setQuery(queryString)
      return self.sparql.query().convert()
    except Exception:
      raise ('Error occured')

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
    startDate = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    endDate = datetime.datetime.strptime(end, "%Y-%m-%d").date()
    delta = endDate - startDate

    # If there are days to be filtered
    if (delta.days > 0):
    #   return """FILTER (?date > "{0}"^^xsd:dateTime)
    #             FILTER (?date < "{1}"^^xsd:dateTime)""".format(startDate, endDate)
    # else:
    #   return ''

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

  def perform_search(self, dateFrom, dateTo, artists, genres, locations, limit):
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

    fields = " ?label ?performer ?description ?location ?place ?date"
    whereString = """
     ?art skos:prefLabel ?label.
     ?art mo:performer ?performer. 
     ?art etree:description ?description.
     ?performer foaf:name ?name.
     ?art event:place ?location.
     ?art etree:date ?date.
     ?location etree:location ?place.
     """

    # If custom date range entered (assuming default is 1950-01-01?)
    if dateFrom != '1950-01-01' or dateTo != '2000-01-01':
      # Calculate a filter string for this
      dateString = self.date_range(dateFrom, dateTo)
    else:
      dateString = ''

    # If limit is 0
    if (limit == 0):
      limit = ''
    # If custom limit entered
    else:
      limit = 'LIMIT ' + str(limit)

    # Generate filter
    artistString = self.text_parse(artists, 1)
    genreString = self.text_parse(genres, 2)
    if len(genreString) > 2:
      fields = fields + ' ?genre'
      whereString = whereString + '?performer etree:mbTag ?genre.'
    locationString = self.text_parse(locations, 3)
    # lineageString = text_parse(lineage, 4)

    q = """PREFIX etree:<http://etree.linkedmusic.org/vocab/>
          PREFIX mo:<http://purl.org/ontology/mo/>
          PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
          PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
          PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
          SELECT DISTINCT """ + "?label ?name ?place ?location ?date" \
          + """  WHERE {    """ \
          + str(whereString) \
          + str(artistString) \
          + str(genreString)   \
          + str(locationString) \
          + str(dateString) + """      } """ \
          + str('GROUP BY ?label') + ' ' \
          + str(limit)
    print(q)
    return q

  def text_parse(self, inputList, type):
    """
    Generates filter string for a given list, and type.

    A complex query may have several seperate filters applied, in which case it makes sense to move this into
    it's own class. The type is used to identify the attribute being filtered.

    Parameters
    ----------
    inputList : string[]
      A list of filter conditions

    type : str
      The attribute to be filtered

    Returns
    -------
    filterString : string
        A appropriate filter string for the inputs

    """

    # Determine correct field
    if type == 1:
      fieldType = "?name='"
    elif type == 2:
      fieldType = "?genre='"
    elif type == 3:
      fieldType = "?place='"
    elif type == 4:
      fieldType = "?lineage'="
    else:
      raise ('No matching field type')

    # Join all possible filter clauses
    temp = " ".join(str(x) for x in inputList)
    if len(temp) < 3:
      filterString = ''
    # If matches requirement for filter string
    else:
      filterString = 'FILTER('
      for entry in inputList:
        filterString = "    {0}{1}{2} ||\n".format(filterString, fieldType, entry)
      filterString = filterString[:-3].strip()
      filterString += "')\n"

    print(filterString)
    return filterString
