class Region:
    def __init__(self,segments):
        """
        segments: tuple of integers (arc labels)
        """
        self.bounding_segments = segments

    def __eq__(self,other):
        if not isinstance(other, Region):
            return False
        elif set(other.bounding_segments)==set(self.bounding_segments):
            return True
        return False

    def __hash__(self):
        return hash(frozenset(self.bounding_segments))

    def __repr__(self):
        return f"Region {self.bounding_segments}"
    
class Crossing:
    def __init__(self, segments):
        """
        segments: 4 segments of the crossing in counterclockwise order
        """
        self.segments= segments

    def get_segment(self,segment_no):
        return self.segments[segment_no]

    def __repr__(self):
        return f"Crossing {self.segments}"
    
    def __eq__(self, other):
        return isinstance(other, Crossing) and self.segments == other.segments

    # for using Crossing as a key in a dictionary
    def __hash__(self):
        return hash(self.segments) 

    def first_region_segment(self, region):
        """
        Input id of region: 
            0=region between segment 0,1, 
            1=region between segment 1 and 2,
            2=region between segment 2 and 3,
            3=region between segment 3 and 0,
        return clockwise next segment of region
        """
        return self.segments[region]
    def second_region_segment(self, region):
        """
        Input id of region: 
            0=region between segment 0,1, 
            1=region between segment 1 and 2,
            2=region between segment 2 and 3,
            3=region between segment 3 and 0,
        
        """
        return self.segments[(region +1) % 4]
    def clockwise_next(self,segment):
        if not segment in self.segments:
            raise ValueError("segment not in this crossing")
        segment_index = self.segments.index(segment)
        return self.segments[(segment_index - 1) % 4]

    def counterclockwise_next(self,segment):
        if not segment in self.segments:
            raise ValueError("segment not in this crossing")
        segment_index = self.segments.index(segment)
        return self.segments[(segment_index + 1) % 4]


class KnotDiagram:
    def __init__(self,pd_notation):
        """
        pd_notation: knot diagram in pd notation, for each crossing a 4-tuple
        """
        self.crossings = [Crossing(segments) for segments in pd_notation]
        self.number_of_crossings = len(pd_notation)
        self.number_of_regions = self.number_of_crossings + 2
        self.number_of_segments = 2*self.number_of_crossings
    
    def get_region(self, crossing_id, region_id):
        """
        Reconstruct the region adjacent to a given crossing at a specific marker position.
        
        Parameters:
            crossing_id (int): Index of the starting crossing in self.crossings.
            region_id (int): Marker position (0 to 3) on that crossing.
            
        Returns:
            Region: The region bounded by segments traced from that marker.
        """
        boundary = []
        visited_segments = set()

        crossing = self.crossings[crossing_id]
        segment = crossing.segments[region_id]
        current_segment = segment
        current_crossing = crossing

        visited_segments.add(current_segment)
        boundary.append(current_segment)

        while True:

            # Step to the next segment in counterclockwise direction
            next_segment = current_crossing.counterclockwise_next(current_segment)
            if next_segment == segment:
                break  # Completed the loop
            boundary.append(next_segment)

            # Now find the next crossing that shares this segment
            for next_c in self.crossings:
                if next_c != current_crossing and next_segment in next_c.segments:
                    current_crossing = next_c
                    # determine the position of the segment in next_c to continue
                    current_segment = next_segment
                    break
            else:
                raise ValueError(f"No next crossing found for segment {next_segment}")


        return Region(tuple(boundary))

    def get_knot_description(self):
        return f"Crossings: {self.number_of_crossings}, Regions: {self.number_of_regions}, Segments: {self.number_of_segments}"

    def __repr__(self):
        knot_string="Knot:\n"
        for crossing in self.crossings:
            knot_string += str(crossing)  + "\n"
        return knot_string

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
    def _is_valid_state(diagram, marker_positions):
        if len(diagram.crossings)!=len(marker_positions):
            return False
        if any([marker not in range(4) for marker in marker_positions]):
            return False
        regions = [diagram.get_region(i,marker) for i,marker in enumerate(marker_positions)]
        if len(set(regions)) != diagram.number_of_crossings:
            return False
        return True

    def get_transposition_type(self, segment):
        """
        Checks whether a transposition at a segment is possible.
        Returns 'cw' if a clockwise transposition is possible at the segment,
        'ccw' if a counterclockwise transposition is possible,
        or None if no transposition is possible.
        """
        segment_crossings = [crossing for crossing in self.marker_positions if segment in crossing.segments]
        if len(segment_crossings) != 2:
            return None

        c0, c1 = segment_crossings
        m0, m1 = self.marker_positions[c0], self.marker_positions[c1]

        # Check for clockwise transposition
        if (
            c0.second_region_segment(m0) == c1.second_region_segment(m1)
            and segment == c1.second_region_segment(m1)
        ):
            return 'cw'

        # Check for counterclockwise transposition
        if (
            c1.first_region_segment(m1) == c0.first_region_segment(m0)
            and segment == c1.first_region_segment(m1)
        ):
            return 'ccw'

        return None

    def transpose(self, segment):
        """ 
        Returns the transposed Kauffman state if possible.
        Else returns None.
        """
        trans_type = self.get_transposition_type(segment)
        segment_crossings = [crossing for crossing in self.marker_positions if segment in crossing.segments]
        if len(segment_crossings) != 2 or trans_type is None:
            return None

        c0, c1 = segment_crossings
        m0, m1 = self.marker_positions[c0], self.marker_positions[c1]
        new_positions = self.marker_positions.copy()

        if trans_type == 'cw':
            new_positions[c0] = (m0 + 1) % 4
            new_positions[c1] = (m1 + 1) % 4
            return KauffmanState(new_positions)
        elif trans_type == 'ccw':
            new_positions[c0] = (m0 - 1) % 4
            new_positions[c1] = (m1 - 1) % 4
            return KauffmanState(new_positions)
        return None

    def __eq__(self, other):
        return isinstance(other, KauffmanState) and self.marker_positions == other.marker_positions

    # for using KauffmanState as a key in a dictionary
    def __hash__(self):
        return hash(frozenset(self.marker_positions.items()))

    def __repr__(self):
        return f"KauffmanState({{ {', '.join(f'{k}: {k.first_region_segment(v),k.second_region_segment(v)}' for k,v in self.marker_positions.items())} }})"

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