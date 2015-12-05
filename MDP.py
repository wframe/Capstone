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

