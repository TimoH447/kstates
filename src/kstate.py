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

