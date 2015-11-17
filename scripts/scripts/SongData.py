#from __future__ import division
try:
   import cPickle as pickle
except:
   import pickle
import midi
import os.path
import random
import copy
import os
from operator import itemgetter
from collections import OrderedDict
import numpy as  np

class StartState(object):
    def __init__(self, pitch,beatindex, actiongenerated, filename):
        self.pitch = pitch
        self.beat = beatindex 
        self.actiongenerated = actiongenerated
        self.filename = filename
    def display(self):
        print("\tSTART STATE:")
        print('\t\tpitch: ' + str(self.pitch))
        print('\t\taction: ' + str(self.actiongenerated))                               
        print('\t\tbeat: ' + str(self.beat))	
        print('\t\tfile: ' + str(self.filename))
class FeatureVector(object):
    def __init__(self, vector, actiongenerated):
         self.vector = vector
         self.actiongenerated = actiongenerated
class SongContextState(object):
    def __init__(self,currentBarNumber,currentlyHeldNote, beat):
        self.songPitchMap = PitchMap()
        self.barPitchMap = PitchMap()
        self.updownsame = ['null']*SongData.TRAJECTORYHISTORYSPAN
        self.currentBeatIndex = beat
        self.currentlyHeldNote = currentlyHeldNote
        self.songPitchMap.upsertPitch(currentlyHeldNote)
        self.barPitchMap.upsertPitch(currentlyHeldNote)
    def update(self,newevent):
        self.currentBeatIndex+=1
        tonalcenter = self.songPitchMap.getPitchMax(SongData.REST)
        actiongenerated = SongData.findaction(newevent,tonalcenter)
        udsSymbol = SongData.getUDSSymbol(self.currentlyHeldNote, newevent)					
        SongData.updateUDS(self.updownsame, udsSymbol)
        if newevent != SongData.HOLD:
            self.currentlyHeldNote = newevent	

        self.feature = FeatureVector(constructFeature(self),None)

        self.songPitchMap.upsertPitch(self.currentlyHeldNote)
        if self.currentBeatIndex%SongData.BEATS_PER_BAR==0:
            self.barPitchMap= PitchMap()
        self.barPitchMap.upsertPitch(self.currentlyHeldNote)
class Node(object):
    def __init__(self, context, feature, parent, prospects, action,utility=None):
        self.feature = feature
        self.prospects = prospects
        self.canonicalprospects = prospects
        self.context = context
        self.parent = parent
        self.actiongenerated = action
        self.generatedbyaction = None
        self.isMutant = False
        self.utility = utility
    def display(self):
        print('\tNODE: ')
        print('\t\tfeature' + str(self.feature)) 
        print('\t\tprospects: ' + str(self.prospects))
        print('\t\tbeat index: ' + str(self.context.currentBeatIndex))

    def __cmp__(self, other):
        return cmp(self.utility, other.intAttribute)
def drawStart(startstates):
    return startstates[random.randint(0,len(startstates)-1)]

def drawFeature(features):
    return features[random.randint(0,len(features)-1)]

def drawActionNoRep(actions):
    list_of_key_instance_lists = [(key,)*actions[key] for key in actions.keys()]
    instances = [instance for instance_list in list_of_key_instance_lists for instance in instance_list]
    action = instances[random.randint(0,len(instances)-1)]
    return action

def findnextevent(actiontaken, pitchmode):
    if actiontaken in [SongData.NULL, SongData.REST, SongData.END, SongData.HOLD]:
        return actiontaken
    return actiontaken-pitchmode 

def findevent(actiontaken,pitchmode=None):
    if actiontaken in [SongData.NULL, SongData.REST, SongData.END, SongData.HOLD]:
        return actiontaken
    return actiontaken+pitchmode

