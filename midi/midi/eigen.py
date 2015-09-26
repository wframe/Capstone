import numpy as  np
try:
   import cPickle as pickle
except:
   import pickle
with open('X.pkl', 'rb') as input:
	X = pickle.load(input)	

mean_vec = np.mean(X, axis=0)
cov_mat = (X - mean_vec).T.dot((X - mean_vec)) / (X.shape[0]-1)
print('Covariance matrix \n%s' %cov_mat)
print('NumPy covariance matrix: \n%s' %np.cov(X.T))

cov_mat = np.cov(X.T)
eig_vals, eig_vecs = np.linalg.eig(cov_mat)

print('Eigenvectors \n%s' %eig_vecs)
print('\nEigenvalues \n%s' %eig_vals)

#for ev in eig_vecs:
#    np.testing.assert_array_almost_equal(1.0, np.linalg.norm(ev))
#print('Everything ok!')

# Make a list of (eigenvalue, eigenvector) tuples
eig_pairs = [(np.abs(eig_vals[idx]), eig_vecs[:,idx], idx) for idx in range(len(eig_vals))]

# Sort the (eigenvalue, eigenvector) tuples from high to low
eig_pairs.sort()
eig_pairs.reverse()

# Visually confirm that the list is correctly sorted by decreasing eigenvalues
print('Eigenvalues in descending order:')
for i in eig_pairs:
    print("value: "+ str(i[0]) + " index: " + str(i[2]))