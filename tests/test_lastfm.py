from unittest import TestCase
import pytest
import lastfm
import cache
import mock
import httpretty
import lastfm
import httpretty
import pytest
def return_now_playing_url(self, artist):
  return "http://ws.audioscrobbler.com/2.0/?api_key=c957283a3dc3401e54b309ee2f18645b&artist=3 Dimensional Figures&method=track.updateNowPlaying&sk=F1glGFdcZEZ5xTrkOJ6V1ESE0f1_91b9&timestamp=1517689174.0849104&track=atoyot&api_sig=ee68f6b8775e57d7642548b0ef766b33"

class TestLastFM(TestCase):
  @pytest.fixture(scope="function", autouse=True)
  def setup(self):
    self.lastfmHandler = lastfm.lastfmAPI('c957283a3dc3401e54b309ee2f18645b', 'f555ab4615197d1583eb2532b502c441')
    self.cache = cache.Cache()
    return

  def test_hasSession(self):
    assert(self.lastfmHandler.hasSession() == True)
    assert(self.lastfmHandler.sessionKey == self.cache.load('last_fm_sessionkey'))

  @mock.patch('cache.Cache.save')
  def test_has_no_session(self, arg):
    self.lastfmHandler.logout()
    assert(self.lastfmHandler.hasSession() == False)
    assert(self.lastfmHandler.sessionKey == None)

  def test_setSessionKey(self):
    oldKey = self.lastfmHandler.sessionKey
    self.lastfmHandler.setSessionKey('NewKey')
    assert (oldKey != 'NewKey')
    assert(self.lastfmHandler.hasSession() == True)
    assert (self.lastfmHandler.sessionKey == 'NewKey')

  def test_get_tags_for_artist(self):
    tags = self.lastfmHandler.get_tags_for_artist('Grateful Dead')
    assert(isinstance(tags, dict))

    for item in tags:
      assert(isinstance(tags[item], dict))
      assert(tags[item]['name'])
      assert('https://www.last.fm/music' in tags[item]['url'])

  @mock.patch('lastfm.lastfmAPI.generate_api_request', side_effect=return_now_playing_url)
  def test_update_now_playing(self, apiMock):
    self.lastfmHandler.update_now_playing('Artist', 'Track')
    assert(apiMock)
  # def test_get_similar_artists(self):
  #   similar = self.lastfmHandler.get_similar_artists('Grateful Dead')
  #   assert(isinstance(similar, list))

  def test_request_auth_token(self):
    try:
      self.lastfmHandler.request_auth_token()
    except Exception as e:
      print(e)
      self.fail()

  def test_generate_api_request(self):
    parameters = [['api_key', 'c957283a3dc3401e54b309ee2f18645b'], ['format', 'json'], ['method', 'auth.getToken']]
    url = self.lastfmHandler.generate_api_request(parameters, self.lastfmHandler.sharedSecret)

    assert(url.startswith('http://ws.audioscrobbler.com/2.0/'))

    for singleParameter in parameters:
      assert(singleParameter[0] in url)

  def test_getAPIKey(self):
    assert(self.lastfmHandler.apiKey == self.lastfmHandler.getAPIKey())

  def test_get_similar_artists(self):
    similar = self.lastfmHandler.get_similar_artists('Grateful Dead')
    assert(type(similar) == list)

  @httpretty.activate
  def test_request_auth_token(self):
    paras = [['api_key', 'c957283a3dc3401e54b309ee2f18645b'], ['format', 'json'], ['method', 'auth.getToken']]
    url = self.lastfmHandler.generate_api_request(paras, 'jadiajsio')
    httpretty.register_uri(httpretty.POST, url, status=504)

    with pytest.raises(ValueError):
      self.lastfmHandler.request_auth_token()

    httpretty.register_uri(httpretty.POST, url, status=404)

    with pytest.raises(ValueError):
      self.lastfmHandler.request_auth_token()

  @httpretty.activate
  def test_request_session_key(self):
    parameters = []
    parameters.append(['api_key', 'apikey'])
    parameters.append(['method', 'auth.getSession'])
    parameters.append(['token', 'token'])
    self.lastfmHandler.apiKey = 'apikey'
    self.lastfmHandler.token = 'token'

    url = self.lastfmHandler.generate_api_request(parameters, 'jadiajsio')

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

    self.lastfmHandler.request_session_key()
