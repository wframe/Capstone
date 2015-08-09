from __future__ import division
try:
   import cPickle as pickle
except:
   import pickle
import src as midi
import os.path
import os
from operator import itemgetter
#simple heuristic to predict most likely melody track:
##(total unique pitches)*(total notes)/(average simultaneous notes)
def microseconds_per_beat(bpm):
	return 60000/bpm
def ticks_to_time(bpm, resolution):
	return microseconds_per_beat(bpm)
folder = os.path.join('C:\\', 'Users', 'William','Documents','GitHub','Capstone','downloads','midiworld')
songs = []
				
for p_idx,filename in enumerate(os.listdir(folder)):
	try:       
		song_path = os.path.join(folder, filename)
		pattern = midi.read_midifile(song_path)
		song_track_events = []
		new_pattern = midi.Pattern()
		list_of_coordinates = []
		song_track_notes = []
		for t_idx,track in enumerate(pattern):			
			new_track = midi.Track()
			if t_idx == 0:
				for e_idx, event in enumerate(track):
					if event.name == 'Set Tempo':
						if e_idx == 0:
							new_track.append(event)
						list_of_coordinates.append((event.name, event.tick, event.length, event.bpm, pattern.resolution))
			else:
				for event in track:
					if event.name == 'Note On':
						new_track.append(event)
						list_of_coordinates.append((event.name, event.tick, event.length, event.pitch))
				#list_of_coordinates.sort(key=itemgetter(1))
				song_track_notes.append(list_of_coordinates)
				new_track.append(midi.EndOfTrackEvent(tick = 1))
			if t_idx == 1:
				new_pattern.append(new_track)
				midi.write_midifile("track",new_pattern)
				print("new_pattern")
				print(new_pattern)
				print("pattern")
				print(pattern)
		songs.append(song_track_notes)								
	except Exception as e:
		print(e)
midi_pickle = open('midi_list.pkl', 'wb')
pickle.dump(songs, midi_pickle)