
from utilz import *
class MDP:
    """A Markov Decision Process, defined by an initial state, transition model,
    and reward function. We also keep track of a gamma value, for use by
    algorithms. The transition model is represented somewhat differently from
    the text.  Instead of P(s' | s, a) being a probability number for each
    state/state/action triplet, we instead have T(s, a) return a list of (p, s')
    pairs.  We also keep track of the possible states, terminal states, and
    actions for each state. [page 646]"""

    def __init__(self, init, actlist, terminals, gamma = 0.9):
        update(self, init=init, actlist=actlist, terminals=terminals, gamma=gamma, states=set(), reward={})

    def R(self, feature):
        """Return a numeric reward for this state."""
        return self.reward[state]

    def T(self, state, action):
        """Transition model.  From a state and an action, return a list
        of (probability, result-state) pairs."""
        abstract

    def actions(self, state):
        """Set of actions that can be performed in this state.  By default, a
        fixed list of actions, except for terminal states. Override this
        method if you need to specialize by state."""
        if state in self.terminals:
            return [None]
        else:
            return self.actlist


class MelodyMDP(MDP):

    def __init__(self, startstates, rewards,  tfam, gamma = 0.9):
        self.startstates = startstates
        self.gamma = gamma
        self.rewards = rewards
        self.tfam = tfam
        self.frontier = []
        self.encounteredstates = dict()

    def R(self, feature):
        return np.dot(self.rewards, feature)

    def T(self, feature, act):
        encounteredstates = self.encounteredstates
        if act not in encounteredstates[feature]:
            return None
        childfeatures = encounteredstates[feature][act]
        total = sum(childfeatures.values())
        #print('childfeatures: '+str(childfeatures))
        r = [ ((childfeatures[f] / float(total)), f) for f in childfeatures ]
        #print('\t returning r: '+str(r))
        return r

    def spawn(self, node):
        children = []
        encountered = node.feature in self.encounteredstates
        if not encountered:
            self.encounteredstates[node.feature] = dict()
        encountered_children = self.encounteredstates[node.feature]
        for action in node.prospects.keys():
            if action != SongData.END:
                if action not in encountered_children:
                    encountered_children[action] = Counter()
                newevent = findevent(action, node.context.songPitchMap.getPitchMax(SongData.REST))
                context = copy.deepcopy(node.context)
                context.update(newevent)
                candidate = Node(context, None, node, None, None)
                candidate.feature = context.feature.vector
                if candidate.feature in self.tfam:
                    encountered_children[action][candidate.feature] += 1
                    if not encountered or candidate.feature not in encountered_children[action]:
                        candidate.prospects = copy.deepcopy(self.tfam[candidate.feature])
                        candidate.generatedbyaction = action
                        children.append(candidate)

        self.frontier += children
        return children

    def evaluteFrontier(self,node,tfam,pca,cmodels):
        from SongData import SongData, findevent
        from GenerateRandomPolicy import updateNodeAndFeature
        terminus = None
        candidates = []
        prospects =copy.deepcopy(node.transformedprospects)
        for action in prospects.keys():
            candidate = copy.deepcopy(node)
            candidate.generatedbyaction = action
            if action != SongData.END:
                event = findevent(action, candidate.context.songPitchMap.getPitchMax(SongData.REST))            
                updateNodeAndFeature(candidate,event,tfam,pca,cmodels)
            else:
                terminus = candidate
            candidates.append(candidate)        
        candidaterewards = [self.R(pca.transform(feature.vector)) for c in candidates]
        maxindex = np.argmax(candidaterewards)
        reward = candidaterewards[maxindex]
        argcand = candidates[maxindex]
        if terminus != None:
            total_prospects = sum([prospects[pro] for pro in prospects])
            if np.random.uniform(0,1) < float(prospects[SongData.END])/total_prospects:
                reward, argcand = 0, terminus
        return reward, argcand
    #def actions(self, feature):
    #    if state in self.terminals:
    #        return [None]
    #    else:
    #        total = sum([ tfam[state.feature][action] for action in tfam[state.feature].keys() ])
    #        return [ [float(count) / total, nextstate(state, action)] for action in tfam[state.feature].keys() ]

