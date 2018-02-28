import requests
import hashlib
import xml.etree.ElementTree as ET
import json
import time
import cache

class lastfmAPI():
  def __init__(self, apiKey, sharedSecret):
    self.apiKey = apiKey
    self.sharedSecret = sharedSecret
    self.sessionKey = cache.load('last_fm_sessionkey')

    # apiKey = 'c957283a3dc3401e54b309ee2f18645b'
    # sharedSecret = 'f555ab4615197d1583eb2532b502c441'
    # sessionKey = '0KZYiiBtaC_JVVlqQ_wAqbFtbIacAJCC'

  def update_now_playing(self, artist, track):
    parameters = []
    parameters.append(['api_key', self.apiKey])
    parameters.append(['artist', artist])
    parameters.append(['method', 'track.updateNowPlaying'])
    parameters.append(['sk', self.sessionKey])
    parameters.append(['timestamp', str(time.time() - 30)])
    parameters.append(['track', track])
    url = self.generate_api_request(parameters, self.sharedSecret)
    r = requests.post(url, None)
    if r.status_code != 200:
      raise ValueError(str((r.status_code)))

  def hasSession(self):
    if self.sessionKey and type(self.sessionKey) is not None:
      return True
    else:
      return False

  def setSessionKey(self, key):
    self.sessionKey = key

  def getAPIKey(self):
    return self.apiKey

  def request_auth_token(self):
    parameters = []
    parameters.append(['api_key', self.apiKey])
    parameters.append(['format', 'json'])
    parameters.append(['method', 'auth.getToken'])

    url = self.generate_api_request(parameters, self.sharedSecret)
    r = requests.post(url, None)
    if r.status_code == 200:
      result = r.json()
      self.token = result['token']
      return self.token
    else:
      raise ValueError(str((r.status_code)))

  def get_venue_info(self, venue):
    return

  def request_session_key(self):
    parameters = []
    parameters.append(['api_key', self.apiKey])
    parameters.append(['method', 'auth.getSession'])
    parameters.append(['token', self.token])
    url = self.generate_api_request(parameters, self.sharedSecret)
    r = requests.post(url, None)

    if r.status_code == 200:
      root = ET.fromstring(str(r.text))
      for child in root:
        for sub in child:
          if len(str(sub.tag)) == 3:
            self.sessionKey = sub.text
            cache.save(self.sessionKey, 'last_fm_sessionkey')
    else:
      print('Error: ' + str(r.status_code) + '\n' + str(r.text))

  def get_similar_artists(self, artistName):
    url = """http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&autocorrect=1&artist= """ + artistName.strip().replace(' ', '%20') \
          + \
          '&api_key=' + self.apiKey + '&format=json'

    r = requests.post(url)

    if r.status_code == 200:
      r_json = json.loads(r.text)
      results = []
      try:
        for artist in r_json['similarartists']['artist']:
          results.append(artist['name'])
        return results
      except KeyError as k:
        return []
    else:
      raise ValueError('Error: ' + str(r.status_code) + '\n' + str(r.text))

  def get_tags_for_artist(self, artistName):
    url = """http://ws.audioscrobbler.com/2.0/?method=artist.getInfo&autocorrect=1&artist= """ + artistName.strip() \
          + \
          '&api_key=' + self.apiKey + '&format=json'
    print(url)
    r = requests.post(url)
    if r.status_code == 200:
      r_json = json.loads(r.text)
      return r_json
    else:
      raise ValueError('Error: ' + str(r.status_code) + '\n' + str(r.text))

  def set_session_key(self, newKey):
    self.sessionKey = newKey

  def generate_api_request(self, parameters, secret):
    key_value_string = ''
    for item in parameters:
      key_value_string = key_value_string + item[0] + item[1]
    url = 'http://ws.audioscrobbler.com/2.0/?'
    for item in parameters:
      url = url + item[0] + '=' + item[1] + '&'
    url = url + 'api_sig=' + hashlib.md5(str(key_value_string + secret).encode('utf-8')).hexdigest()
    return url

  def logout(self):
    self.sessionKey = None
    cache.save(self.sessionKey, 'last_fm_sessionkey')