def averageProspects(prospects1,prospects2):
    for prospect in prospects2.keys():
        if prospect in prospects1:
            prospects1[prospect] += prospects2[prospect]
        else: 
            prospects1[prospect] = prospects2[prospect] 
    for prospect in prospects1.keys():
        prospects1[prospect] = int(round((prospects1[prospect] / float(2))))
    return prospects1

def sexuallyGenerateProspects(observedstates):
    mommy = drawFeature(observedstates.keys())
    daddy = drawFeature(observedstates.keys())
    while(mommy == daddy):
        daddy = drawFeature(observedstates.keys())
    mommyProspects = copy.deepcopy(observedstates[mommy])
    daddyProspects = copy.deepcopy(observedstates[daddy])
    return averageProspects(mommyProspects,daddyProspects)

def getOnes(vec):
    return [idx for idx, elem in enumerate(vec) if elem==1]

def printOnes(vec):
    print('ONES: '+str(getOnes(vec)))

def constructFeature(context):	
    songPitchMode = context.songPitchMap.getPitchMax(SongData.REST)
    featureSongPitchTuple = SongData.constructRelativePitchDistanceVector(songPitchMode, context.currentlyHeldNote)
    barPitchMode = context.barPitchMap.getPitchMax(SongData.REST)
    featureBarPitchTuple = SongData.constructRelativePitchDistanceVector(barPitchMode, context.currentlyHeldNote) 
    featureUDSTuple = SongData.getUDSTuple(context.updownsame)
    featureBarMod = SongData.getBarModTuple((context.currentBeatIndex/SongData.BEATS_PER_BAR)+1)	 
    innerPos = interiorOctile(context.currentBeatIndex)
    feature = featureSongPitchTuple + featureBarPitchTuple + featureUDSTuple + featureBarMod + innerPos + ((context.currentBeatIndex%2),)
    return feature
def interiorOctile(beat):
    intOct = (beat%SongData.BEATS_PER_BAR) / 4
    return (0,)*intOct+((1,))+((0,)*(7-intOct))

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
        try:
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
        except KeyError:
            return None

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
    def upsertPitch(self, pitch, incrementation=1):
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