def value_iteration(mdp, tfam,pca,cmodels,epsilon = 0.001, MAXINNERITERATIONS = 100000):
    from GenerateRandomPolicy import updateNodeAndFeature, initializetrajectory
    from SongData import SongData
    """Solving an MDP by value iteration. [Fig. 17.4]"""
    new_utilities = dict()
    new_utilities[0]= dict() 
    new_utilities[1] = dict()

    R, gamma = mdp.R,  mdp.gamma
    start, event, parent = initializetrajectory(mdp.startstates)
    updateNodeAndFeature(parent,event,tfam,pca,cmodels) 
    while True:
        print 'OUTER LOOP OF VALUE ITERATION--'
        old_utilities = copy.deepcopy(new_utilities)
        delta = 0
        while parent.generatedbyaction != SongData.END:
            maximum_value_action, child = mdp.evaluteFrontier(parent,tfam,pca,cmodels)       
            parity = parent.feature.vector[0]
            tfeat = parent.transformedfeature
            new_utilities[parity][parent.transformedfeature] = R(tfeat) + gamma * maximum_value_action
            delta = max(delta, abs(new_utilities[parity][tfeat] - old_utilities[parity][tfeat] ))
            parent = child
        if delta < epsilon * (1 - gamma) / gamma:
             return old_utilities

        print '\tmax delta: ' + str(delta)


def best_policy(mdp, U):
    """Given an MDP and a utility function U, determine the best policy,
    as a mapping from state to action. (Equation 17.4)"""
    pi = {}
    for s in mdp.states:
        pi[s] = argmax(mdp.actions(s), lambda a: expected_utility(a, s, U, mdp))

    return pi


def expected_utility(a, s, U, mdp):
    """The expected utility of doing a in state s, according to the MDP and U."""
    return sum([ p * U[s1] for p, s1 in mdp.T(s, a) ])

def ApprenticeshipTest(featurevectors,startstates,pricedsums,tfam,songs,pca,cmodels,espilon=.001):
    MuEMPIRICAL = empiricalestimate(songs,pca)
    MuMONTE_1, MuMONTE_2 = pricedsums, None
    MuHAT_1, MuHAT_2, w, t = None, None, None, None 
    i = 0
    while(True):
        i += 1
        MuHAT_2 = MuHAT_1
        MuMONTE_2 = MuMONTE_1
        if i == 1:
            MuHAT_1 = MuMONTE_1
            w = np.array(MuEMPIRICAL) - np.array(MuMONTE_1)
        else:
            numerator = np.dot(np.array(MuMONTE_1)-np.array(MuHAT_2),np.array(MuEMPIRICAL)-np.array(MuHAT_2))
            denominator = np.dot(np.array(MuMONTE_1)-np.array(MuHAT_2),np.array(MuMONTE_1)-np.array(MuHAT_2))
            scale = (np.array(MuMONTE_1) - np.array(MuHAT_2))
            MuHAT_1 = np.array(MuHAT_2) + scale*(numerator/denominator)
            w = np.array(MuEMPIRICAL) - np.array(MuHAT_1)
            t = norm(w,2)
        mdp = MelodyMDP(startstates, w, tfam)
        Pi_1 = value_iteration(mdp, tfam,pca,cmodels)
        MuMONTE_1 = grp.Main(startstates,Pi_1,TOTALSONGSTOMONTECARLO=200)
if __name__ == '__main__':
    featurevectors = pickle.load(open('featurevectors.pkl','rb'))
    startstates = pickle.load(open('startstates.pkl','rb'))
    extendedstates = pickle.load(open('extendedstates.pkl','rb'))
    observedstates = pickle.load(open('observedstates.pkl','rb'))
    finalstates = pickle.load(open('finalstates.pkl','rb'))
    songs = pickle.load(open('songs.pkl','rb'))
    pricedsums = pickle.load(open('pricedsums.pkl','rb'))

    tfam= pickle.load(open('tfam.pkl','rb'))
    pca = pickle.load(open(pca_pickle_string,'rb'))
    clusters = [pickle.load(open(ncluster_pickle_string,'rb')),pickle.load(open(rcluster_pickle_string,'rb'))]
    ApprenticeshipTest(featurevectors,startstates,pricedsums,tfam,songs,pca,clusters)