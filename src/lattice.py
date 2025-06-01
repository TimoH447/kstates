from src.kstate import StateNode
from src.kstate import TranspositionSequence

class StateLattice:
    """
    Class representing the state lattice of a knot diagram.
    
    Possible methods:
    - get_minimal_state: Get the minimal state in the lattice.
    - get_maximal_state: Get the maximal state in the lattice.
    - get_sequence_min_to_max: Get a sequence of transpositions from the minimal state to the maximal state.
    - get_f_polynomial: Get the f-polynomial of the lattice.
    - get_f_polynomial_latex: Get the f-polynomial of the lattice in LaTeX format.
    - get_alexander_polynomial: Get the Alexander polynomial of the lattice.
    - get_alexander_polynomial_latex: Get the Alexander polynomial of the lattice in LaTeX format.
    """
    def __init__(self, diagram, fixed_segment):
        self.diagram = diagram
        self.fixed_segment = fixed_segment
        self.nodes = []
        self.state_count = 0
        self.edges = []
        self._build_lattice()

    def _create_node(self, state, previous_node_transpositions, transposition):
        """
        Add a node to the lattice and return the node.
        """
        if previous_node_transpositions == "":
            node = StateNode(state, str(transposition))
        else:
            node = StateNode(state, previous_node_transpositions +","+ str(transposition))
        return node

    def _build_lattice(self):
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
                new_node = self._create_node(next_state, node.transpositions.string, transposition)
                if new_node not in queue:
                    queue.append(new_node)
                    self.nodes.append(new_node)
                    self.edges.append((node, new_node, transposition))
                else:
                    self.edges.append((node, new_node, transposition))
    
    def get_node_by_transpositions(self, transpositions_string):
        """
        Get a node by its name.
        """
        for node in self.nodes:
            if node.transpositions == TranspositionSequence(transpositions_string):
                return node
        return None

    def get_depth(self):
        """
        Depth of the lattice, lattice build method has to be called first
        """
        return self.nodes[-1].get_length()

    def get_nodes_in_layer(self, layer_number):
        """
        Get all nodes in a specific layer of the lattice, i.e. states which are *layer_number* times transposed starting from the minimal state.
        """
        return [node for node in self.nodes if node.get_length() == layer_number]

    def get_minimal_state(self):
        """
        Get the minimal state in the lattice.
        If the lattice is already built, return the first node's state which is the minimal state.
        Otherwise, computes the minimal state by transposing clockwise until no more transpositions are possible 
        from a random starting state.

        Returns the state as a KauffmanState object.
        """
        # If the lattice is already built, return the first node's state.
        if len(self.nodes) > 0:
            return self.nodes[0].state

        # Otherwise, compute the minimal state by transposing clockwise.
        state = self.diagram.get_kstate_greedy_randomized(self.fixed_segment,1000)
        made_transposition = True
        while made_transposition:
            made_transposition = False
            for segment in self.diagram.segments:
                if state.is_transposable(segment, "cw"):
                    state = state.transpose(segment,"cw")
                    made_transposition = True
        return state
    
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

    def get_f_pol_specialization(self):
        """
        Get the specialization of the f-polynomial which is equal to the Alexander polynomial.
        """
        polynomial = self.get_f_polynomial()
        specialized_polynomial = []
        for summand in polynomial:
            if summand[0] == 1:
                specialized_polynomial.append([1,0])
            else:
                term = []
                t_power = 0
                for i, count in enumerate(summand):
                    if self.diagram.is_segment_from_under_to_over(i):
                        t_power += count
                    elif self.diagram.is_segment_from_over_to_under(i):
                        t_power -= count
                sign = sum(summand) % 2
                if sign == 0:
                    term = [1, t_power]
                else: 
                    term = [-1, t_power]
                specialized_polynomial.append(term)
        return specialized_polynomial

    def get_alexander_polynomial(self):
        """
        Get the Alexander polynomial of the lattice.
        """
        specialized_polynomial = self.get_f_pol_specialization()
        alexander_polynomial = []
        for summand in specialized_polynomial:
            if any(term[1] == summand[1] for term in alexander_polynomial):
                for term in alexander_polynomial:
                    if term[1] == summand[1]:
                        term[0] += summand[0]
            else:
                alexander_polynomial.append(summand)
        return alexander_polynomial
    
    def get_alexander_polynomial_latex(self):
        """
        Get the Alexander polynomial of the lattice in LaTeX format.
        """
        alexander_polynomial = self.get_alexander_polynomial()
        alexander_polynomial_latex = ""
        for term in alexander_polynomial:
            if term[0] == 0:
                continue
            sign = "+" if term[0] > 0 else "-"
            coefficient = abs(term[0])
            if term[1] == 0:
                alexander_polynomial_latex += f" {sign} {coefficient}"
            else:
                if coefficient == 1:
                    coefficient = ""
                elif coefficient == -1:
                    coefficient = ""
                if term[1] == 1:
                    alexander_polynomial_latex += f" {sign} {coefficient}t"
                else:
                    alexander_polynomial_latex += f" {sign} {coefficient}t^{{{term[1]}}}"
        alexander_polynomial_latex = alexander_polynomial_latex.strip()
        if alexander_polynomial_latex.startswith("+"):
            alexander_polynomial_latex = alexander_polynomial_latex[1:].strip()
        return alexander_polynomial_latex


