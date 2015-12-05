from __future__ import print_function
try:
   import cPickle as pickle
except:
    import pickle 

import random 
import copy
from collections import Counter
import midi
import math
import sklearn
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import numpy as np
import timeit
import random
import datetime
from routez import *
import os.path
import os
import uuid
from operator import itemgetter
from collections import OrderedDict

def getDerivedPickles():
    tfam  = pload(tfam_pickle_string)
    return tfam,getModelPickles()
def getModelPickles():
    pca = pload(pca_pickle_string)
    cmodels = get_cmodels()
    return pca, cmodels
def getRawPickles():
    songs = pload('songs.pkl')
    return songs, getRawFeaturePickles()
def getRawFeaturePickles():
    featurevectors = pload(featurevector_pickle_string)
    startstates = pload(startstate_pickle_string)
    return featurevectors, startstates

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

def DimReducer(X, transformers):
    '''X is an array_like and transformers is an ordered list of functions,
    where the first element accepts an array_like the shape of X and where all subsequent elements accept as their sole input an array_like object the same shape as is output by their predecessor
    '''
    
    for transform in transformers:        
        X = transform(X)

    return X
def get_cmodels():
    Ncluster = pload(ncluster_pickle_string)
    Rcluster = pload(rcluster_pickle_string)
    return [Ncluster,Rcluster]
def clustermodelheuristic(feature,cmodels):
    return cmodels[0] if feature[0] == 0 else cmodels[1]

def pdump(obj,filename,noPrefix=False):
    prefix = "" if noPrefix else outputmodelname
    out = open(os.path.join(pickleDir,prefix+filename), 'wb')
    pickle.dump(obj,out,-1)
def pload(filename,noPrefix=False):
    prefix = "" if noPrefix else inmodelname
    return pickle.load(open(os.path.join(pickleDir,prefix+filename),'rb'))

def IntegerizeArray(arr):
    return np.array(np.around(arr,decimals=0),dtype='int32')

def empiricalestimate(songs,pca):
    from SongData import SongData
    accumulatations = [0]
    for song in songs:
        accumulatations = np.add(accumulatations,get_song_discounted_feature_expectations(song,pca))
    expectations = accumulatations/len(songs)
    return expectations

def get_song_discounted_feature_expectations(song,pca, gamma = 0.9):
    from SongData import SongData
    accumulatations = [0]
    for timestep,feature in enumerate(song.featurevectors):
        vector = pca.transform(feature.vector)
        accumulatations = np.add(accumulatations,math.pow(gamma,timestep)*np.array(vector))
    return accumulatations

def discount_and_accumulate_ordered_feature_list(olist, gamma = 0.9):
    accumulatations =[0]
    for timestep,vector in enumerate(olist):
        accumulatations = np.add(accumulatations,math.pow(gamma,timestep)*np.array(vector))
    return accumulatations

def getOnes(vec):
    return [idx for idx, elem in enumerate(vec) if elem==1]

def printOnes(vec):
    print('ONES: '+str(getOnes(vec)))

def SemanticizeFeature(feature):
    facts = []
    if len(feature) < 2:
        feature = (feature,'UNKNOWN')

    assertions = list(sorted(getOnes(feature[0])))
    assertionset = set(assertions)

    for assertion in assertions:
        #pitch facts:
        if assertion == 0:
            facts.append('Current note is a rest.')
        if assertion == 1:
            facts.append('Song pitch mode is a rest.')
        if assertion >= 2 and assertion <=13:
            facts.append('Current note is pitch ' + str(assertion-2)+' in the song pitch modes chromatic scale.')
            if 14 in assertionset:
                facts.append('Current note was above songs pitch mode.')
            else:
                facts.append("Current note wasn't above songs pitch mode.")
        if assertion >= 15 and assertion <=24:
            facts.append('Current note is  ' + str(assertion-15)+' octaves away from song pitch mode.')
        if assertion == 26:
            facts.append('Bar pitch mode is a rest.')
        if assertion >= 27 and assertion <=38:
            facts.append('Current note is pitch ' + str(assertion-27)+' in the bar pitch modes chromatic scale.')
            if 39 in assertionset:
                facts.append('Current note was above bar pitch mode.')
            else:
                facts.append("Current note wasn't above bar pitch mode.")
        if assertion >= 40 and assertion <= 49:
            facts.append('Current note is  ' + str(assertion-40)+' octaves away from bar pitch mode.')
        
        #last eight event facts
        if assertion >= 50 and assertion <= 89: 
            notesago = ((assertion-50)/5)+1   
            eventpart = ((assertion-50)%5)
            if eventpart == 0:
                facts.append(str(notesago) + ' note ago was above the note previous to it.')
            if eventpart == 1:
                facts.append(str(notesago) + ' note ago was below the note previous to it.')
            if eventpart == 2:
                facts.append(str(notesago) + ' note ago was the same as the note previous to it.')
            if eventpart == 3:
                facts.append(str(notesago-1) + ' note ago was a rest.')
            if eventpart == 4:
                facts.append(str(notesago) + ' note ago was a rest.')
        if assertion >= 90 and assertion <= 93: 
            facts.append('Note occurred in measure number ' + str(assertion-90) + ' as mod 4 of total bars.')
        if assertion >= 94 and assertion <= 101:
            facts.append('Note occurred in octile ' + str(assertion-94) + ' of its respective measure.')
    if 102 in assertionset:
        facts.append('Note occurred on odd beat.') 
    else:
        facts.append('Note occurred on even beat.')
    print('EVENT HAPPENED '+ str(feature[1]) + ' times and had these features:\n\t'+"\n\t".join(facts))
    return  "\t"+"\n\t".join(facts)
