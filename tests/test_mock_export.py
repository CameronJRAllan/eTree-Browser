import export
import sparql
def test_save_file(mocker):
  exportInstance = export.Export()
  exportStub = stubExport()
  path = ('/home/cameron/test.csv', 'null')

  # mocker.spy(exportInstance, 'to_csv')
  mocker.spy(exportInstance, 'to_json')
  mocker.spy(exportInstance, 'to_xml')
  mocker.spy(exportInstance, 'to_m3u')

  # exportInstance.save_file(path, exportStub.data, 'CSV')
  exportInstance.save_file(path, exportStub.data, 'JSON')
  exportInstance.save_file(path, exportStub.data, 'XML')
  # exportInstance.save_file(None, None, 'M3U')

  # assert (exportInstance.to_csv.call_count == 1)
  assert (exportInstance.to_json.call_count == 1)
  assert (exportInstance.to_xml.call_count == 1)
  # assert (exportInstance.to_m3u.call_count == 1)

class stubExport():
  def __init__(self):
    self.file = open('saveFileTest', 'w')
    self.data = sparql.SPARQL().get_tracklist('Mogwai Live at the Forum on 16-10-1999')
