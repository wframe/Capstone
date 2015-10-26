#from __future__ import division
try:
   import cPickle as pickle
except:
   import pickle
import midi
import os.path
import os
from operator import itemgetter
from collections import OrderedDict
import numpy as  np
from SongData import SongData
def Main():
	import os
	import csv	
	#these values should match what is in SongData
	#and are here just for reference
	#REST = 128
	#HOLD = 129
	#NULL = 130
	#END = 131
	#BEATS_PER_BAR = 32
	#extract features
	absolute_pos = 0
	#folder = os.path.join('scripts','scripts','melodies','noChords')
	folder = os.path.join('C:\\', 'Users', 'William','Documents','GitHub','Capstone', 'largeDataset')
	pitches = set()
	songs = []
	observedstates = set()
	featurevectors = []		
	with open('features.csv','wb') as out:
		try:
			print('finding valid songs')
			csv_out=csv.writer(out)
			valid_filenames = []		

			files = [filename for filename in os.listdir(folder)]
			for filename in os.listdir(folder):
				out_of_range = False
				song_path = os.path.join(folder, filename)
				pattern = midi.read_midifile(song_path)
				song = SongData(pattern, filename)
				print("examining " + str(len(song.actionset)) + " actions for: " + filename)

				for action in song.actionset:
					if (action > 84 and action < 128) or action < 48:
						out_of_range = True
					if song.startstate.pitch == 131:
						out_of_range = True
				if not out_of_range:
					valid_filenames.append(song.filename)
			print(len(valid_filenames))
			with open('valid_filenames.pkl', 'wb') as output:
				pickle.dump(valid_filenames, output, -1)
		except Exception as e:
			import traceback, os.path
			top = traceback.extract_stack()[-1]
			print ', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])])
if __name__ == "__main__":
	Main()