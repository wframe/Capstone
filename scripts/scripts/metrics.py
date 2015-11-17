from __future__ import print_function
try:
   import cPickle as pickle
except:
    import pickle 
from SongData import *
from SongData import SongData
import GenerateRandomPolicy as grp
import random 
import copy
from collections import Counter
import midi
import math

def write_featurefreq_csv(observedstates):
    prospects = [observedstates[feature] for feature in observedstates]
    sums = sorted([sum(prospect.values()) for prospect in prospects])
    with open('featurefreq.csv','w+') as f:
        print('index,count',file=f)
        for idx,s in enumerate(sums):
            print(str(idx)+','+str(s), file=f)
    
    

if __name__ == '__main__':
    #featurevectors = pickle.load(open('featurevectors.pkl','rb'))
    #startstates = pickle.load(open('startstates.pkl','rb'))
    observedstates = pickle.load(open('observedstates.pkl','rb'))
    #finalstates = pickle.load(open('finalstates.pkl','rb'))


    write_featurefreq_csv(observedstates)
