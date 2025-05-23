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
        print(state)
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
        pass

    def build_lattice(self,segment):
        """
        Build the state lattice for the given knot diagram.
        """
        minimal_state = self.get_minimal_state(segment)
        min_id = ""
        node = StateNode(minimal_state,min_id)
        queue = [node]
        self.nodes.append(node)

        while queue:
            node = queue.pop(0)
            print(node.id)
            possible_transpositions = node.state.get_all_possible_transpositions("ccw")
            for transposition in possible_transpositions:
                next_state = node.state.transpose(transposition,"ccw")
                next_id = node.id + str(transposition)
                new_node = StateNode(next_state, next_id)
                if new_node not in queue:
                    queue.append(new_node)
                    self.nodes.append(new_node)
                    self.edges.append((node.id, new_node.id, transposition))
                else:
                    self.edges.append((node.id, new_node.id, transposition))

