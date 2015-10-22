#from __future__ import division
try:
   import cPickle as pickle
except:
   import pickle
import src as midi
import os.path
import os
from operator import itemgetter
from collections import OrderedDict
import numpy as  np
from SongData import SongData
def Main():
	#these values should match what is in SongData
	#and are here just for reference
	#REST = 128
	#HOLD = 129
	#NULL = 130
	#END = 131
	#BEATS_PER_BAR = 32
	#extract features
	absolute_pos = 0
	folder = os.path.join('downloads','midiworld')
	pitches = set()
	songs = []
	observedstates = set()
	featurevectors = []	
	import csv	
	with open('features.csv','wb') as out:
		try:
			print('finding valid songs')
			csv_out=csv.writer(out)
			valid_filenames = []		
			for filename in os.listdir(folder):
				out_of_range = False
				song_path = os.path.join(folder, filename)
				pattern = midi.read_midifile(song_path)
				song = SongData(pattern, filename)
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
if __name__ == "__main__":
	Main()