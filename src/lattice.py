class StateLattice:
    def __init__(self, diagram):
        self.diagram = diagram
        self.state_to_id = {}
        self.id_to_state = {}
        self.state_count = 0
        self.edges = []

    def add_state(self, state):
        if state not in self.state_to_id:
            state_id = self.state_count
            self.state_to_id[state] = state_id
            self.id_to_state[state_id] = state
            self.state_count += 1
        return self.state_to_id[state]


    def get_state_by_id(self, state_id):
        return self.id_to_state.get(state_id)

    def get_state_id(self, state):
        return self.state_to_id.get(state)

    def build_lattice(self):
        """
        Build the state lattice for the given knot diagram.
        """
        pass

    def get_minimal_state(self):
        """
        Get the minimal state in the lattice.
        """
        pass

    def get_maximal_state(self):
        """
        Get the maximal state in the lattice.
        """
        pass