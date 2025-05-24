from src.kstate import StateNode

class StateLattice:
    def __init__(self, diagram):
        self.diagram = diagram
        self.nodes = []
        self.state_count = 0
        self.edges = []

    def get_minimal_state(self,segment):
        """
        Get the minimal state in the lattice.
        """
        state = self.diagram.get_kstate_greedy_randomized(segment,1000)
        made_transposition = True
        while made_transposition:
            made_transposition = False
            for segment in self.diagram.segments:
                if state.is_transposable(segment, "cw"):
                    state = state.transpose(segment,"cw")
                    made_transposition = True
        return state

    def get_maximal_state(self,fixed_segment):
        """
        Get the maximal state in the lattice.
        """
        state = self.diagram.get_kstate_greedy_randomized(fixed_segment,1000)
        made_transposition = True
        while made_transposition:
            made_transposition = False
            for segment in self.diagram.segments:
                if state.is_transposable(segment, "ccw"):
                    state = state.transpose(segment,"ccw")
                    made_transposition = True
        return state

    def get_sequence_min_to_max(self,fixed_segment):
        """
        Get a sequence of transpositions from the minimal state to the maximal state.
        """
        state = self.get_minimal_state(fixed_segment)
        sequence_of_transpositions = []
        made_transposition = True
        while made_transposition:
            made_transposition = False
            for segment in self.diagram.segments:
                if state.is_transposable(segment, "ccw"):
                    state = state.transpose(segment,"ccw")
                    sequence_of_transpositions.append(segment)
                    made_transposition = True
        return sequence_of_transpositions

    def get_f_polynomial(self):
        polynomial = []
        for segment in self.diagram.segments:
            monomial = []
            seq_of_transpositions = self.get_sequence_min_to_max(segment)
            for seg in self.diagram.segments:
                number_of_occurrences = seq_of_transpositions.count(seg)
                monomial.append(number_of_occurrences)
            polynomial.append(monomial)
        return polynomial





    def create_node(self, state, previous_node_name, transposition):
        """
        Add a node to the lattice and return the node.
        """
        if previous_node_name == "":
            node = StateNode(state, str(transposition))
        else:
            node = StateNode(state, previous_node_name +","+ str(transposition))
        return node

    def build_lattice(self,segment):
        """
        Build the state lattice for the given knot diagram.
        """
        minimal_state = self.get_minimal_state(segment)
        min_name = ""
        node = StateNode(minimal_state,min_name)
        queue = [node]
        self.nodes.append(node)

        while queue:
            node = queue.pop(0)
            possible_transpositions = node.state.get_all_possible_transpositions("ccw")
            for transposition in possible_transpositions:
                next_state = node.state.transpose(transposition,"ccw")
                new_node = self.create_node(next_state, node.name, transposition)
                if new_node not in queue:
                    queue.append(new_node)
                    self.nodes.append(new_node)
                    self.edges.append((node, new_node, transposition))
                else:
                    self.edges.append((node, new_node, transposition))

    def get_depth(self):
        """
        Depth of the lattice, lattice build method has to be called first
        """
        return self.nodes[-1].get_length()

    def print_lattice(self):
        """
        Print the state lattice.
        """
        state_names = [node.name.split(",") for node in self.nodes]
        state_names.sort(key=lambda x: len(x))
        state_names = [",".join(name) for name in state_names]
        print(state_names)


