import cache
import sys
from geopy import geocoders
import re

class GroupLocation():
  def __init__(self):
    self.geoCache = cache.load('geoCache')
    self.locations = cache.load('locationList')
    self.latlng = cache.load('locationLatLng')
    self.notGeolocated = cache.load('failedToGeolocate')
    self.geolocator = geocoders.GoogleV3(api_key="AIzaSyBnR6mRCbJ3yPsmhY-btGpfHpHJ_H6fZLI")
    #AIzaSyBnR6mRCbJ3yPsmhY-btGpfHpHJ_H6fZLI")
    # AIzaSyChlf0VSGWPD3tbp2fbCWOGoniICT_2owc")
    # AIzaSyDE3JOGCJJvG7OWo4BIfgW-6bmp5icH840

    # Get latitude and longitude for each place name
    self.get_lat_lng()

    # Group on these retrieved lat / lng values
    self.group_on_lat_lng()

    # Calculate the new default key
    self.add_default_keys()

    # Evaluate and provide statistics
    self.evaluate_processing()

  def get_locations_single_word(self):
    count = 0
    for location in self.locations:
      if len(re.findall(r'\w+', str(location))) == 1:
        count += 1
    return count

  def get_lat_lng(self):
    self.tooShort = 0
    for location in self.locations:
      if len(location) > 3:
        if location not in self.latlng and location not in self.notGeolocated:
          try:
            locLatLng = self.geolocator.geocode(location.encode('ascii', errors='ignore'), timeout=30)

            if locLatLng:
              latitude = locLatLng.latitude
              longitude = locLatLng.longitude
              self.latlng[location] = str(locLatLng.latitude) + " " + str(locLatLng.longitude)
              cache.save(self.latlng, 'locationLatLng')
            else:
              self.notGeolocated.append(location)

          except Exception:
            print('Error: ' + str(sys.exc_info()[0]) + '\n' + str(location) + '\n\n')
      else:
        self.tooShort += 1

    cache.save(self.notGeolocated, 'failedToGeolocate')

  def group_on_lat_lng(self):
    self.grouped = {}
    for value, key in sorted(self.latlng.items()):
      self.grouped.setdefault(key, []).append(value)

    list_count = []
    for key in self.grouped.keys():
      list_count.append(len(self.grouped[key]))
    # print('Average number of items: ')
    # print('important stuff below')
    # print(sum(list_count))
    # print(len(self.grouped.keys()))
    # print(sum(list_count)/len(self.grouped.keys()))

    return self.grouped

  def add_default_keys(self):
    # dict = {}
    dict = cache.load('newReversedGroupedLocations')

    self.prev_validated = [] # cache.load('previously_validated')

    for key in self.grouped.keys():
      newKey = self.generateKey(key)
      if newKey is not None:
        if newKey not in dict.keys():
          newKey = newKey.strip()
          dict[newKey] = {}
          dict[newKey]['latlng'] = key
          dict[newKey]['locations'] = self.grouped[key]
        else:
          # Append contents of conflicting key to existing key
          dict[newKey]['locations'] = dict[newKey]['locations'] + self.grouped[key]
        cache.save(dict, 'redo_dict_grouped_locations')
        cache.save(self.prev_validated, 'redo_previously_validated')

  def generateKey(self, key):
    if key not in self.prev_validated:
      self.prev_validated.append(key)

      # Get address from latitude and longitude
      address = self.geolocator.reverse(key, exactly_one=True, language='en', timeout=30)
      # If this request was successful
      if address is not None:
        addr = address.address

        # Remove any numbers
        addr_no_numbers = ''.join([letter for letter in addr if not letter.isdigit()])

        # Strip out the street which is always the behind the first comma
        addr_no_street = addr_no_numbers[addr_no_numbers.find(',') + 1:]

        # Format the address further to ensure it matches our consistent format
        index_for_formatting = addr_no_street.find(',', addr_no_street.find(',') + 1)
        addr_formatted = addr_no_street[1:index_for_formatting-1] + addr_no_street[index_for_formatting:]

        # Remove any spaces before commas (this happens regularly)
        addr_final = ', '.join(segment.strip() for segment in addr_formatted.split(','))

        # Check that we don't start with a comma
        if addr_final[0] == ',':
          addr_final = addr_final[1:].strip()

        # Return our formatted string
        print(addr_final)
        return (addr_final)
      else:
        return ''
    else:
      return None

  def evaluate_processing(self):
    print('Length location list: ' + str(len(self.locations)))
    print('Number of locations consisting of 1 word: ' + str(self.get_locations_single_word()))
    print('Length grouped list: ' + str(len(self.grouped.keys())))
    print('Number too short to geolocate: ' + str(self.tooShort))
    print('Number we failed to GeoLocate upon attempt: ' + str(len(self.notGeolocated)))

    failedGeoHasNum = 0
    for item in self.notGeolocated:
        if bool(re.search(r'\d', item)):
            failedGeoHasNum += 1
    print('Number of failed attempts which contained numbers: ' + str(failedGeoHasNum))

if __name__ == '__main__':
  instance = GroupLocation()
