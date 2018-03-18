from geopy import geocoders
import cache
global queriesExecuted, geolocator, geoCache
class Maps():
  global queriesExecuted
  queriesExecuted = 0
  def __init__(self):
    self.cache = cache.Cache()
    self.keys = self.cache.load('preferences')
    self.geolocator = geocoders.GoogleV3(api_key=self.keys[2])
    self.geoCache = self.cache.load('geoCache')

  def homepage_add(self, results, **kwargs):
    kwargs['homepage_start'].emit()

    for result in results['results']['bindings']:
      if result['place']['value'] is not '':
        # Extract the venue name for geo-coding
        start = ' at '
        end = ' on '
        address = (str(result['label']['value']).split(start))[1].split(end)[0] + ', ' + str(result['place']['value'])
        # If already in the cache
        if address in self.geoCache:
          if len(self.geoCache[address].replace(' ','')) > 0:
            words = self.geoCache[address].split()
            latitude = words[0]
            longitude = words[1]
            kwargs['js_callback'].emit(str('%.3f' % (float(latitude))), str('%.3f' % (float(longitude))), str(result['label']['value']))
        # If not, get geo-code, and save into the cache
        else:
          try:
            location = self.geolocator.geocode(address, timeout=60)
            if location:
              latitude = location.latitude
              longitude = location.longitude
              self.geoCache[address] = str(location.latitude) + " " + str(location.longitude)
              kwargs['js_callback'].emit(str('%.3f' % (float(latitude))), str('%.3f' % (float(longitude))), str(result['label']['value']))
            else:
              self.geoCache[address] = ''
            self.cache.save(self.geoCache, 'geoCache')
            print("Saved cache for: {0}".format(address))
          except Exception as e:
            print("Geocoder Error: " + str(e))

    kwargs['homepage_end'].emit()


  