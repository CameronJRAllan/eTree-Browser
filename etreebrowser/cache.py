import pickle, os

def save(obj, name):
  dir = os.path.join(os.path.dirname(__file__) + "/cache", name + '.pkl')
  with open(dir, 'wb') as f:
    pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
  return

def load(name):
  dir = os.path.join(os.path.dirname(__file__) + "/cache", name + '.pkl')
  try:
    with open(dir, 'rb') as f:
      return pickle.load(f)
  except FileNotFoundError:
    return None