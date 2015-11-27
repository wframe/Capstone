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

def IntegerizeArray(arr):
    return np.array(np.around(arr,decimals=0),dtype='int32')