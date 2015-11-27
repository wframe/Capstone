#from __future__ import division
try:
   import cPickle as pickle
except:
   import pickle
import midi
import os.path
import os
from operator import itemgetter
from collections import OrderedDict, Counter
import numpy as  np
from SongData import SongData, FeatureVector, StartState
import routes 

#these values should match what is in SongData
#and are here just for reference
#REST = 128
#HOLD = 129
#NULL = 130
#END = 131
#BEATS_PER_BAR = 32

#extract features
datasetDir=os.path.join('scripts','scripts','melodies','noChords')
def Main():
    import os
    print('calculating features')
    absolute_pos = 0
    folder = os.path.join(routes.root, 'largeDataset')
    pitches = set()
    songs = []
    observedstates = dict()
    featurevectors = []	
    startstates = []
    uniquestartstates = set()
    finalstates = set()
    with open("valid_filenames.pkl","rb") as input:
        valid_filenames = pickle.load(input)
    for filename in valid_filenames:
        #try:  
            #folder = os.path.join('midi','midi','melodies','noChords')
        song_path = os.path.join(folder, filename)
        
        pattern = midi.read_midifile(song_path)
        song = SongData(pattern, filename)
        startstates.append(song.startstate)
        uniquestartstates.add((song.startstate.beat,song.startstate.pitch%12))
        for idx,feature in enumerate(song.featurevectors):
            if len(feature.vector) != 103:
                print(str(filename) + " had malformed vector")
                print("vector at index " + str(idx))
            if feature.vector not in observedstates:
                observedstates[feature.vector] = Counter()
            observedstates[feature.vector][feature.actiongenerated] += 1
            featurevectors.append(feature)
        if len(song.featurevectors) > 0:
            finalstates.add(song.featurevectors[len(song.featurevectors)-1])
        songs.append(song)

    #except Exception as e:
        #	import traceback, os.path
        #	top = traceback.extract_stack()[-1]
        #	print ', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])])

    print('unique start states: ' + str(len(uniquestartstates)))	
    print('unique states: ' + str(len(observedstates.keys())))
    print('total states observed: ' + str(len(featurevectors)))

    X = np.array([feature.vector for feature in featurevectors],dtype=bool)

    with open('songs.pkl', 'wb') as output:
    	pickle.dump(songs, output, -1)
    with open('featurevectors.pkl', 'wb') as output:
    	pickle.dump(featurevectors, output, -1)
    with open('observedstates.pkl', 'wb') as output:
    	pickle.dump(observedstates, output, -1)
    with open('startstates.pkl', 'wb') as output:
    	pickle.dump(startstates, output, -1)
    with open('finalstates.pkl', 'wb') as output:
    	pickle.dump(finalstates, output, -1)
    with open('X.pkl', 'wb') as output:
    	pickle.dump(X, output, -1)

if __name__ == "__main__":
    Main()