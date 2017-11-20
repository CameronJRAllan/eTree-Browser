import os, sys, pickle, editdistance

def load(name):
  dir = os.path.join(os.path.dirname(__file__) + "/cache", name + '.pkl')
  with open(dir, 'rb') as f:
    return pickle.load(f)

list = load('grouped_musicbrainz_no_threshold')
count = 0
totalcount = 0
for key in list.keys():
  if len(list[key]) > 1:
    count += 1

    print(list[key])
    print('Average edit distance between items in list: ' + str(editdistance.eval(list[key][0], list[key][1])))
    print('\n')
  else:
    totalcount += 1
print(count)
print(totalcount)