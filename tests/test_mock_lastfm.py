import requests_mock
import requests
import lastfm
import httpretty
import pytest
import re
lastfmHandler = lastfm.lastfmAPI('c957283a3dc3401e54b309ee2f18645b', 'f555ab4615197d1583eb2532b502c441')

@httpretty.activate
def test_request_auth_token():
  paras = [['api_key', 'c957283a3dc3401e54b309ee2f18645b'], ['format', 'json'], ['method', 'auth.getToken']]
  url = lastfmHandler.generate_api_request(paras, 'jadiajsio')
  httpretty.register_uri(httpretty.POST, url, status=504)

  with pytest.raises(ValueError):
    lastfmHandler.request_auth_token()

  httpretty.register_uri(httpretty.POST, url, status=404)

  with pytest.raises(ValueError):
    lastfmHandler.request_auth_token()

@httpretty.activate
def test_request_session_key():
  parameters = []
  parameters.append(['api_key', 'apikey'])
  parameters.append(['method', 'auth.getSession'])
  parameters.append(['token', 'token'])
  lastfmHandler.apiKey = 'apikey'
  lastfmHandler.token = 'token'

  url = lastfmHandler.generate_api_request(parameters, 'jadiajsio')

  contents = """<?xml version="1.0" encoding="utf-8"?>
  <lfm status="ok">
    <session>
      <name>CameronJAllan</name>
      <key>F1glGFdcZEZ5xTrkOJ6V1ESE0f1_91b9</key>
      <subscriber>0</subscriber>
    </session>
  </lfm>
  """

  httpretty.register_uri(httpretty.POST, url, status=200,
                         body=contents)

  lastfmHandler.request_session_key()
