import math

def get_binary(i,n):
        binary = [0 for j in range(n)]
        if i==0:
            return binary
        k = n-1
        while i!=0:
            if i>=2**k:
                i=i-2**k
                binary[k] = 1
            k -= 1
        return binary

def binary_to_label(binary):
    if binary == 0:
        return "A"
    elif binary==1:
        return "B"
    raise ValueError("Label has to be 0 or 1")

class JonesState:
    def __init__(self,labels):
        self.labels = labels

    @classmethod
    def from_integer(cls,number_of_crossings,state_number):
        """
        For a knot diagram with n crossings there are 2^n states,
        this method turns integer (0 to 2^n-1) into binary and uses this for the labels"""
        binary = get_binary(state_number, number_of_crossings)
        state_labels = list(map(binary_to_label,binary)) # use same labelling as Kauffman ("A" or "B")
        return cls(state_labels)


    def get_number_of_A_labels(self):
        number_of_A_labels = 0
        for label in self.labels:
            if label == "A":
                number_of_A_labels += 1
        return number_of_A_labels

    def get_number_of_B_labels(self):
        number_of_B_labels = 0
        for label in self.labels:
            if label == "B":
                number_of_B_labels +=1
        return number_of_B_labels

    def get_split(self,crossing):
        segments = crossing.segments
        if self.labels[crossing.id] == "A":
            return [list(segments[:2]),list(segments[2:])]
        elif self.labels[crossing.id] == "B":
            return [list(segments[1:3]),[segments[3],segments[0]]]
        raise ValueError("Jones Crossing got an unvalid label.")

    def get_next_segment(self,crossing,segment):
        split = self.get_split(crossing)
        if segment in split[0]:
            split[0].remove(segment)
            next_segment = split[0][0]
            return next_segment
        elif segment in split[1]:
            split[1].remove(segment)
            next_segment = split[1][0]
            return next_segment
        raise ValueError("Cant trace segment in Jones States because it is not contained in the crossing.")

    def get_next_crossing(self,diagram, segment,previous_crossing):
        crossings = diagram.get_crossings_containing_segment(segment)
        if previous_crossing==crossings[0]:
            return crossings[1]
        else:
            return crossings[0]

    def remove_segments_of_circle(self,diagram, segment_of_circle,segments):
        previous_crossing = None
        segment = segment_of_circle
        segments.remove(segment)
        next_crossing = self.get_next_crossing(diagram, segment, previous_crossing)
        next_segment = self.get_next_segment(next_crossing,segment)
        while next_segment in segments:
            segments.remove(next_segment)
            previous_crossing = next_crossing
            segment = next_segment
            next_crossing = self.get_next_crossing(diagram, segment, previous_crossing)
            next_segment = self.get_next_segment(next_crossing,segment)

    def get_number_of_circles_in_splitting(self,diagram):
        number_of_circles = 0
        segments = diagram.segments.copy()
        while len(segments)>0:
            number_of_circles +=1
            segment = segments[0]
            self.remove_segments_of_circle(diagram,segment,segments)
        return number_of_circles

    def get_monomial_of_state(self,diagram):
        return [1,self.get_number_of_A_labels(),self.get_number_of_B_labels(),self.get_number_of_circles_in_splitting(diagram)-1]

    
        


