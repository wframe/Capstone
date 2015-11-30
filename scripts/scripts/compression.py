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
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import numpy as np
from utilz import *
featurevectors = pickle.load(open(outputmodelname+featurevectorlist_pickle_string,'rb'))
print('compressing to [1500 X 12]\n')
X = np.array([feature.vector for feature in featurevectors])
pca = PCA(copy=True, n_components=12, whiten=True)

#featurecounter = Counter([feature.vector for feature in features])
#drivel = set([i[0] for i in featurecounter.most_common(128)])

print('fitting pca.. current time is: ' + str(datetime.datetime.now().time()))
pca.fit(X)

print('tranforming the states.. current time is: ' + str(datetime.datetime.now().time()))
RX_red = pca.transform([x for x in X if x[0]==1])
NX_red = pca.transform([x for x in X if x[0]!=1])

with open(outputmodelname+'pca12.pkl', 'wb') as output:
    pickle.dump(pca, output, -1)

RFeatureClustr = KMeans(n_clusters=300)
NFeatureClustr = KMeans(n_clusters=1200)

print('fitting rest clusters.. current time is: ' + str(datetime.datetime.now().time()))
RFeatureClustr.fit(RX_red)
with open(outputmodelname+'RFeatureClustr300.pkl', 'wb') as output:
    pickle.dump(RFeatureClustr, output, -1)

print('fitting note clusters.. current time is: ' + str(datetime.datetime.now().time()))
NFeatureClustr.fit(NX_red)

print('finished.. current time is: ' + str(datetime.datetime.now().time()))


with open(outputmodelname+'NFeatureClustr1200.pkl', 'wb') as output:
    pickle.dump(NFeatureClustr, output, -1)

#TranformedFeatureActionPairs(featurevectors,dim_red=pca.transform)





