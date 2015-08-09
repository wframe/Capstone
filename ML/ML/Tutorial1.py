import src as midi
pattern = midi.Pattern()
track = midi.Track()
pattern.append(track)
on = midi.NoteOnEvent(tick = 0, velocity = 20, pitch = midi.G_3)
track.append(on)
off = midi.NoteOffEvent(tick = 200, pitch = midi.G_3)
track.append(off)
eot = midi.EndOfTrackEvent(tick = 1)
track.append(eot)
print(pattern)
midi.write_midifile("tutorial1.mid", pattern)

