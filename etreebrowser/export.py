import sys
import os
from PyQt5 import QtWidgets
import csv
import json

class Export():
  def __init__(self, app):
    self.app = app
    return

  def export_data(self, data, labels, dataFormat):
    # Present file dialog to user to save
    path = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File', '/home')

    if len(path[0]) < 1:
      return

    # Normalise the JSON
    dataParsed = self.normalize_json(data, labels)

    # Save file
    self.save_file(path, dataParsed, dataFormat)

  def normalize_json(self, data, labels):
    normalized = {}
    for property in data['results']['bindings']:
      if labels[property['p']['value']] not in normalized:
        normalized[labels[property['p']['value']]] = []
      normalized[labels[property['p']['value']]].append(property['o']['value'])

    return normalized

  def save_file(self, path, data, dataFormat):
    if dataFormat == 'CSV':
      self.to_csv(path, data)
    elif dataFormat == 'JSON':
      self.to_json(path, data)
    elif dataFormat == 'XML':
      self.to_xml(path, self.xml_recursive(data, ""))
    elif dataFormat == 'M3U':
      self.to_m3u(path, data)

  def to_m3u(self, path, data):
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
      outFile.close()

  def to_csv(self, path, data):
    #data = map(lambda x: self.flatten_for_csv(x, "__"), data)
    data = self.flatten_for_csv(data, "___")
    columns = [row for row in data]
    columns = list(set(columns))

    with open(path[0], 'w+') as outFile:
      csv_w = csv.writer(outFile)
      csv_w.writerow(columns)

      for i_r in data:
        csv_w.writerow(map(lambda x: data[i_r], columns))

  def flatten_for_csv(self, inputDict, delimiter):
    # Dict for storing our new, lat dictionary
    flatDict = {}

    # For each key in the dictionary
    for i in inputDict.keys():
      # If sub-dictionary found
      if isinstance(inputDict[i], dict):

        # Call recursively for level down
        levelDown = self.flatten_for_csv(inputDict[i], delimiter)

        # Seperate fields with delimiter
        for e in levelDown.keys():
          flatDict[i + delimiter + e] = levelDown[e]

      # If not a sub-dictionary
      else:
        flatDict[i] = inputDict[i]

    return flatDict

  def to_json(self, path, data):
    with open(path[0], 'w+') as outFile:
      json.dump(data, outFile, indent=2)

  def to_xml(self, path, data):
    with open(path[0], 'w+') as outFile:
      outFile.write("""<?xml version="1.0" encoding="UTF-8"?>\n""")
      outFile.write("""<performance>\n""")
      outFile.write(data)
      outFile.write("""</performance>\n""")

  def xml_recursive(self, data, padding):
    results = []

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

    return "%s%s" % (padding, data)


