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

class PickleTainer(object):
     def __init__(self, **kwargs):
         self.__dict__.update(kwargs)

class PitchMap(object):
	#some max heap functionality using dicts
	#pitch with longest length will always be at Index_Pitch[0]
	#with single unit increments on update, upserts are O(1)
	def __init__(self):
		self.Pitch_Length = dict()
		self.Pitch_Index = dict()
		self.Index_Pitch = dict()
		self.top = 0
	#helper method definitions:
	def getMax(self):
		if self.top > 0:
			return self.Index_Pitch[0]
		else:
			return None
	def getPitchMax(self,REST):
		max = self.Index_Pitch[0]
		if max != REST:
			return self.Index_Pitch[0]
		else:
			pitch1 = self.Index_Pitch[1]
			if self.top == 2:			
				return pitch1				#2 elems total in heap
			else:
				pitch2 = self.Index_Pitch[2]
				count1 = self.Pitch_Length[pitch1]
				count2 = self.Pitch_Length[pitch2]
				return pitch2 if count2 > count1 else pitch1

	def bubbleUp(self, bubbleIndex):
		def swap(bubbleIndex, parentIndex):
			#swap indices of pitch
			parentPitch = self.Index_Pitch[parentIndex]	
			bubblePitch = self.Index_Pitch[bubbleIndex]

			self.Index_Pitch[parentIndex] = bubblePitch
			self.Pitch_Index[bubblePitch] = parentIndex

			self.Index_Pitch[bubbleIndex] = parentPitch
			self.Pitch_Index[parentPitch] = bubbleIndex
		parentIndex = (bubbleIndex - 1) / 2;
		bubblePitch = self.Index_Pitch[bubbleIndex]
		bubbleLength = self.Pitch_Length[bubblePitch]
		parentPitch = self.Index_Pitch[parentIndex]
		parentLength = self.Pitch_Length[parentPitch]
		while	(
				bubbleLength > 
				parentLength
				):
				swap(bubbleIndex, parentIndex)
				bubbleIndex = parentIndex
				if bubbleIndex==0:	#terminate
					parentLength = bubbleLength
				else:
					parentIndex = (bubbleIndex - 1) / 2
					parentPitch = self.Index_Pitch[parentIndex]
					parentLength = self.Pitch_Length[parentPitch]
	def upsertAction(self, pitch, incrementation=1):
		if pitch not in self.Pitch_Length:
			self.Pitch_Length[pitch] = incrementation
			self.Pitch_Index[pitch] = self.top
			self.Index_Pitch[self.top] = pitch 
			self.top += 1
		else:																		
			count = self.Pitch_Length[pitch]										#get current count from first item in value
			index = self.Pitch_Index[pitch]											#get index from second item in value
			self.Pitch_Length[pitch] = count + incrementation						#increment count			
				
			if index > 0:															#max never bubbles up 
				self.bubbleUp(index)

class StartState(object):
    def __init__(self, pitch, beatspermeasure, beatindex, actiongenerated):
		self.pitch = pitch
		self.beatwithinmeasure = beatindex % beatspermeasure
		self.actiongenerated = actiongenerated
class FeatureVector(object):
	 def __init__(self, vector, actiongenerated):
		 self.vector = vector
		 self.actiongenerated = actiongenerated

