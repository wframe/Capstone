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
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import numpy as np
from utilz import *

def Main():
    featurevectors = pload(featurevector_pickle_string)
    print('compressing')
    X = np.array([feature.vector for feature in featurevectors])
    pca = PCA(copy=True, n_components=PCA_components, whiten=True)

    #featurecounter = Counter([feature.vector for feature in features])
    #drivel = set([i[0] for i in featurecounter.most_common(128)])

    print('fitting pca.. current time is: ' + str(datetime.datetime.now().time()))
    pca.fit(X)

    print('tranforming the states.. current time is: ' + str(datetime.datetime.now().time()))
    RX_red = pca.transform([x for x in X if x[0]==1])
    NX_red = pca.transform([x for x in X if x[0]!=1])

    pdump(pca, 'pca.pkl')

    RFeatureClustr = KMeans(n_clusters=300)
    NFeatureClustr = KMeans(n_clusters=1200)

    print('fitting rest clusters.. current time is: ' + str(datetime.datetime.now().time()))
    RFeatureClustr.fit(RX_red)
    pdump(RFeatureClustr, 'RFeatureClustr.pkl')

    print('fitting note clusters.. current time is: ' + str(datetime.datetime.now().time()))
    NFeatureClustr.fit(NX_red)

    print('finished.. current time is: ' + str(datetime.datetime.now().time()))


    pdump(NFeatureClustr, 'NFeatureClustr.pkl')

    #TranformedFeatureActionPairs(featurevectors,dim_red=pca.transform)





