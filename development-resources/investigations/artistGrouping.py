import editdistance
import sys
import cache

# Load list of artists
artistList = cache.load('artistList')

possibleDuplicates = []

# For each artist
for artist in artistList:
  # Compare against each other artist
  for otherArtist in artistList:
    # If we can reach otherArtist from artist in 1-2 letter changes
    if 0 < editdistance.eval(artist, otherArtist) < 2:
      # Add to possible duplicates
      possibleDuplicates.append([artist, otherArtist])

correct = 0
incorrect = 0

processed = []
for artist, otherArtist in possibleDuplicates:
  # If artist, otherArtist have not been compared against each-other yet
  if [artist, otherArtist] not in processed and [otherArtist, artist] not in processed:
    isCorrect = input(str(artist) + ',  ' + str(otherArtist) + '\n')
    # If user says this is a correct assumption
    if isCorrect == '1':
      correct += 1
    # If user says this is a false positive
    else:
      incorrect += 1
    processed.append([artist, otherArtist])

print('Percentage correct: ' + str(correct / (correct + incorrect)))
print('Number correct: ' + str(correct))
print('Number incorrect: ' + str(incorrect))
print('Fin')