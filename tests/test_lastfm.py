from unittest import TestCase
import pytest
import lastfm
import cache
import mock

class TestLastFM(TestCase):
  @pytest.fixture(scope="function", autouse=True)
  def setup(self):
    self.lastfmHandler = lastfm.lastfmAPI('c957283a3dc3401e54b309ee2f18645b', 'f555ab4615197d1583eb2532b502c441')
    return

  def test_hasSession(self):
    assert(self.lastfmHandler.hasSession() == True)
    assert(self.lastfmHandler.sessionKey == cache.load('last_fm_sessionkey'))

  @mock.patch('cache.save')
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

    assert(isinstance(tags, list))

    for item in tags:
      assert(isinstance(item, dict))
      assert(item['name'])
      assert(item['url'])

  def test_get_similar_artists(self):
    similar = self.lastfmHandler.get_similar_artists('Grateful Dead')
    assert(isinstance(similar, list))

  def test_request_auth_token(self):
    try:
      self.lastfmHandler.request_auth_token()
    except Exception as e:
      self.fail()

  def test_generate_api_request(self):
    parameters = [['api_key', 'c957283a3dc3401e54b309ee2f18645b'], ['format', 'json'], ['method', 'auth.getToken']]
    url = self.lastfmHandler.generate_api_request(parameters, self.lastfmHandler.sharedSecret)

    assert(url.startswith('http://ws.audioscrobbler.com/2.0/'))

    for singleParameter in parameters:
      assert(singleParameter[0] in url)

  def test_getAPIKey(self):
    assert(self.lastfmHandler.apiKey == self.lastfmHandler.getAPIKey())

# lastfm_handler = lastfm.lastfm('Key', 'secretSecret')
# def testhasSession():
#   lastfm_handler.setSessionKey(None)
#   assert False == lastfm_handler.hasSession()
#
#   lastfm_handler.setSessionKey('Test')
#   assert True == lastfm_handler.hasSession()
#
# def testgetAPIKey():
#   assert 'Key' == lastfm_handler.getAPIKey()
#
# def test_get_tags_for_artist():
#   results = lastfm_handler.get_tags_for_artist("Grateful Dead")
