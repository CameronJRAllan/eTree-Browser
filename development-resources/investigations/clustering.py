from SPARQLWrapper import SPARQLWrapper, JSON
import collections, re
from fuzzywuzzy import fuzz
finalFrequency = {}
import string
import numpy as np
import sklearn.cluster
from nltk.corpus import stopwords
import distance
import enchant
global groups
s=set(stopwords.words('english'))
from rdflib.namespace import SKOS
import cache

artistList = sorted(cache.load('artistList'))
genreList = sorted(cache.load('genreList'))
locationList = sorted(cache.load('locationList'))

words = np.asarray(list(genreList))  # So that indexing with a list will work

print(str('Calculating levenstein similarity'))
lev_similarity = -1 * np.array([[distance.levenshtein(w1, w2) for w1 in words] for w2 in words])
print(str('Clustering begin'))
affprop = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=0.5)
affprop.fit(lev_similarity)
groups = {}
for cluster_id in np.unique(affprop.labels_):
  print(str(cluster_id))
  exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
  cluster = np.unique(words[np.nonzero(affprop.labels_ == cluster_id)])
  # cluster_str = ", ".join(cluster)
  temp = []
  if len(exemplar) > 1:
    for i in cluster:
      temp.append(i)

    if len(temp) > 1:
      cluster_str = ", ".join(temp)
      print("ADDED - *%s:* %s" % (exemplar, cluster_str))
      groups[exemplar] = temp
      print('\n \n')

for item in groups.keys():
  print(str(item))
