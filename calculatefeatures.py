from utilz import *
from SongData import SongData, FeatureVector, StartState
import routez 

def Main():
    import os
    print('calculating features')
    absolute_pos = 0
    folder = os.path.join(routez.root, 'largeDataset')
    pitches = set()
    songs = []
    observedstates = dict()
    featurevectors = []	
    startstates = []

    finalstates = set()
    valid_filenames = pload(valid_filename_pickle_string,noPrefix=True)
    for filename in valid_filenames:
        #try:  
            #folder = os.path.join('midi','midi','melodies','noChords')

        elistfile = open('excludelist.txt', 'r')
        excludelist = elistfile.read().splitlines()
        if filename not in excludelist:
            song_path = os.path.join(folder, filename)
        
            pattern = midi.read_midifile(song_path)
            song = SongData(pattern, filename)
            startstates.append(song.startstate)
            
            for idx,feature in enumerate(song.featurevectors):
                if len(feature.vector) != 104:
                    print(str(filename) + " had malformed vector")
                    print("vector at index " + str(idx))
                if feature.vector not in observedstates:
                    observedstates[feature.vector] = Counter()
                observedstates[feature.vector][feature.actiongenerated] += 1
                featurevectors.append(feature)
            if len(song.featurevectors) > 0:
                finalstates.add(song.featurevectors[len(song.featurevectors)-1])
            songs.append(song)



    print('total states observed: ' + str(len(featurevectors)))

    X = np.array([feature.vector for feature in featurevectors],dtype=bool)

    pdump(songs, songs_pickle_string)
    pdump(featurevectors, featurevector_pickle_string)
    pdump(observedstates, 'observedstates.pkl')
    pdump(startstates, 'startstates.pkl')
    pdump(finalstates, 'finalstates.pkl')
    pdump(X, 'X.pkl')

if __name__ == "__main__":
    Main()