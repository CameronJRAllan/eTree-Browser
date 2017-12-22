import export
import sparql
import application
import pytest
from PyQt5 import QtWidgets

class TestExportQt():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self, qtbot):
    # Create dialog to show this instance
    self.dialog = QtWidgets.QMainWindow()

    # Start main event loop
    self.prog = application.mainWindow(self.dialog)

  def test_save_file(self, mocker):
    exportInstance = export.Export(self.prog)
    exportStub = stubExport()
    path = ('/home/cameron/test.csv', 'null')

    # mocker.spy(exportInstance, 'to_csv')
    mocker.spy(exportInstance, 'to_json')
    mocker.spy(exportInstance, 'to_xml')
    mocker.spy(exportInstance, 'to_csv')

    exportInstance.save_file(path, exportStub.data, 'CSV')
    exportInstance.save_file(path, exportStub.data, 'JSON')
    exportInstance.save_file(path, exportStub.data, 'XML')

    assert (exportInstance.to_csv.call_count == 1)
    assert (exportInstance.to_json.call_count == 1)
    assert (exportInstance.to_xml.call_count == 1)

class stubExport():
  def __init__(self):
    self.file = open('saveFileTest', 'w')
    self.data = sparql.SPARQL().get_tracklist('Mogwai Live at the Forum on 16-10-1999')
