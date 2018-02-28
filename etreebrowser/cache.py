import os
try:
   import cPickle as pickle
except:
   import pickle

def save(obj, name):
  """
  Saves an object in memory to disk.

  Parameters
  ----------
  obj : string
      Object to save.

  name : string
      Name of the file (in the cache folder) to save to.

  """
  dir = os.path.join(os.path.dirname(__file__) + "/cache", name + '.pkl')
  with open(dir, 'wb') as f:
    pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
  return

def load(name):
  """
  Loads an object from backing store (the /cache) folder, into memory.

  Parameters
  ----------
  name : string
      Name of the file (in the cache folder) to load.
  """

  dir = os.path.join(os.path.dirname(__file__) + "/cache", name + '.pkl')
  try:
    with open(dir, 'rb') as f:
      return pickle.load(f)
  except FileNotFoundError:
    return None