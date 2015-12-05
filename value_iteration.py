from utilz import *
from MelodyMDP import MelodyMDP

def value_iteration(mdp, tfam,pca,cmodels,epsilon = 0.001, MIN_INNER_ITERATIONS = 10000):
    """Solving an MDP by value iteration. [Fig. 17.4]"""
    from generate_random_policy import updateNodeAndFeature, initializetrajectory
    from SongData import SongData
    
    new_utilities = dict()
    new_utilities[0]= dict() 
    new_utilities[1] = dict()

    R, gamma = mdp.R,  mdp.gamma
    
    s_events = initializetrajectory(mdp.startstates)

    while True:
        print 'OUTER LOOP OF VALUE ITERATION--'
        old_utilities = copy.deepcopy(new_utilities)
        start, event, parent = s_events
        updateNodeAndFeature(parent,event,tfam,pca,cmodels) 
        delta = 0
        iteration = 0
        #walk the space, updating each state by its most lucrative neighbor and following same trajectory
        while parent.generatedbyaction != SongData.END:
            iteration+=1
            maximum_value_action, child = mdp.evaluteFrontier(parent,old_utilities,tfam,pca,cmodels)
            originalfeature=parent.feature.vector       
            parity = originalfeature[0]
            tfeat = tuple(pca.transform(originalfeature).reshape(pca.n_components))
            featurecluster = np.asscalar(clustermodelheuristic(originalfeature,cmodels).predict(tfeat))
            new_utilities[parity][featurecluster] = R(tfeat) + gamma * maximum_value_action
            if featurecluster not in old_utilities[parity]:
                old_utilities[parity][featurecluster] = 0 
            delta = max(delta, abs(new_utilities[parity][featurecluster] - old_utilities[parity][featurecluster] ))
            parent = child
        print('iteration #:' + str(iteration))
        print '\tmax delta: ' + str(delta)
        if delta < epsilon * (1 - gamma) / gamma:
            return old_utilities