try:
   import cPickle as pickle
except:
	import pickle 
from SongData import *
from SongData import SongData
import random 
import copy
from collections import Counter
import midi
import uuid
import heapq

class Node(object):
	def __init__(self, context, feature, parent, prospects, action):
		self.feature = feature
		self.prospects = prospects
		self.context = context
		self.parent = parent
		self.actiongenerated = action
	def display(self):
		print('feature' + str(self.feature)) 
		print('prospects: ' + str(self.prospects))
		print('beat index: ' + str(self.context.currentBeatIndex))

def drawStart(startstates):
	return startstates[random.randint(0,len(startstates)-1)]

def drawActionNoRep(actions):
	list_of_key_instance_lists = [(key,)*actions[key] for key in actions.keys()]
	instances = [instance for instance_list in list_of_key_instance_lists for instance in instance_list]
	action = instances[random.randint(0,len(instances)-1)]
	return action

def findevent(actiontaken,pitchmode=None):
	if actiontaken in [SongData.NULL, SongData.REST, SongData.END, SongData.HOLD]:
		return actiontaken
	return actiontaken+pitchmode 

def findaction(actiontaken, pitchmode):
	if actiontaken in [SongData.NULL, SongData.REST, SongData.END, SongData.HOLD]:
		return actiontaken
	return actiontaken-pitchmode 