class SongData(object):
    REST = 128
    HOLD = 129
    NULL = 130
    END = 131

    LONOTE = 48
    HINOTE = 84

    BEATS_PER_BAR = 32
    MAXHOLDBARS = 2

    TRAJECTORYHISTORYSPAN = 8

    def __init__(self, pattern, filename,tracknumber=1):  
        self.filename = filename
        self.eventset = []
        self.featurevectors = []
                
        #get local copies of class constants
        REST = self.REST
        HOLD = self.HOLD
        NULL = self.NULL
        END = self.END
        LONOTE = self.LONOTE
        HINOTE = self.HINOTE

        BEATS_PER_BAR = self.BEATS_PER_BAR  


        track = pattern[tracknumber]			
        
        self.uniquepitches = set()

        resolution = pattern.resolution							#length of quarter note
        actionLength = resolution/float(BEATS_PER_BAR/4)		#length of action
        def getNotes(track):
            currNote, on, ticks, notes = (), False, 0, []
            for idx, event in enumerate(track):
                if 'Note' in event.name:
                    event.tick += ticks
                    currNote += (event,)
                    on, ticks = not on, 0
                    if not on:
                        notes.append(currNote)
                        currNote = ()  
                else:
                    ticks += event.tick
            return notes 
        def getTicks(on, off):
            sum(x.tick for x in track[on+1:off])     
        try:
            notes = getNotes(track)
        except Exception as e:
            print("error building notes list in:" + str(filename))
        
        #function to quantize note durations
        def roundLength(actionLength, noteLength):
            units = round(noteLength/actionLength)
            return int(units)
                 
        quantizationBias = 0                	#this can generally be 
                                                #any integer on the interval: 0 +/- (actionLength/2)
                                                #and is used to offset the start time of events which 
                                                #follow events that have been quantized
        
        #map midi notes to actions
        #each note is a 2-tuple containing a note on and note off signal
        for note in notes:      
            noteStart = note[0].tick - quantizationBias                             #offset observed note value by
                                                                                    #quantization bias from previous notes 
                                                                                    
                          
            numberOfRests = roundLength(actionLength, noteStart)					#number of rest actions in this note

            quantizationBias = (numberOfRests*actionLength) - noteStart				#this is equal to the rounded note length
                                                                                    #minus the observed note length
            if numberOfRests > 0:
                self.eventset.append(REST)											#append rest 

                self.eventset += [HOLD]*(numberOfRests-1)							#append hold actions for 
                                                                                    #rest duration - 1 time steps
            note_end = note[1].tick - quantizationBias 
            numberOfSustains = roundLength(actionLength, note_end)					#number of sustain actions in this note

            quantizationBias = (numberOfSustains*actionLength) - note_end			#this is equal to the rounded note length
                                                                                    #minus the observed note length
            if numberOfSustains > 0:
                self.eventset.append(note[0].pitch)								#append pitch on action

                self.eventset += [HOLD]*(numberOfSustains-1)						#append hold actions for 
                                                                                    #pitch duration - 1 time steps
                self.uniquepitches.add(note[0].pitch)

        self.eventset.append(END)													#append end of song action
        try:
            self.deleteLongHolds()
        except IndexError:
            print("index error deleting holds in " + str(self.filename))
        self.startstate = self.findstartstate()
        ##now set feature vectors
        self.computeFeatureVectors(actions=self.eventset, filename=self.filename)	
        
    
    def computeFeatureVectors(self, actions, filename=""):
        print('computing features for file: ' + filename)
        states = set()
        startindex = self.findstartindex()			                                #first non rest note
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

        barPitchMapsList = list()													#list of previous bar pitch distributions
        barModPitchMapsList = [PitchMap()] * 8										#summary of bar pitch distributions by modulus
                                                                                    #0 meaning the start bar

        previousPitch = currentlyHeldNote
        
        currentBarNumber = 1
        positionInCurrentBar = 0

        startpitch = self.startstate.pitch
        context = SongContextState(0, startpitch, startindex)
        startaction = self.findnextevent(startindex,context.songPitchMap.getPitchMax(SongData.REST))
        self.startstate = StartState(startpitch, startindex, startaction, filename)
        #feature vectors
        firstfeatureIndex = startindex + 1
        for idx, event in enumerate(self.eventset[firstfeatureIndex:len(self.eventset)-1]):
            idx += firstfeatureIndex 
            context = copy.deepcopy(context)				
            context.update(event)
            context.feature.actiongenerated = self.findnextevent(idx,context.songPitchMap.getPitchMax(SongData.REST))
            self.featurevectors.append(context.feature)
									    
    @staticmethod
    def constructRelativePitchDistanceVector(pitchMode, currentPitch):
        distanceTuple = ()
        newbit = ()
        distanceExists = True if pitchMode is not None else False
        if currentPitch == SongData.REST:										#previous action was rest bit (1 bit)
            newbit = (1,)
            distanceTuple += newbit
            distanceExists = False
        else:
            newbit = (0,)
            distanceTuple += newbit
        if pitchMode == SongData.REST:										#previous action was rest bit (1 bit)
            newbit = (1,)
            distanceTuple += newbit
            distanceExists = False
        else:
            newbit = (0,)
            distanceTuple += newbit
        if distanceExists:													#was i pitches above pitchMode bits (12 bits) 
            currentPitchMod = currentPitch % 12
            pitchDifference =	(currentPitch%12-pitchMode%12
                                ) if (
                                currentPitch%12 >= pitchMode%12
                                ) else (
                                currentPitch%12+12-pitchMode%12)
            distanceTuple +=	(0,)*pitchDifference+(
                                (1,))+(
                                (0,)*(11-pitchDifference))	
                
        else:
            distanceTuple += (0,)*12

        if distanceExists:
            pitchDifference =  currentPitch-pitchMode
            wasAbove = True if pitchDifference >= 0 else False
            distanceTuple += (0,) if wasAbove else (1,)
            octavesAway = abs(pitchDifference/12)
            distanceTuple +=  (0,)*octavesAway+(
                              (1,))+(
                              (0,)*(9-octavesAway))	

        else:
            distanceTuple += (0,) + (0,)*10
        return distanceTuple

    @staticmethod
    def getUDSSymbol(currentlyHeld, nextEvent):
        udsSymbol = ''
        if currentlyHeld == SongData.REST:
            udsSymbol += 'p'
        if currentlyHeld == SongData.NULL:
            udsSymbol += 'null'			
        elif nextEvent == SongData.REST:
            udsSymbol += 'c'
        else:
            if currentlyHeld == nextEvent or nextEvent == SongData.HOLD:
                udsSymbol = 's'
            elif currentlyHeld < nextEvent:
                udsSymbol = 'u'
            elif currentlyHeld > nextEvent:
                udsSymbol = 'd'
        return udsSymbol
   
    @staticmethod
    def getUDSTuple(updownsame):
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
            print("exception in file: " + filename)
            print("UpDownSame_PreviousEightPitchStrikes index: " + str(idx)) 
        return udsTuple

    @staticmethod
    def updateUDS(updownsame,udsSymbol):
        del updownsame[0]
        updownsame.append(udsSymbol)
    
    def deleteLongHolds(self):
        for idx,action in enumerate(self.eventset):
            if action == SongData.HOLD:
                holdEnd = next((jdx for jdx, x in enumerate(self.eventset[idx:]) if x!= SongData.HOLD), None) 
                maxLength = SongData.MAXHOLDBARS*SongData.BEATS_PER_BAR
                holdLength = holdEnd-idx+1
                if holdLength >= maxLength: 
                    remainder = holdLength % maxLength
                    self.eventset[idx+remainder:holdEnd+1] = []

    @staticmethod	
    def getBarModTuple(currentBarNumber):
        barMod4Tuple = tuple()
        barMod4 = (currentBarNumber-1)%4

        barMod4Tuple += (0,)*barMod4+(
                        (1,))+(
                        (0,)*(3-barMod4))
        return barMod4Tuple 


    def findstartstate(self):
        startindex = self.findstartindex() 
        startpitch = self.eventset[startindex]
        return StartState(startpitch, startindex, self.findnextevent(startindex,startpitch),self.filename)	
    def findstartindex(self):
        return next((i for i, x in enumerate(self.eventset) if x!= self.REST and x!= self.HOLD), None)  
    @staticmethod	
    def findaction(event,pitchmode):
        if event in [SongData.NULL, SongData.REST, SongData.END, SongData.HOLD]:
            return event
        return event-pitchmode
    def findnextevent(self,index,pitchmode):
        try:
            nextobservation = self.eventset[index+1]
            return self.findaction(nextobservation, pitchmode)
        except IndexError:
            print(self.filename + " attempted a bad index access in findnextevent.")
            print("    " + "occurred attempting to access index " + str(index+1))
            print("    " + "true length of eventset was: " + str(len(self.eventset)))
            print("    " + "current observation was: " + str(self.eventset[index]))

            
    #observedstates = set()
    #featurevectors = []
    #with open('featurevectors.pkl', 'rb') as input:
    #	featurevectors = pickle.load(input)
    
    #with open('observedstates.pkl', 'rb') as input:
    #	observedstates = pickle.load(input)
    #print('featurevectors length: )' + len(featurevectors))
    #print('observedstates: )' + len(observedstates))

    #with open('SongDataList.pkl', 'wb') as output:
    #    pickle.dump(songs, output)
    #with open('SongDataList.pkl', 'rb') as input:
    #	songs = pickle.load(input)
    #valid_tracks = 0
    #valid_songs = []
    #for song in songs:
    #	out_of_range = False
    #	for action in song.eventset:
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