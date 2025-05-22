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