class SongData(object):
	REST = 128
	HOLD = 129
	NULL = 130
	END = 131

	LONOTE = 48
	HINOTE = 84

	BEATS_PER_BAR = 32


	def __init__(self, pattern, filename):  
		self.filename = filename
		self.actionset = []
		self.featurevectors = []
				
		#get local copies of class constants
		REST = self.REST
		HOLD = self.HOLD
		NULL = self.NULL
		END = self.END
		LONOTE = self.LONOTE
		HINOTE = self.HINOTE

		BEATS_PER_BAR = self.BEATS_PER_BAR  

		track = pattern[1]			#pattern has been preprocessed to contain only 
									#one track of musical information, which contains the
									#heuristically selected, expected melody 

		resolution = pattern.resolution							#length of quarter note
		actionLength = resolution/float(BEATS_PER_BAR/4)		#length of action
		     
		notes = [
				(track[idx],track[idx+1])						#pair note ons with note offs 
				for idx, evt in enumerate(track) 
				if evt.name == 'Note On' and idx % 2 == 0
				]
		
		#function to quantize note durations
		def roundLength(actionLength, noteLength):
			units = round(noteLength/actionLength)
			return int(units)
				 
		quantizationBias = 0		#this can generally be 
									#any integer on the interval: 0 +/- (actionLength/2)
									#and is used to offset the start time of events which 
									#follow events that have been quantized
		
		#map midi notes to actions
		#each note is a 2-tuple containing a note on and note off signal
		for note in notes:      
			noteStart = note[0].tick + quantizationBias								#offset observed note value by
																					#quantization bias from previous notes 
																					
				          
			numberOfRests = roundLength(actionLength, noteStart)					#number of rest actions in this note

			quantizationBias = (numberOfRests*actionLength) - noteStart				#this is equal to the rounded note length
																					#minus the observed note length
			if numberOfRests > 0:
				self.actionset.append(REST)											#append rest 

				self.actionset += [HOLD]*(numberOfRests-1)							#append hold actions for 
																					#rest duration - 1 time steps
			note_end = note[1].tick + quantizationBias
			numberOfSustains = roundLength(actionLength, note_end)					#number of sustain actions in this note

			quantizationBias = (numberOfSustains*actionLength) - note_end			#this is equal to the rounded note length
																					#minus the observed note length
			if numberOfSustains > 0:
				self.actionset.append(note[0].pitch)								#append pitch on action

				self.actionset += [HOLD]*(numberOfSustains-1)						#append hold actions for 
																					#pitch duration - 1 time steps

		self.actionset.append(END)													#append end of song action
		self.startstate = self.findstartstate()
		##now set feature vectors
		#self.computeFeatureVectors(actions=self.actionset)			
	
	def computeFeatureVectors(self, actions):
		states = set()
		startindex = self.findstartindex()				#first non rest note
		#FEATURES
		tupleOfFeatures=	(
								"Distance_PreviousPitchToSongPitchMode"
								,"Distance_CurrentBarsPitchModeToSongsPitchMode"
								,"UpDownSame_PreviousEightPitchStrikes"
								,"SongBarMod4"
								#,"Distance_CurrentBarsSecondPitchModeToSongsPitchMode"
								#,"Distance_CurrentBarsThirdPitchModeToSongsPitchMode"
								#,"Distance_CurrentBarsPitchModeToSongsSecondPitchMode"
								#,"Distance_CurrentBarsPitchModeToSongsThirdPitchMode"
								#,"Distance_PitchModeOfBarsEqualToCurrentBarMod4ToSongPitchMode"
								#,"Distance_PitchModeOfBarsEqualToCurrentBarMod4Minus1ToSongPitchMode"
								#,"Distance_PitchModeOfBarsEqualToCurrentBarMod4Minus2ToSongPitchMode"
								#,"Distance_PitchModeOfBarsEqualToCurrentBarMod4Minus3ToSongPitchMode"
								#,"SongBarMod8"
								#,"SongBarMod16"
								#,"PreviousActionWasHold"
							)

		#song state variables for computing feature vectors
		currentlyHeldNote = self.NULL												#value of most recently struck note
		songPitchMap = PitchMap()													#2 dicts as max heap for song pitch distribution
		barPitchMap = PitchMap()													#2 dicts as max heap for bar pitches distribution
		barPitchMapsList = list()													#list of previous bar pitch distributions
		barModPitchMapsList = [PitchMap()] * 8										#summary of bar pitch distributions by modulus
																					#0 meaning the start bar

		previousPitch = currentlyHeldNote
		
		currentBarNumber = 0
		positionInCurrentBar = 0

		TRAJECTORYHISTORYSPAN = 8
		updownsame = ['null']*TRAJECTORYHISTORYSPAN									#last TRAJECTORYHISTORYSPAN actions:
																						#u = up
																						#d = down
																						#s = same
		#feature vector algorithm
		for idx, action in enumerate(self.actionset[startindex:len(self.actionset)-1]):
			idx += startindex

			#bookkeeping first
			positionInCurrentBar = idx % self.BEATS_PER_BAR

			#here we are starting a new bar
			if positionInCurrentBar == 0:
				currentBarNumber += 1
				#here we are starting any bar after the first bar... 
				#this specifically means we should store the previous bar's pitch distribution dictionary, 
				#and reset the bar's state
				if currentBarNumber > 1:
					barPitchMapsList.append(barPitchMap)			#store previous bar's pitch distribution
					currentBarMod = (currentBarNumber-2) % 8
					currentBarModPitchMap = barModPitchMapsList[currentBarMod]
					for pitch in barPitchMap.Pitch_Length.keys():
						currentBarModPitchMap.upsertAction(pitch=pitch, incrementation=barPitchMap.Pitch_Length[pitch]) 
					barPitchMap = PitchMap()
			
			#this is the case when a note changes	
			if action != self.END and action != self.HOLD:
				currentlyHeldNote = action

			if action != self.END:
				
				barPitchMap.upsertAction(currentlyHeldNote)			#inserts or updates, increments heaps length, 
																	#and bubbles up if necessary 
				songPitchMap.upsertAction(currentlyHeldNote)

				#now construct feature vector
				if idx > startindex:
					tempDict = {-1:tupleOfFeatures}
					self.rowFeatureTuples = dict([(i, k) for k, v in tempDict.
											iteritems() 
											for i in v])										#will be concatenated together later to make 
																								#featureRow..-1 used as placeholder for feature
																						 		#values which will ultimately 
																								#become binary tuples
																							
					#1.
					#"Distance_PreviousPitchToSongPitchMode"
					#
					try:
						pitchMode = songPitchMap.getMax()
						distanceTuple = self.constructRelativePitchDistanceVector(pitchMode=pitchMode, previousAction=previousPitch)				
						self.rowFeatureTuples["Distance_PreviousPitchToSongPitchMode"] = distanceTuple
					except Exception as e:
						print(filename+str(e))
						import traceback, os.path
						top = traceback.extract_stack()[-1]
						print ', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])])
					#2.
					#"Distance_CurrentBarsPitchModeToSongsPitchMode"
					#
					try:
						pitchMode = barPitchMap.getMax()
						distanceTuple = self.constructRelativePitchDistanceVector(pitchMode=pitchMode, previousAction=previousPitch)				
						self.rowFeatureTuples["Distance_CurrentBarsPitchModeToSongsPitchMode"] = distanceTuple
					except Exception as e:
						print(filename+str(e))
						import traceback, os.path
						top = traceback.extract_stack()[-1]
						print ', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])])
					#3.
					#"UpDownSame_PreviousEightPitchStrikes"
					#
					udsSymbol = ''
					if previousPitch == self.REST:
						udsSymbol += 'p'			
					if currentlyHeldNote == self.REST:
						udsSymbol += 'c'
					if previousPitch != self.REST and currentlyHeldNote != self.REST:
						if previousPitch < currentlyHeldNote:
							udsSymbol = 'u'
						if previousPitch > currentlyHeldNote:
							udsSymbol = 'd'
						if previousPitch == currentlyHeldNote:
							udsSymbol = 's'
				
					del updownsame[0]
					updownsame.append(udsSymbol)
					udsTuple = tuple()
					try:
					    for i in updownsame:
							if i == 'null':					#there was no previous
								udsTuple += (0,0,0,0,0)
							elif i == 'u':					#moved up from previous
								udsTuple +=(1,0,0,0,0)
							elif i == 'd':					#moved down from previous
								udsTuple +=(0,1,0,0,0)
							elif i == 's':					#moved down from previous
								udsTuple +=(0,0,1,0,0)
							else:
								udsTuple +=(0,0,0)
								if 'p' in i:				#previous was a rest
									udsTuple +=(1,)
								else:
									udsTuple +=(0,)			#previous was a rest
								if 'c' in i: 
									udsTuple +=(1,)			#current is a rest
								else:
									udsTuple +=(0,)			#current not a rest
					except Exception as e:
						print(filename+str(e))
						import traceback, os.path
						top = traceback.extract_stack()[-1]
						print ', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])])

					self.rowFeatureTuples["UpDownSame_PreviousEightPitchStrikes"] = udsTuple

					#4.
					#"SongBarMod4"
					#
					barMod4Tuple = tuple()
					barMod4 = (currentBarNumber-1)%4

					barMod4Tuple += (0,)*barMod4+(
									(1,))+(
									(0,)*(3-barMod4))

					self.rowFeatureTuples["SongBarMod4"] = barMod4Tuple

					features = [self.rowFeatureTuples[feature] for feature in tupleOfFeatures]		
																									#get all the feature tuples
					featvec = tuple(bit for f in features for bit in f)								#store them as one vector
					try:
						feature = FeatureVector(featvec,self.findaction(idx, songPitchMap.getPitchMax(self.REST)))	#construct feature object
					except IndexError:
						print("Bad index access attempting to construct feature at actionset index " + str(idx) + " in file: " + self.filename )
					if(len(featvec)!=84):
						print(self.filename)
					else:
						self.featurevectors.append(feature)			
				previousPitch = currentlyHeldNote	

	def constructRelativePitchDistanceVector(self, pitchMode, previousAction):
		distanceTuple = ()
		distanceExists = True
		if previousAction == self.REST:										#previous action was rest bit (1 bit)
			distanceTuple += (1,)
			distanceExists = False
		else:
			distanceTuple += (0,)
		if distanceExists:													#was i pitches above pitchMode bits (12 bits) 
			previousActionMod = previousAction % 12
			pitchDifference =	(previousAction%12-pitchMode%12
								) if (
								previousAction%12 >= pitchMode%12
								) else (
								previousAction%12+12-pitchMode%12)
			distanceTuple +=	(0,)*pitchDifference+(
								(1,))+(
								(0,)*(11-pitchDifference))			
		else:
			distanceTuple += (0,)*12
		if distanceExists:
			pitchDifference =  previousAction-pitchMode
			wasAbove = True if pitchDifference >= 0 else False
			distanceTuple += (0,1) if wasAbove else (1,0)
			octavesAway = abs(pitchDifference/12)
			distanceTuple +=  (0,)*octavesAway+(
							  (1,))+(
							  (0,)*(3-octavesAway))	

		else:
			distanceTuple += (0,)*2 + (0,)*4

		return distanceTuple
	
	def findstartstate(self):
		startindex = self.findstartindex()
		startpitch = self.actionset[startindex]
		return StartState(startpitch, self.BEATS_PER_BAR, startindex+1, self.findaction(startindex,startpitch))	
	def findstartindex(self):
		return next((i for i, x in enumerate(self.actionset) if x!= self.REST and x!= self.HOLD), None)
	def findaction(self,index,pitchmode):
		try:
			currentobservation = self.actionset[index]
			nextobservation = self.actionset[index+1]
			if nextobservation in [self.NULL, self.REST, self.END, self.HOLD]:
				return i
			return pitchmode-nextobservation 
		except IndexError:
			print(self.filename + " attempted a bad index access in findaction.")
			print("\t" + "occurred attempting to access index " + str(index+1))
			print("\t" + "true length of actionset was: " + str(len(self.actionset)))
			print("\t" + "current observation was: " + str(currentobservation))

			
	#observedstates = set()
	#featurevectors = []
	#with open('featurevectors.pkl', 'rb') as input:
	#	featurevectors = pickle.load(input)
	
	#with open('observedstates.pkl', 'rb') as input:
	#	observedstates = pickle.load(input)
	#print('featurevectors length: )' + len(featurevectors))
	#print('observedstates: )' + len(observedstates))
	#print('poop')

	#with open('SongDataList.pkl', 'wb') as output:
	#    pickle.dump(songs, output)
	#with open('SongDataList.pkl', 'rb') as input:
	#	songs = pickle.load(input)
	#valid_tracks = 0
	#valid_songs = []
	#for song in songs:
	#	out_of_range = False
	#	for action in song.actionset:
	#		if (action > 84 and action < 128) or action < 48:
	#			out_of_range = True
	#		if not out_of_range:
	#			valid_songs.append(song)
	#with open('ValidSongDataList.pkl', 'wb') as output:
	#	  pickle.dump(valid_songs, output)

#featurevectors = []
#observedstates = set()
#with open('featurevectors.pkl', 'rb') as input:
#	featurevectors = pickle.load(input)



