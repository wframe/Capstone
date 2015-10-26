import numpy as  np
#from __future__ import division
try:
   import cPickle as pickle
except:
   import pickle
with open('X.pkl', 'rb') as input:
	X = pickle.load(input)	
	print(str(X.shape))
	u,s,v = np.linalg.svd(X, full_matrices = False)
	with open('u.pkl', 'wb') as output:
		pickle.dump(u, output, -1)
	with open('s.pkl', 'wb') as output:
		pickle.dump(s, output, -1)
	with open('v.pkl', 'wb') as output:
		pickle.dump(v, output, -1)