from __future__ import print_function
try:
   import cPickle as pickle
except:
    import pickle 
from SongData import *
from SongData import SongData
import generate_random_policy as grp
import random 
import copy
from collections import Counter
import midi
import math

def write_featurefreq_csv(observedstates):
    prospects = [observedstates[feature] for feature in observedstates]
    sums = sorted([sum(prospect.values()) for prospect in prospects])
    print("AVERAGE FEATURE FREQUENCY: \n" + str(np.average(sums)))
    with open('featurefreq3_no_log_full.csv','w+') as f:
        print('index,count',file=f)
        for idx,s in enumerate(sums):
            print(str(idx)+','+str((s)), file=f)

def write_branchfreq_csv(observedstates):
    prospects = [observedstates[feature] for feature in observedstates]
    counts = sorted([len(prospect.keys()) for prospect in prospects])
    print("AVERAGE BRANCHING FACTOR: \n" + str(np.average(counts)))
    with open('branchfreq2.csv','w+') as f:
        print('index,count',file=f)
        for idx,s in enumerate(counts):
            print(str(idx)+','+str(s), file=f)
        
    

if __name__ == '__main__':
    featurevectors,startstates = getRawFeaturePickles()

    print("FEATURE EXPECTATIONS: \n" + str(np.around(a=np.average([vec.vector for vec in featurevectors], axis=0),decimals=2)))
    print("NUMBER OF STATES: \n" + str(len(featurevectors)))

    print("UNIQUE START STATES: \n" + str(len(set(startstates))))
    #write_featurefreq_csv(observedstates)
    #write_branchfreq_csv(observedstates)