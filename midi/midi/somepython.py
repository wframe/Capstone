from __future__ import division
try:
   import cPickle as pickle
except:
   import pickle

import src as midi
import os.path
import os
from operator import itemgetter

def hasChords(track):
	chordOn = False
	onPitches = set()
	uniquePitches = set()
	total_notes = 0
	count = 0
	for event in track:
		if event.name == "Note On":
			pitch = event.pitch
			uniquePitches.add(pitch)
			if pitch in onPitches: 
				onPitches.remove(pitch)			
			else:
				onPitches.add(pitch)
				if len(onPitches) > 1:
					return True
	return False
absolute_pos = 0
folder = os.path.join('melodies','noChords')
pitches = set()
for p_idx,filename in enumerate(os.listdir(folder)):
	try:  
		song_path = os.path.join(folder, filename)
		pattern = midi.read_midifile(song_path)
		for event in pattern[1]:
			if event.name == 'poop':
				poop = 'poop'
		#if not hasChords(pattern)
	except Exception as e:
		print(e)


