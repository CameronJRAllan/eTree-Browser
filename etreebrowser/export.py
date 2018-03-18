import sys
import os
from PyQt5 import QtWidgets
import csv
import json

class Export():
  """
  Initializes an instance of the Export class.

  The export class provides functionality for exporting data from a view in the interface into a data format for use
  outside of the application..
  """
  def __init__(self, app):
    self.app = app
    return

  def export_data(self, data, labels, dataFormat):
    """
    Gets a save path from the user, before initialising write of the file in the desired format.

    Parameters
    ----------
    data : dict
        The data we wish to save to a file.
    labels : list
        A list of labels.
    dataFormat : string
        The desired format to save the data in.
    """

    # Present file dialog to user to save
    path = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File', '/home')

    if len(path[0]) < 1:
      return

    # Normalise the JSON
    dataParsed = self.normalize_json(data, labels)

    # Save file
    self.save_file(path, dataParsed, dataFormat)

  def normalize_json(self, data, labels):
    """
    Takes a dictionary of data from the SPARQL end-point and normalises it prior to conversion / saving.

    Parameters
    ----------
    data : dict
        The data we wish to save to a file.
    labels : list
        A list of labels.

    Returns
    ----------
    normalized : dict
        A normalised dictionary of data to be saved.
    """

    normalized = {}
    for property in data['results']['bindings']:
      if labels[property['p']['value']] not in normalized:
        normalized[labels[property['p']['value']]] = []
      normalized[labels[property['p']['value']]].append(property['o']['value'])

    return normalized

  def save_file(self, path, data, dataFormat):
    """
    Takes a dictionary of data from the SPARQL end-point and normalises it prior to conversion / saving.

    Parameters
    ----------
    path : tuple
        A tuple containing the save path.
    data : dict
        The data we wish to save to a file.
    dataFormat : string
        The desired format to save the data in.
    """

    if dataFormat == 'CSV':
      self.to_csv(path, data)
    elif dataFormat == 'JSON':
      self.to_json(path, data)
    elif dataFormat == 'XML':
      self.to_xml(path, self.xml_recursive(data, ""))
    elif dataFormat == 'M3U':
      self.to_m3u(path, data)

  def to_m3u(self, path, data):
    """
    Saves some normalised data to M3U format.

    Parameters
    ----------
    path : tuple
        A tuple containing the save path.
    data : dict
        The data we wish to save to a file.
    """

    # To store raw M3U data
    m3u = []

    artistName = data['Label'][0].split('Live at')[0]

    # For each item in the data
    for item in data['Has Sub Event']:
      trackData = self.app.sparql.get_audio_track(item)
      # Generate meta-data for M3U
      meta = {'filename' : trackData[0]['label']['value'],
              'url' : trackData[0]['url']['value']
              }

      m3u.append(meta)

    # If 1 or more URLs added
    if len(m3u) > 0:
      with open(path[0], 'w+') as outFile:
        # Write header
        outFile.write("#EXTM3U\n")

        # Write individual playlist items
        for item in m3u:
          outFile.write("#EXTINF:,{0} - {1} \n #EXTVLCOPT:network-caching=1000 \n".format(artistName,item['filename']))
          outFile.write(item['url'] + '\n')

      # Close file
      outFile.close()

  def to_csv(self, path, data):
    """
    Saves some normalised data to CSV format.

    Parameters
    ----------
    path : tuple
        A tuple containing the save path.
    data : dict
        The data we wish to save to a file.
    """

    # Create a flattened data structure from the JSON
    data = self.flatten_for_csv(data, "___")

    # Remove duplicates from the columns
    columns = [row for row in data]
    columns = list(set(columns))

    with open(path[0], 'w+') as outFile:
      # Write CSV to file
      csvWriter = csv.writer(outFile)
      csvWriter.writerow(columns)

      for indexRow in data:
        csvWriter.writerow(map(lambda x: data[indexRow], columns))

  def flatten_for_csv(self, inputDict, delimiter):
    """
    Saves some normalised data to CSV format.

    Parameters
    ----------
    inputDict : dict
        The data we wish to save to a file.
    delimiter : string
        Value which acts as a delimiter between items.

    Returns
    ----------
    flatDict : dict
        A flattened representation of our input dictionary.
    """

    # Dict for storing our new, lat dictionary
    flatDict = {}

    # For each key in the dictionary
    for singleKey in inputDict.keys():
      # If sub-dictionary found
      if isinstance(inputDict[singleKey], dict):

        # Call recursively for level down
        levelDown = self.flatten_for_csv(inputDict[singleKey], delimiter)

        # Seperate fields with delimiter
        for levelDownKey in levelDown.keys():
          flatDict[singleKey + delimiter + levelDownKey] = levelDown[levelDownKey]

      # If not a sub-dictionary
      else:
        flatDict[singleKey] = inputDict[singleKey]

    # Return our flat dictionary
    return flatDict

  def to_json(self, path, data):
    """
    Saves some normalised data to JSON format.

    Parameters
    ----------
    data : dict
        The data we wish to save to a file.
    path : tuple
        A tuple containing the save path.
    """

    with open(path[0], 'w+') as outFile:
      json.dump(data, outFile, indent=2)

  def to_xml(self, path, data):
    """
    Saves some normalised data to XML format.

    Parameters
    ----------
    data : dict
        The data we wish to save to a file.
    path : tuple
        A tuple containing the save path.
    """

    with open(path[0], 'w+') as outFile:
      # Write header to file
      outFile.write("""<?xml version="1.0" encoding="UTF-8"?>\n""")

      # Performance tag opening
      outFile.write("""<performance>\n""")

      # Write flat XML data (from recursive function)
      outFile.write(data)

      # Performance tag closing
      outFile.write("""</performance>\n""")

  def xml_recursive(self, data, padding):
    """
    Saves some normalised data to XML format. To achieve this we build a translation
    table using the str.maketrans function.

    Parameters
    ----------
    data : dict
        The data we wish to save to a file.
    padding : string
        Current padding value (indentation in the file).
    """

    # Empty results file
    results = []

    # If need to call recursive function (step case)
    if type(data) is dict:
      # For each 'tag' to be created
      for nameOfTag in data:
        # Get data for this tag
        subObject = data[nameOfTag]

        # Append opening tag
        results.append("%s<%s>" % (padding, nameOfTag.translate(str.maketrans({'(': '', ')': '', ' ': '_'}))))

        # Append sub-object if applicable
        results.append(self.xml_recursive(subObject, "\t" + padding))

        # Append closing tag
        results.append("%s</%s>" % (padding, nameOfTag.translate(str.maketrans({'(': '', ')': '', ' ': '_'}))))

      # Append into single string, newline seperated
      return "\n".join(results)

    # Base case
    return "%s%s" % (padding, data)


