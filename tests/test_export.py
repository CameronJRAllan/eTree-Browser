import sys
sys.path.append("..")
from unittest import TestCase
import export
import sparql
import application
import pytest
from PyQt5 import QtWidgets, QtCore
import os

class TestExport():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()
    qtbot.add_widget(self.dialog)

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

    # self.prog.exporter

    self.file = open('saveFileTest', 'w')
    self.stubInstance = stubExport()
  # def test_export_data(self):
  #   self.fail()

  def test_normalize_json(self):
    normalized = self.prog.exporter.normalize_json(self.stubInstance.data, self.stubInstance.get_labels())

    assert(len(normalized) == 15)

    for x in normalized:
      assert(isinstance(normalized[x], list))

  def test_to_csv(self):

    data = self.prog.exporter.normalize_json(self.stubInstance.data, self.stubInstance.get_labels())
    try:
      self.prog.exporter.to_csv(('/home/cameron/test.t', None), data)
    except Exception as e:
      pytest.fail()


  # def test_to_json(self):
  #   self.fail()
  #
  # def test_to_xml(self):
  #   self.fail()

  def test_xml_recursive(self):
    xml = self.prog.exporter.xml_recursive(self.stubInstance.data, "")

    # Check head in XML
    assert("<head>" in xml and "</head>" in xml)

    # Check distinct is false
    assert("<distinct>" in xml and "</distinct>" in xml)

    # Check bindings
    assert("<bindings>" in xml and "</bindings>" in xml)

    # Check results
    assert("<results>" in xml and "</results>" in xml)

  def test_flatten_for_csv(self):
    inputDict = {'data item 1' : {'subitem' : 'data_1',
                                  'subitem2': 'data_2',
                                  'subitem3': 'data_3'
                                },
                 'data item 2': {'subitem': 'data_1',
                                 'subitem2': 'data_2',
                                 'subitem3': 'data_3'
                                 },
                 'data item 3': 'data_4'
                }

    flattened = self.prog.exporter.flatten_for_csv(inputDict, "__")

    assert(isinstance(flattened, dict))

  def test_to_m3u(self):
    try:
      data = self.prog.exporter.normalize_json(self.stubInstance.data, self.stubInstance.get_labels())
      self.prog.exporter.to_m3u(('/home/cameron/test.t', None), data)
    except Exception as e:
      print(e)
      pytest.fail()

class stubExport():
  def __init__(self):
    self.file = open('saveFileTest', 'w')
    self.data = sparql.SPARQL().get_release_properties('3 Dimensional Figures Live at The Red Square on 2008-01-10')

  def get_labels(self):
    labels = {'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 'Type',
              'http://www.w3.org/2000/01/rdf-schema#seeAlso': 'See Also',
              'http://purl.org/ontology/mo/performer': 'Performer',
              'http://etree.linkedmusic.org/vocab/date': 'Date',
              'http://etree.linkedmusic.org/vocab/description': 'Description',
              'http://etree.linkedmusic.org/vocab/id': 'ID',
              'http://etree.linkedmusic.org/vocab/keyword': 'Keyword(s)',
              'http://etree.linkedmusic.org/vocab/lineage': 'Lineage',
              'http://etree.linkedmusic.org/vocab/notes': 'Notes',
              'http://etree.linkedmusic.org/vocab/source': 'Source',
              'http://etree.linkedmusic.org/vocab/uploader': 'Uploader',
              'http://purl.org/NET/c4dm/event.owl#place': 'Place',
              'http://www.w3.org/2004/02/skos/core#prefLabel': 'Label',
              'http://purl.org/NET/c4dm/event.owl#hasSubEvent': 'Has Sub Event',
              'http://purl.org/NET/c4dm/event.owl#time': 'Time',
              'http://etree.linkedmusic.org/vocab/audio': 'Audio URL',
              'http://etree.linkedmusic.org/vocab/isSubEventOf': 'Sub Events',
              'http://etree.linkedmusic.org/vocab/number': 'Track Number',
              'http://purl.org/ontology/mo/performed': 'Performances',
              'http://xmlns.com/foaf/0.1/name': 'Name'
              }
    return labels