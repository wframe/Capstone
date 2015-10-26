try:
   import cPickle as pickle
except:
   import pickle
import midi
import os.path
import os
folder = os.path.join('C:\\', 'Users', 'William','Documents','GitHub','Capstone','downloads','midiworld')
songs = []
for idx,filename in enumerate(os.listdir(folder)):
    try:        
        song_path = os.path.join(folder, filename)
        pattern = midi.read_midifile(song_path)
        songs.append(pattern)        
    except:
        print('bad data: ' + filename)
midi_pickle = open('midi_list.pkl', 'wb')
pickle.dump(songs, midi_pickle)


