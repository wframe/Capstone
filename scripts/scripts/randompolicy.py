#returns random deterministic policy and feature expectation for
#given start states, feature vectors and goal states
featurevectors,observedstates,startstates,finalstates,X=None,None,None,None,None
with open('featurevectors.pkl', 'rb') as input:
	featurevectors = pickle.load(input)
with open('observedstates.pkl', 'rb') as input:
	observedstates = pickle.load(input)
with open('startstates.pkl', 'rb') as input:
	startstates = pickle.load(input)
with open('finalstates.pkl', 'rb') as input:
	finalstates = pickle.load(input)
with open('X.pkl', 'rb') as input:
	X = pickle.load(input)

if __name__ == "__main__": 
	rpolicy

