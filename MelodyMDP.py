from MDP import MDP
class MelodyMDP(MDP):

    def __init__(self, startstates, rewards,  tfam, gamma = 0.9):
        self.startstates = startstates
        self.gamma = gamma
        self.rewards = rewards
        self.tfam = tfam
        self.frontier = []
        self.encounteredstates = dict()

    def R(self, feature):
        return np.dot(self.rewards.reshape(pca.n_components).T, feature)

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

    def evaluteFrontier(self,parent,utilities,tfam,pca,cmodels):
        from SongData import SongData, findevent
        from generate_random_policy import updateNodeAndFeature
        terminus = None
        candidates = []
        prospects = copy.deepcopy(parent.transformedprospects)
        for action in prospects.keys():
            candidate = copy.deepcopy(parent)
            candidate.generatedbyaction = action
            event = findevent(action, candidate.context.songPitchMap.getPitchMax(SongData.REST))            
            updateNodeAndFeature(candidate,event,tfam,pca,cmodels)
            if action == SongData.END:
                terminus = candidate
            elif candidate.transformedfeature not in utilities[candidate.feature.vector[0]]:
                utilities[candidate.feature.vector[0]][candidate.transformedfeature] = 0
            candidates.append(candidate)        
        
        reward = max([utilities[c.feature.vector[0]][c.transformedfeature] for c in candidates if c.feature != SongData.END])
        maxlist = [(c,prospects[c.generatedbyaction]) for c in candidates if c.feature!=SongData.END and utilities[c.feature.vector[0]][c.transformedfeature]==reward]
        #if tie for best action, draw based on corpus incidence, otherwise list will only have one element anywayz
        drawbest= lambda s : random.choice(sum(([v]*wt for v,wt in s),[]))
        argcand = drawbest(maxlist)
        if terminus is not None:
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