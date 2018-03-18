import os
try:
   import cPickle as pickle
except:
   import pickle
import threading

class Cache():
  def __init__(self):
    self.lock = threading.Lock()

  def save(self, obj, name):
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
    self.lock.acquire()
    print('Lock acquired')
    try:
      with open(dir, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    finally:
      self.lock.release()
      print('Lock released')
    return

  def load(self, name):
    """
    Loads an object from backing store (the /cache) folder, into memory.

    Parameters
    ----------
    name : string
        Name of the file (in the cache folder) to load.
    """
    dir = os.path.join(os.path.dirname(__file__) + "/cache", name + '.pkl')
    self.lock.acquire()

    try:
      with open(dir, 'rb') as f:
        f = pickle.load(f)
    finally:
      self.lock.release()

    return f

    # try:
    #   with open(dir, 'rb') as f:
    #     return pickle.load(f)
    # except FileNotFoundError:
    #   return None