from __future__ import division
try:
   import cPickle as pickle
except:
   import pickle

import midi
import os.path
import os
from operator import itemgetter
#simple heuristic to predict most likely melody track:
##(total unique pitches)*(total notes)/(total chords+1)
def microseconds_per_beat(bpm):
	return 60000/bpm
def ticks_to_time(bpm, resolution):
	return microseconds_per_beat(bpm)/resolution
def write_track(pattern, melody_index, filename):
	melody_pattern = midi.Pattern()  
	melody_pattern.append(pattern[0])
	melody_pattern.append(pattern[melody_index])
	midi.write_midifile(str(filename),melody_pattern)
def get_chord_count_and_pitch_count(track):
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
				if chordOn and len(onPitches) == 0:
				#in this case we've terminated a chord	
					chordOn = False
					count += 1
			else:
				onPitches.add(pitch)
				if len(onPitches) > 1:
					chordOn = True
	return count, len(uniquePitches)
def predict_melody_index(pattern):
	index = 0
	max_score = 0
	index = 1
	for idx,track in enumerate(pattern):				
		if idx != 0 and len(track) > 1:
			counts = get_chord_count_and_pitch_count(track)
			curr_score = counts[1]/(counts[0]+1)
			if curr_score > max_score :
				max_score = curr_score
				index = idx 
	return index
def Main():
	folder = os.path.join('C:\\', 'Users', 'William','Documents','GitHub','Capstone','downloads','midiworld')
	songs = []	
	patterns = []
	for p_idx,filename in enumerate(os.listdir(folder)):
		try:   
			contains_note_off = False    
			song_path = os.path.join(folder, filename)
			pattern = midi.read_midifile(song_path)
			if len(pattern) > 1:
				new_pattern = midi.Pattern()
				list_of_coordinates = []
				song_track_notes = []
				patterns.append(pattern)
				for t_idx,track in enumerate(pattern):		
					note_ons = []		
					new_track = midi.Track()
					if t_idx == 0:
						for e_idx, event in enumerate(track):
							if event.name == 'End of Track':
								new_track.append(event)
							if event.name == 'Set Tempo':
								new_track.append(event)
								list_of_coordinates.append((event.name, event.tick, event.bpm, pattern.resolution))
						new_pattern.append(new_track)
					else:
						for event in track:
							if event.name == 'Note On':
								note_ons.append((event.tick, event.pitch))	
								new_track.append(event)					
							if event.name == 'End of Track':
								new_track.append(event)
							if event.name == 'Note Off':
								contains_note_off = True
								list_of_coordinates.append((event.name, event.tick, event.length, event.pitch))
						new_pattern.append(new_track)
					#song_track_notes.append(list_of_coordinates)
						#new_track += note_ons
				if not contains_note_off:
					track_index = predict_melody_index(new_pattern)
					write_track(new_pattern, track_index, filename)						
		except Exception as e:
			print(e)

	pdump(songs,'midi_list.pkl')
if __name__ == "__main__":
	Main()