try:
   import cPickle as pickle
except:
    import pickle 
from SongData import *
from SongData import SongData
import random 
import copy
from collections import Counter
import numpy as np
import midi
import ValueIteration as vi
import GenerateRandomPolicy as grp
from scipy.linalg import norm

def Main(featurevectors,startstates,extendedstates,observedstates,finalstates,featureexpectations,espilon=.001):
    MuEMPIRICAL = (np.around(a=np.average([vec.vector for vec in featurevectors], axis=0),decimals=4))
    MuMONTE_1, MuMONTE_2 = featureexpectations, None
    MuHAT_1, MuHAT_2, w, t = None, None, None, None 
    i = 0
    while(True):
        i += 1
        MuHAT_2 = MuHAT_1
        MuMONTE_2 = MuMONTE_1
        if i == 1:
            MuHAT_1 = MuMONTE_1
            w = np.array(MuEMPIRICAL) - np.array(MuMONTE_1)
        else:
            numerator = np.dot(np.array(MuMONTE_1)-np.array(MuHAT_2),np.array(MuEMPIRICAL)-np.array(MuHAT_2))
            denominator = np.dot(np.array(MuMONTE_1)-np.array(MuHAT_2),np.array(MuMONTE_1)-np.array(MuHAT_2))
            scale = (np.array(MuMONTE_1) - np.array(MuHAT_2))
            MuHAT_1 = np.array(MuHAT_2) + scale*(numerator/denominator)
            w = np.array(MuEMPIRICAL) - np.array(MuHAT_1)
            t = norm(w,2)
        print(t)
        mdp = vi.MelodyMDP(startstates, w, finalstates, extendedstates)
        Pi_1 = vi.value_iteration(mdp)
        MuMONTE_1 = grp.Main(startstates,Pi_1,TOTALSONGSTOMONTECARLO=200)

if __name__ == '__main__':
    featurevectors = pickle.load(open('featurevectors.pkl','rb'))
    startstates = pickle.load(open('startstates.pkl','rb'))
    extendedstates = pickle.load(open('extendedstates.pkl','rb'))
    observedstates = pickle.load(open('observedstates.pkl','rb'))
    finalstates = pickle.load(open('finalstates.pkl','rb'))
    featureexpectations = pickle.load(open('monteexpectations.pkl','rb'))
    Main(featurevectors,startstates,extendedstates,observedstates,finalstates,featureexpectations)
