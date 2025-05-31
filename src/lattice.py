from src.kstate import StateNode
from src.kstate import TranspositionSequence

# TODO initialize state latice with fixed segment
class StateLattice:
    def __init__(self, diagram, fixed_segment):
        self.diagram = diagram
        self.fixed_segment = fixed_segment
        self.nodes = []
        self.state_count = 0
        self.edges = []

    def get_minimal_state(self):
        """
        Get the minimal state in the lattice.
        """
        state = self.diagram.get_kstate_greedy_randomized(self.fixed_segment,1000)
        made_transposition = True
        while made_transposition:
            made_transposition = False
            for segment in self.diagram.segments:
                if state.is_transposable(segment, "cw"):
                    state = state.transpose(segment,"cw")
                    made_transposition = True
        return state

    def get_node_by_transpositions(self, transpositions_string):
        """
        Get a node by its name.
        """
        for node in self.nodes:
            if node.transpositions == TranspositionSequence(transpositions_string):
                return node
        return None

    def get_maximal_state(self):
        """
        Get the maximal state in the lattice.
        """
        state = self.diagram.get_kstate_greedy_randomized(self.fixed_segment,1000)
        made_transposition = True
        while made_transposition:
            made_transposition = False
            for segment in self.diagram.segments:
                if state.is_transposable(segment, "ccw"):
                    state = state.transpose(segment,"ccw")
                    made_transposition = True
        return state

    def get_sequence_min_to_max(self):
        """
        Get a sequence of transpositions from the minimal state to the maximal state.
        """
        state = self.get_minimal_state()
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
        for node in self.nodes:
            term =[0] + [0]*self.diagram.number_of_segments
            polynomial.append(node.transpositions.get_transposition_count(term))
        return polynomial 

    def get_f_polynomial_latex(self):
        """
        Get the f-polynomial of the lattice in LaTeX format.
        """
        polynomial = self.get_f_polynomial()
        f_polynomial_latex = "1"
        for summand in polynomial:
            term_latex_string = ""
            if summand[0]==0:
                for i, count in enumerate(summand):
                    if count > 1:
                        term_latex_string += f"y_{{{i}}}^{count}"
                    elif count == 1:
                        term_latex_string += f"y_{{{i}}}"
                f_polynomial_latex += " + " + term_latex_string
        return f_polynomial_latex

        for i, count in enumerate(polynomial):
            if count > 0:
                term = f"{count}x_{i}"
                latex_terms.append(term)
        return " + ".join(latex_terms) if latex_terms else "0"
                

    def create_node(self, state, previous_node_transpositions, transposition):
        """
        Add a node to the lattice and return the node.
        """
        if previous_node_transpositions == "":
            node = StateNode(state, str(transposition))
        else:
            node = StateNode(state, previous_node_transpositions +","+ str(transposition))
        return node

    def build_lattice(self):
        """
        Build the state lattice for the given knot diagram.
        """
        minimal_state = self.get_minimal_state()
        min_name = ""
        node = StateNode(minimal_state,min_name)
        queue = [node]
        self.nodes.append(node)

        while queue:
            node = queue.pop(0)
            possible_transpositions = node.state.get_all_possible_transpositions("ccw")
            for transposition in possible_transpositions:
                next_state = node.state.transpose(transposition,"ccw")
                new_node = self.create_node(next_state, node.transpositions.string, transposition)
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

    def get_nodes_in_layer(self, layer_number):
        """
        Get all nodes in a specific layer of the lattice.
        """
        return [node for node in self.nodes if node.get_length() == layer_number]

    def print_lattice(self):
        """
        Print the state lattice.
        """
        state_names = [node.transpositions.string.split(",") for node in self.nodes]
        state_names.sort(key=lambda x: len(x))
        state_names = [",".join(name) for name in state_names]
        print(state_names)


