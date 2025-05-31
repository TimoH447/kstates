class TranspositionSequence:
    def __init__(self,string):
        self.string = string

    def get_length(self):
        if self.string =="":
            return 0
        else:
            return len(self.string.split(","))

    def get_transposition_count(self, segment_list):
        """
        segment_list: list as long as the number of segments in the diagram plus 1, filled with ceros., 
        Returns a list containing how often each segment was transposed.
        entry i is the number of transpositions at segment i.
        entry 0 is alwys 0, only if there are no transposition at all, then it is 1.
        """
        if self.get_length() == 0:
            segment_list[0] = 1
        else:
            transposition_list = self.string.split(",")
            for transposition in transposition_list:
                segment = int(transposition)
                segment_list[segment] += 1
        return segment_list


    def __eq__(self, value):
        if not isinstance(value, TranspositionSequence):
            return False
        transpositions_a = self.string.split(",")
        transpositions_b = value.string.split(",")
        for transposition in transpositions_a:
            if transposition not in transpositions_b:
                return False
            transpositions_b.remove(transposition)
        if 0 != len(transpositions_b):
            return False
        return True

        
class StateNode:
    def __init__(self, state, transposition_string):
        self.state = state
        self.transpositions = TranspositionSequence(transposition_string)
        self.position = None

    def get_length(self):
        return self.transpositions.get_length()

    def __eq__(self, value):
        if not isinstance(value, StateNode):
            return False
        if value.transpositions != self.transpositions:
            return False
        return True

    def __repr__(self):
        return f"({self.transpositions.string})"

        
class KauffmanState:
    def __init__(self, marker_positions):
        """
        marker_positions: dict mapping Crossing to marker position (0–3)
        """
        self.marker_positions = marker_positions  # Crossing -> int

    @classmethod
    def from_marker_positions(cls,diagram,marker_positions):
        if not cls._is_valid_state(diagram, marker_positions):
            raise ValueError("Invalid Kauffman state: each crossing must map to a single valid marker position.")

        marker_dict = {}
        for i,crossing in enumerate(diagram.crossings):
            marker_dict[crossing]=marker_positions[i]
            
        return cls(marker_dict)

    @staticmethod
    def _is_valid_state(diagram, marker_positions, segment=None):
        if len(diagram.crossings)!=len(marker_positions):
            return False
        if any([marker not in range(4) for marker in marker_positions]):
            return False
        regions = [diagram.get_region(i,marker) for i,marker in enumerate(marker_positions)]
        if len(set(regions)) != diagram.number_of_crossings:
            return False

        if segment is not None:
            # Check if the segment is part of the crossings
            if segment not in diagram.segments:
                raise ValueError(f"Segment {segment} is not part of the crossings.")
            if any([segment in region.bounding_segments for region in regions]):
                return False

        return True

    def is_transposable(self, segment, direction):
        """
        Checks whether a transposition at a segment is possible.
        Returns True if a transposition is possible in the specified direction ('cw' or 'ccw'),
        or False if no transposition is possible.
        """
        segment_crossings = [crossing for crossing in self.marker_positions if segment in crossing.segments]
        if len(segment_crossings) != 2:
            return False

        c0, c1 = segment_crossings
        m0, m1 = self.marker_positions[c0], self.marker_positions[c1]

        # Check
        if direction == 'ccw':
            return (
                c0.second_region_segment(m0) == c1.second_region_segment(m1)
                and segment == c1.second_region_segment(m1)
            )
        elif direction == 'cw':
            return (
                c1.first_region_segment(m1) == c0.first_region_segment(m0)
                and segment == c1.first_region_segment(m1)
            )
        raise ValueError("Invalid direction: must be 'cw' or 'ccw'.")
    
    def get_transposition_type(self, segment):
        """
        Checks whether a transposition at a segment is possible.
        Returns 'cw' if a clockwise transposition is possible at the segment,
        'ccw' if a counterclockwise transposition is possible,
        or None if no transposition is possible.
        """
        if self.is_transposable(segment, 'cw'):
            return 'cw'
        elif self.is_transposable(segment, 'ccw'):
            return 'ccw'
        return None
        

    def transpose(self, segment,direction="possible"):
        """ 
        Returns the transposed Kauffman state.
        Before transposing, make sure that the transposition is possible.
        """
        segment_crossings = [crossing for crossing in self.marker_positions if segment in crossing.segments]
        if len(segment_crossings) != 2:
            raise ValueError("Invalid segment: must be part of exactly two crossings.")

        c0, c1 = segment_crossings
        m0, m1 = self.marker_positions[c0], self.marker_positions[c1]
        new_positions = self.marker_positions.copy()

        if direction == 'ccw':
            new_positions[c0] = (m0 + 1) % 4
            new_positions[c1] = (m1 + 1) % 4
            return KauffmanState(new_positions)
        elif direction == 'cw':
            new_positions[c0] = (m0 - 1) % 4
            new_positions[c1] = (m1 - 1) % 4
            return KauffmanState(new_positions)
        elif direction == "possible":
            pos=self.get_transposition_type(segment)
            if pos == 'cw':
                return self.transpose(segment, 'cw')
            elif pos == 'ccw':
                return self.transpose(segment, 'ccw')
            return self
        else:
            raise ValueError("Invalid direction: must be 'cw' or 'ccw'.")

    def get_all_possible_transpositions(self,direction):
        """
        Returns a list of all possible transpositions for the current Kauffman state.
        """
        transpositions = []
        for segment in range(1, len(self.marker_positions)*2 +1):
            if self.is_transposable(segment, direction):
                transpositions.append(segment)
        return transpositions
            

    def __eq__(self, other):
        return isinstance(other, KauffmanState) and self.marker_positions == other.marker_positions

    # for using KauffmanState as a key in a dictionary
    def __hash__(self):
        return hash(frozenset(self.marker_positions.items()))

    def __repr__(self):
        return f"KauffmanState({{ {', '.join(f'{k}: {k.first_region_segment(v),k.second_region_segment(v)}' for k,v in self.marker_positions.items())} }})"

