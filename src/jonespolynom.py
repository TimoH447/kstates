import math

from src.knotdiagram import Crossing
from src.knotdiagram import KnotDiagram

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

def get_summands_binomial_theorem(power):
    summands = []
    if power == 0:
        return [[1,0]]
    elif power == 1:
        return [[-1,2],[-1,-2]]
    for i in range(power+1):
        coefficient = math.comb(power,i)
        power_in_summand = 2*(i-power+i)
        if power%2 ==1:
            coefficient = -coefficient
        summands.append([coefficient,power_in_summand])
    return summands

def multiply_monomials(mon_a,mon_b):
    coefficient = mon_a[0]*mon_b[0]
    power = mon_a[1] +mon_b[1]
    return [coefficient,power]

def simplify_laurent_polynom(polynom):
    simplified_polynom = []
    for summand in polynom:
        if any(term[1] == summand[1] for term in simplified_polynom):
            for term in simplified_polynom:
                if term[1] == summand[1]:
                    term[0] += summand[0]
        else:
            simplified_polynom.append(summand)
    return simplified_polynom

def get_specialisation(polynom):
    specialisation = []
    for mon in polynom:
        power = mon[2]
        summands_binomial_theorem = get_summands_binomial_theorem(power)
        number_of_summands = len(summands_binomial_theorem)
        other_factor = [1,mon[0]-mon[1]]
        summands_multiplied = list(map(multiply_monomials,summands_binomial_theorem,[other_factor]*number_of_summands))
        simplified_polynom = simplify_laurent_polynom(summands_multiplied)
        for summand in simplified_polynom:
            specialisation.append(summand)
    result = simplify_laurent_polynom(specialisation)
    return result

class JonesCrossing(Crossing):
    def __init__(self,segments,label):
        Crossing.__init__(self,segments)
        self.label = label

    def get_split(self):
        segments = self.segments
        if self.label == "A":
            return [list(segments[:2]),list(segments[2:])]
        elif self.label == "B":
            return [list(segments[1:3]),[segments[3],segments[0]]]
        raise ValueError("Jones Crossing got an unvalid label.")

    def trace_split(self,segment):
        split = self.get_split()
        if segment in split[0]:
            split[0].remove(segment)
            next_segment = split[0][0]
            return next_segment
        elif segment in split[1]:
            split[1].remove(segment)
            next_segment = split[1][0]
            return next_segment
        raise ValueError("Cant trace segment in Jones States because it is not contained in the crossing.")


class JonesState:
    def __init__(self,labels,pd_notation,segments):
        self.labels = labels
        self.crossings = [JonesCrossing(segments,labels[i]) for i,segments in enumerate(pd_notation)]
        self.segments = segments

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

    def get_crossings_containing_segment(self,segment):
        crossing_containg_the_segment = []
        for crossing in self.crossings:
            if segment in crossing.segments:
                crossing_containg_the_segment.append(crossing)
        return crossing_containg_the_segment

    def get_next_segment(self,segment, previous_segment):
        crossings = self.get_crossings_containing_segment(segment)
        crossing_1, crossing_2 = crossings[0],crossings[1]
        other_segment_in_split_1 = crossing_1.trace_split(segment)
        other_segment_in_split_2 = crossing_2.trace_split(segment)
        if other_segment_in_split_1==other_segment_in_split_2:
            return other_segment_in_split_2
        if other_segment_in_split_1==previous_segment:
            return other_segment_in_split_2
        else:
            return other_segment_in_split_1

    def remove_segments_of_circle(self, segment_of_circle,segments):
        segment = segment_of_circle
        segments.remove(segment)
        next_segment = self.get_next_segment(segment,None)
        while next_segment in segments:
            segments.remove(next_segment)
            previous_segment = segment
            segment = next_segment
            next_segment = self.get_next_segment(segment,previous_segment)

    def get_number_of_circles_in_splitting(self):
        number_of_circles = 0
        segments = self.segments.copy()
        while len(segments)>0:
            number_of_circles +=1
            segment = segments[0]
            self.remove_segments_of_circle(segment,segments)
        return number_of_circles

    def get_monomial_of_state(self):
        return [self.get_number_of_A_labels(),self.get_number_of_B_labels(),self.get_number_of_circles_in_splitting()-1]

    
        



class JonesPolynom:
    def __init__(self,pd_notation):
        self.pd_notation = pd_notation
        self.diagram = KnotDiagram(pd_notation)

    def get_twist(self):
        return self.diagram.get_twist_number()
    
    def get_kauffman_bracket(self):
        labels = ["A","B"]
        kauffman_bracket = []
        for i in range(2**self.diagram.number_of_crossings):
            binary = get_binary(i,self.diagram.number_of_crossings)
            state_labels = list(map(binary_to_label,binary))
            state = JonesState(state_labels,self.pd_notation,self.diagram.segments)
            state_polynom = state.get_monomial_of_state()
            kauffman_bracket.append(state_polynom)
        result = get_specialisation(kauffman_bracket)
        twist = self.get_twist()
        power = -3*twist
        if abs(power)%2==0:
            coefficient = 1
        else:
            coefficient = -1
        mon = [coefficient,power]
        result = list(map(multiply_monomials,result,[mon]*len(result)))
        return result



