import numpy as  np
#from __future__ import division
try:
   import cPickle as pickle
except:
   import pickle
X,u,s,v=None,None,None,None
with open('X.pkl', 'rb') as input:
	X = pickle.load(input)	
with open('u.pkl', 'rb') as input:
	u = pickle.load(input)	
with open('s.pkl', 'rb') as input:
	s = pickle.load(input)	
	i = np.argsort(s)
	s = np.sort(s)
with open('v.pkl', 'rb') as input:
	v = pickle.load(input)
print('poop')
