from random import randint

from src.kstate import KauffmanState
from src.lattice import StateLattice

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

    def get_sign(self):
        a = self.segments[1]
        b = self.segments[3]
        if abs(a-b)==1:
            if a>b:
                return 1
            else:
                return -1
        else:
            if a>b:
                return -1
            else:
                return 1

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
    """
    Class representing a knot diagram.
    It is initialized with a knot diagram in pd notation.
    
    possible methods:
    """

    def __init__(self,pd_notation):
        """
        pd_notation: knot diagram in pd notation, for each crossing a 4-tuple
        """
        self.pd_notation = pd_notation
        self.crossings = [Crossing(segments) for segments in pd_notation]
        self.number_of_crossings = len(pd_notation)
        self.number_of_regions = self.number_of_crossings + 2
        self.number_of_segments = 2*self.number_of_crossings
        self.segments = [i+1 for i in range(self.number_of_segments)]

    def __repr__(self):
        knot_string="Knot:\n"
        for crossing in self.crossings:
            knot_string += str(crossing)  + "\n"
        return knot_string

    def get_pd_notation(self):
        return self.pd_notation
    
    def get_crossings_containing_segment(self,segment):
        crossing_containg_the_segment = []
        for crossing in self.crossings:
            if segment in crossing.segments:
                crossing_containg_the_segment.append(crossing)
        return crossing_containg_the_segment

    def get_twist_number(self):
        twist = 0
        for crossing in self.crossings:
            twist += crossing.get_sign()
        return twist


    def get_quiver_notation_qpa(self):
        number_of_vertices = str(self.number_of_crossings*2)
        arrows = []
        for crossing in self.pd_notation:
            for i in range(4):
                arrows.append([crossing[i],crossing[-1]])
        arrows = str(arrows)

        return f"Quiver( {number_of_vertices}, {arrows})"
    
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

    def get_kstate_greedy(self,segment):
        """
        Get a Kauffman state of the knot diagram with no markers in the regions adjacent to the segment
        This algorithm will choose the first possible marker position for each crossing. 
        As consequence, it may not find a solution for all crossings.
        """
        # list of marker positions
        marker_positions = []
        # marked regions
        marked_regions = []
        for crossing_id,crossing in enumerate(self.crossings):
            for region_id in range(4):
                region = self.get_region(crossing_id,region_id)
                if segment in region.bounding_segments:
                    continue
                if region in marked_regions:
                    continue
                marked_regions.append(region)
                marker_positions.append(region_id)
                break
        
        if len(marker_positions) != self.number_of_crossings:
            raise ValueError("Not all crossings have a marker position")
        return KauffmanState.from_marker_positions(self, marker_positions)

    def get_kstate_greedy_randomized(self, segment,retries=100):
        """
        Get a Kauffman state of the knot diagram with no markers in the regions adjacent to the segment
        This algorithm will choose the first possible marker position for each crossing. 
        As consequence, it may not find a solution for all crossings.
        """
        # list of marker positions
        marker_positions = []
        # marked regions
        marked_regions = []
        while retries > 0 and len(marker_positions) != self.number_of_crossings:
            retries -= 1
            marker_positions = []
            marked_regions = []
            for crossing_id,crossing in enumerate(self.crossings):
                randomized_start_region = randint(0,3)
                for i in range(randomized_start_region,randomized_start_region+4):
                    region_id = i % 4
                    region = self.get_region(crossing_id,region_id)
                    if segment in region.bounding_segments:
                        continue
                    if region in marked_regions:
                        continue
                    marked_regions.append(region)
                    marker_positions.append(region_id)
                    break
        if len(marker_positions) != self.number_of_crossings:
            raise ValueError("Not all crossings have a marker position")
        return KauffmanState.from_marker_positions(self, marker_positions)

    def get_kstate_bruteforce(self,segment):
        """
        Get a Kauffman state of the knot diagram with no markers in the regions adjacent to the segment
        """
        # list of marker positions
        marker_positions = [0]*self.number_of_crossings
        while not KauffmanState._is_valid_state(self,marker_positions, segment):
            # increment marker positions
            for i in range(self.number_of_crossings):
                x = (marker_positions[i]+1)%4
                if x != 0:
                    break
        return KauffmanState.from_marker_positions(self, marker_positions)
                    
    def get_knot_description(self):
        return f"Crossings: {self.number_of_crossings}, Regions: {self.number_of_regions}, Segments: {self.number_of_segments}"

    def is_segment_from_under_to_over(self, segment):
        """
        This method returns True if the segment goes from an under-crossing to an over-crossing."""
        segment_positions = [crossing.segments.index(segment) for crossing in self.crossings if segment in crossing.segments]
        if not 2 in segment_positions:
            return False
        segment_positions.remove(2)
        if segment_positions[0] == 1 or segment_positions[0] == 3:
            return True
        return False

    def is_segment_from_over_to_under(self, segment):
        """
        This method returns True if the segment goes from an over-crossing to an under-crossing."""
        segment_positions = [crossing.segments.index(segment) for crossing in self.crossings if segment in crossing.segments]
        if not 0 in segment_positions:
            return False
        segment_positions.remove(0)
        if segment_positions[0] == 1 or segment_positions[0] == 3:
            return True
        return False

    def get_alexander_specialization(self):
        """
        returns a list for each variable in the f polynom, i.e. number of segments many laurent polynom
        that can be later inserted in the f polynom, 
        e.g. if the f polynom has 4 variables:
        [ [[1,2]], [[1,0]], [[1,0]], [[-1,0],[1,1]] ] = (t^2,1,1,-1+t)
        """
        specialization = []
        for segment in self.segments:
            if self.is_segment_from_under_to_over(segment):
                specialization.append([[-1,1]])
            elif self.is_segment_from_over_to_under(segment):
                specialization.append([[-1,-1]])
            else:
                specialization.append([[1,0]])
        return specialization

    def get_lattice(self,segment):
        """
        returns a StateLattice object
        """
        return StateLattice(self,segment)

    def get_alexander_polynom(self):
        """
        returns a LaurentPolynom object
        """
        lattice = self.get_lattice(1)
        f_pol = lattice.get_f_polynomial()
        specialization = self.get_alexander_specialization()
        return f_pol.specialize_to_laurent(specialization)

    
    
        


    
