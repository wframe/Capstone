try:
	import cPickle as pickle
except:
	import pickle
from ExtractMidiData import write_track
import os
import src as midi
def Main():
	print('hello hugh mon')
	folder = os.path.join('C:\\', 'Users', 'William','Documents','GitHub','Capstone','downloads','midiworld')
	datasetdir =  os.path.join('C:\\', 'Users', 'William','Documents','GitHub','Capstone', 'largeDataset')
	songs = []	
	patterns = []
	MINPITCHES = 12
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
					print("track " + str(t_idx) + " in " + filename)
					noteevents = [evt for evt in track if evt.name == 'Note On' or evt.name == 'Note Off']	
					if len(noteevents) != 0:
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
						if contains_note_off:
							def hasChords():
								return len([idx for idx,evt in enumerate(track) if 
																				idx > 0 and 
																				track[idx].name == 'Note On' and 
																				track[idx-1].name == 'Note On']
																				) > 0   	
							newfile = str(filename)			 
							if not hasChords():
								from SongData import SongData
								song = SongData(pattern, newfile, t_idx)
								uniquepitches = len(song.uniquepitches)
								print("had " + str(uniquepitches) + " unique pitches")		 
								if uniquepitches > MINPITCHES:
									write_track(pattern, t_idx, os.path.join(datasetdir,str(t_idx)+'_'+newfile))		
						elif "Note On" in set(evt.name for evt in track):
							def hasChords():
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
							newfile = str(filename)			 
							if not hasChords():
								from SongData import SongData
								song = SongData(pattern, newfile, t_idx)	
								uniquepitches = len(song.uniquepitches) 
								print("had " + str(uniquepitches) + " unique pitches")
								if uniquepitches > MINPITCHES:
									write_track(pattern, t_idx, os.path.join(datasetdir,str(t_idx)+'_'+newfile))			
		except Exception as e:
			print("exception in: " + filename)
	midi_pickle = open('midi_list.pkl', 'wb')
	pickle.dump(songs, midi_pickle)
if __name__ == "__main__":
	Main()