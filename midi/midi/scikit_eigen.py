from sklearn.decomposition import PCA as sklearnPCA
import numpy as  np
try:
   import cPickle as pickle
except:
   import pickle
with open('X.pkl', 'rb') as input:
	X = pickle.load(input)	

sklearn_pca = sklearnPCA(n_components=32)
Y_sklearn = sklearn_pca.fit_transform(X)
vectors = set()
for vector in Y_sklearn:
	vectors.add(tuple(elem for elem in vector))
print(len(vectors))