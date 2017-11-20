import cache
import sys
from geopy import geocoders
import re

class TidyFurtherGroupedLocations():
  def __init__(self):
    self.locations = cache.load('newReversedGroupedLocations')

    countries = []
    for key in self.locations.keys():
      countries.append(key.split(',')[-1].rstrip())
    countries = list(set(countries))

    translation = {'Slovaka' : 'Slovakia',
                   'Trinidad and Tobao' : 'Trinidad and Tobago',
                   'Luxemboug' : 'Luxembourg',
                   'Icelad' : 'Iceland',
                   'Cua' : 'Cuba',
                   'Brazl' : 'Brazil',
                   'Belgim' : 'Belgium',
                   'Portugl' : 'Portugal',
                   'Pakistn' : 'Pakistan',
                   'Moroco' : 'Morroco',
                   'Swedn' : 'Sweden',
                   'Costa Ria' : 'Costa Rica',
                   'Ecuadr' : 'Eduador',
                   'Canaa' : 'Canada',
                   'Greee' : 'Greece',
                   #' K' : 'UK',
                   'Austra' : 'Austria',
                   'Australa' : 'Australia',
                   'Czechna' : 'Czechnia',
                   'Iceld' : 'Iceland',
                   'Peu' : 'Peru',
                   'Itay' : 'Italy',
                   'The Bahams' : 'The Bahamas',
                   'Netherlans' : 'Netherlands',
                   'Span' : 'Spain',
                   'Denmak' : 'Denmark',
                   'Hong Kog' : 'Hong Kong',
                   'Isral' : 'Israel',
                   'Lithuana' : 'Lithuania',
                   'Germay' : 'Germany',
                   'Norwy' : 'Norway',
                   'Jamaia' : 'Jamaica',
                   'Polad' : 'Poland',
                   'Nicaraga' : 'Nicaragra',
                   'Frane' : 'France',
                   'Serba' : 'Serbia',
                   'UA' : 'USA',
                   'Hungay' : 'Hungry',
                   'Switzerlad' : 'Switzerland',
                   'Austriala' : 'Australia',
                   'SSolomon Islans' : 'Solomon Islands',
                   'Boliva' : 'Bolivia'
                   }

    new_dict = {}
    for key in self.locations.keys():
      oldCountry = key[key.rfind(',') + 2:]
      newCountry = oldCountry
      if newCountry == 'K':
        newCountry = 'UK'
      for country_key in translation.keys():
        newCountry = newCountry.replace(country_key, translation[country_key]).rstrip()

      newKey = key[:key.rfind(',') + 2] + newCountry
      new_dict[newKey] = self.locations[key]

    cache.save(new_dict, 'newReversedGroupedLocations')

if __name__ == '__main__':
  tidy = TidyFurtherGroupedLocations()