def Main(featurevectors,TOTALSONGSTOMONTECARLO = 1):
	startstates = pickle.load(open('startstates.pkl','rb'))
	observedstates = pickle.load(open('observedstates.pkl','rb'))
	montefeatures = []
	policy = dict()
	uniques = set(observedstates.keys())

	def constructFeature(context):
		previousPitch = context.previousPitch
		songPitchMode = context.songPitchMap.getMax()
		featureSongPitchTuple = SongData.constructRelativePitchDistanceVector(songPitchMode, previousPitch, False)
		if context.currentBeatIndex % SongData.BEATS_PER_BAR == 0:
			barPitchMode = None 
		else:
			barPitchMode = context.barPitchMap.getMax()
		featureBarPitchTuple = SongData.constructRelativePitchDistanceVector(barPitchMode, previousPitch, True) 
		featureUDSTuple = SongData.getUDSTuple(context.updownsame)
		featureBarMod = SongData.getBarModTuple((context.currentBeatIndex/SongData.BEATS_PER_BAR)+1)	
		return featureSongPitchTuple + featureBarPitchTuple + featureUDSTuple + featureBarMod
	
	def IterativeSearchForEnd(node):
		heap = copy.deepcopy(node.prospects.keys())
		heapq.heapify(heap) 		
		while True:
			some = None
			
	def RecursiveSearchForEnd(node):
		if node.feature in observedstates:
			node.prospects = copy.deepcopy(observedstates[node.feature])
			while len(node.prospects.keys()) > 0:
				action = drawActionNoRep(node.prospects)
				del node.prospects[action]
				node.actiongenerated = action 
				if action == SongData.END:
					print('completed song')
					return node
				context = copy.deepcopy(node.context)
				context.update(node.context.currentlyHeldNote,findevent(action, node.context.songPitchMap.getMax()))
				if action == 128:
 					print('poop')
				feature = constructFeature(context)
				lastscion = RecursiveSearchForEnd(Node(context, feature, node, None, None))
				if lastscion is not None and lastscion.actiongenerated == SongData.END:	
					return lastscion

	songs= []

	def incorporateSongIntoPolicyAndMonteFeature(node, policy, montefeatures):			    
		while node is not None:
			parent = node.parent
			montefeatures.append(node.feature)
			if node.feature not in policy:
				c = Counter()
				c[node.actiongenerated] = 1
				policy[node.feature] = c
			else:
				policy[node.feature][node.actiongenerated] += 1
			node = parent
	
	overflownstax = 0
	while len(songs) < TOTALSONGSTOMONTECARLO:
		start = drawStart(startstates)
		startBeat = start.beatwithinmeasure			
		startPitch = previousPitch = start.pitch
		startAction = start.actiongenerated
	
		event = findevent(actiontaken=startAction,pitchmode=startPitch)	#second event, first after start state
		if event != SongData.HOLD:
			currentlyHeldNote = event
		else:
			currentlyHeldNote = startPitch

		print('startPitch ' + str(startPitch))
		print('startAction ' + str(startAction))
		print('currentlyHeldNote ' + str(currentlyHeldNote))									
		print('startBeat ' + str(startBeat))	

		context = SongContextState(previousPitch,0,currentlyHeldNote,startBeat)
		context.update(previousPitch,currentlyHeldNote)	
		feature = constructFeature(context=context)
		node = Node(context,feature,None,None,None)
		try:
			terminal = RecursiveSearchForEnd(node)
			if terminal is not None:
				songs.append((start,terminal))
				incorporateSongIntoPolicyAndMonteFeature(terminal, policy, montefeatures)
		except RuntimeError:
			print('stack overflow')
			overflownstax += 1
	print("overflownstax: " + str(overflownstax))

	def convertTrajectoryToMidi(songEnds):
		def getnextnote(index,actions):	
			new_index = next((jdx for jdx, x in enumerate(actions[index:]) if x!= SongData.HOLD), None)
			if new_index is None:
				return None
			return index + new_index

		def appendNote(restDuration, pitch, noteDuration,track):
			on = midi.NoteOnEvent(tick=restDuration, velocity=20, pitch=pitch)
			track.append(on)
			off = midi.NoteOffEvent(tick=noteDuration, pitch=pitch)
			track.append(off)
		def actionsToEvents(startpitch,actions):
			events = []
			heap = PitchMap()
			heap.upsertPitch(startpitch)
			events.append(startpitch)
			for action in actions:
				if action < 128:
					newpitch = action+heap.getMax()
					heap.upsertPitch(newpitch)
					events.append(newpitch)
				else:
					events.append(action)
			return events
		start =	songEnds[0]		#start node
		node = songEnds[1]		#terminal node
		parent = node.parent
		events = []
		nodes = []
		startbeat = start.beatwithinmeasure
		while node is not None:
			parent = node.parent
			nodes.append(node)
			events.append(findevent(node.actiongenerated,node.context.songPitchMap.getMax())) 
			node = parent
		events.append(findevent(start.actiongenerated,start.pitch))
		events = events[::-1]
		valid = True
		for event in events:
			if event>131 or event<0:
				valid = False
		if not valid:
			return None
		print('events: ' + str(events))
		pattern = midi.Pattern()
		track = midi.Track()
		pattern.append(track)
		eventlength = 4*midi.Pattern().resolution/SongData.BEATS_PER_BAR
		initialRestDuration = startBeat*eventlength
		idx = getnextnote(0,events)
		noteDuration = idx+1 * eventlength
		appendNote(initialRestDuration,startPitch,noteDuration,track)
		while idx != None:
			restDuration = 0
			if events[idx] == SongData.REST:
				current = idx
				idx = getnextnote(idx+1,events)			
				restDuration = current - idx
			pitch = 0
			try:
				pitch = events[idx]
			except:
				print('ended on rest??')
				return None
			current = idx
			idx = getnextnote(idx+1,events)
			if idx is not None:
				noteDuration = (idx - current) * eventlength	
				appendNote(restDuration, pitch, noteDuration,track)
		track.append(midi.EndOfTrackEvent(tick=1))
		midi.write_midifile(os.path.join('walks',str(uuid.uuid1())+'.mid'),pattern)	
	
	for idx,songEnds in enumerate(songs):
		convertTrajectoryToMidi(songEnds)

	return policy, np.average(montefeatures, axis=0)

if __name__ == '__main__':
	featurevectors = pickle.load(open('featurevectors.pkl','rb'))
	policy, featureexpectations = Main(featurevectors,TOTALSONGSTOMONTECARLO=1)
	print("monte expectations: \n" + str(featureexpectations))
	print("observed expectations: \n" + str(np.around(a=np.average([vec.vector for vec in featurevectors], axis=0),decimals=4)))
	montepickle = open('monteexpectations.pkl', 'wb')
	pickle.dump(featureexpectations, montepickle)







			
			

	
		
		

				
		
		
        
        
        
        
        
        
        
        
        
        
        
        
        
        