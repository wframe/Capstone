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
import utilz
featurevectors = pickle.load(open('featurevectors.pkl','rb'))

X = np.array([feature.vector for feature in featurevectors])
pca = PCA(copy=True, n_components=20, whiten=True)
X_red = pca.fit_transform(X)

print('x_red shape: \n' + str(np.array(X_red).shape))
print('x shape: \n' + str(np.array(X).shape))
print('x sum: \n' + str(np.sum(X)))
print('x avg: \n' + str(np.average(X)))
trans = np.array(pca.transform(X[0]))[0]
print('x[0] red: \n' + str(trans))
print('x[0]: \n')
printOnes(np.array(X[0]))
revert = pca.inverse_transform(trans)
revert = utilz.IntegerizeArray(revert)
print('x[0] reverted: \n')
printOnes(revert)

FeatureClustr = KMeans(n_clusters=2500)
FeatureClustr.fit(X)

TransformedFeatures = dict()
for feat in featurevectors:
    trans_feat = FeatureClustr.transform(pca.transform(feat.vector))
    if trans_feat not in TransformedFeatures:
        TransformedFeatures[trans_feat] = Counter()
    TransformedFeatures[trans_feat][feat.actiongenerated] += 1
with open('TransformedFeatures.pkl', 'wb') as output:
    pickle.dump(TransformedFeatures, output, -1)




