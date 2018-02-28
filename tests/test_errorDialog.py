import application
from PyQt5 import QtWidgets, QtCore, QtGui
import pytest
import urllib3

def test_error_dialog_attribute_error():
  try:
    exception = AttributeError('General Error')
    errorDialog = application.ErrorDialog(exception)
    errorDialog.close()

  except Exception as e:
    pytest.fail()

def test_error_dialog_value_error():
  try:
    exception = ValueError('General Error')
    errorDialog = application.ErrorDialog(exception)

    errorDialog.close()
    errorDialog = None
  except Exception as e:
    pytest.fail()

def test_error_dialog_http_error():
  exception = urllib3.exceptions.HTTPError()
  errorDialog = application.ErrorDialog(exception)
  assert(errorDialog.message == 'A HTTP error occurred, this could be due to the SPARQL end-point being unavailable')
  errorDialog.close()

def test_error_dialog_general_error():
  try:
    exception = Exception('General Error')
    errorDialog = application.ErrorDialog(exception)
    errorDialog.close()

  except Exception as e:
    pytest.fail()
