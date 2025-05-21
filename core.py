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

    def __repr__(self):
        return f"Region {self.bounding_segments}"
    
class Crossing:
    def __init__(self, segments):
        """
        segments: 4 segments of the crossing in counterclockwise order
        """
        self.segments= segments

    def __repr__(self):
        return f"Crossing {self.segments}"
    
    def __eq__(self, other):
        return isinstance(other, Crossing) and self.segments == other.segments

    # for using Crossing as a key in a dictionary
    def __hash__(self):
        return hash(self.segments) 

    def clockwise_next(self, region):
        """
        Input id of region: 
            0=region between segment 0,1, 
            1=region between segment 1 and 2,
            2=region between segment 2 and 3,
            3=region between segment 3 and 0,
        return clockwise next segment of region
        """
        return self.segments[region]
    def counterclockwise_next(self, region):
        """
        Input id of region: 
            0=region between segment 0,1, 
            1=region between segment 1 and 2,
            2=region between segment 2 and 3,
            3=region between segment 3 and 0,
        
        """
        return self.segments[(region +1) % 4]


class KnotDiagram:
    def __init__(self,pd_notation):
        """
        pd_notation: knot diagram in pd notation, for each crossing a 4-tuple
        """
        self.crossings = [Crossing(segments) for segments in pd_notation]
        self.number_of_crossings = len(pd_notation)
        self.number_of_regions = self.number_of_crossings + 2
        self.number_of_segments = 2*self.number_of_crossings


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

#    def get_region(self, crossing):
        #"""Returns the region corresponding to the marker at the given crossing."""
        #pos = self.marker_positions[crossing]
        #return crossing.adjacent_regions[pos]
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
            c0.counterclockwise_next(m0) == c1.counterclockwise_next(m1)
            and segment == c1.counterclockwise_next(m1)
        ):
            return 'cw'

        # Check for counterclockwise transposition
        if (
            c1.clockwise_next(m1) == c0.clockwise_next(m0)
            and segment == c1.clockwise_next(m1)
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
        return f"KauffmanState({{ {', '.join(f'{k}: {k.clockwise_next(v),k.counterclockwise_next(v)}' for k,v in self.marker_positions.items())} }})"

class StateLattice:
    pass