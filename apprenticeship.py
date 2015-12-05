from utilz import *
from MelodyMDP import MelodyMDP
import generate_random_policy as grp

def Main(featurevectors,startstates,pricedsums,tfam,songs,pca,cmodels,espilon=.001):
    MuEMPIRICAL = empiricalestimate(songs,pca)
    MuMONTE_1, MuMONTE_2, MuHAT_1, MuHAT_2, w, t = pricedsums, None,None,None,None,None
    while(True):
        dot = np.dot
        MuHAT_2 = MuHAT_1
        MuMONTE_2 = MuMONTE_1
        if w is None:
            MuHAT_1 = MuMONTE_1
            w = MuEMPIRICAL - MuMONTE_1
        else:
            numerator = dot(MuMONTE_1-MuHAT_2,MuEMPIRICAL-MuHAT_2)
            denominator = dot(MuMONTE_1-MuHAT_2,MuMONTE_1-MuHAT_2)
            MuHAT_1 = MuHAT_2 + (MuMONTE_1 - MuHAT_2)*(numerator/denominator)
            w = MuEMPIRICAL - MuHAT_1
            t = norm(w,2)
            if t <= epsilon:
                print('CONVERGED!!!!!!')
        mdp = MelodyMDP(startstates, w, tfam)
        Pi_1 = value_iteration(mdp, tfam,pca,cmodels)
        MuMONTE_1 = grp.Main(startstates,features,Pi_1,pca, cmodels, TOTALSONGSTOMONTECARLO=200)
        
if __name__ == '__main__':
    songs, featurevectors, startstates = getRawPickles()
    pricedsums = pload(pricedsums_pickle_string)
    tfam,pca,cmodels = getDerivedPickles()
    Main(featurevectors,startstates,pricedsums,tfam,songs,pca,cmodels)
