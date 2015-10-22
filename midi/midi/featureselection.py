from sklearn.feature_selection import VarianceThreshold
from sklearn.decomposition import PCA as sklearnPCA
import numpy as  np
try:
   import cPickle as pickle
except:
   import pickle
incidence_thresh = .80
with open('X.pkl', 'rb') as input:
	X = pickle.load(input)	
	sel = VarianceThreshold(threshold=(incidence_thresh * (1 - incidence_thresh)))
	X_R3dUc3DiM = sel.fit_transform(X)
	print(X_R3dUc3DiM.shape)
vectors = set()
for vector in X_R3dUc3DiM:
	vectors.add(tuple(bit for bit in vector))
feature_expectations = np.mean(X_R3dUc3DiM, axis=0)
print('feature_expectations:')
print(feature_expectations)
print("len(vectors):")
print(len(vectors))