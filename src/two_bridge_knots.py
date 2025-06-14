### Careful really terrible code is coming
from src.knotdiagram import Crossing

class BoxString:
    def __init__(self,box_entrance,  entrance_segment ,  length):
        self.input = (box_entrance, entrance_segment)
        self.output = self._calculate_output(box_entrance,entrance_segment, length) 
        self.length = length
    
    def _calculate_output(self, input_entrance,input_segment, length):
        number_of_crossings = length -1
        position = (input_entrance+number_of_crossings)%2+2
        output_segment = input_segment+number_of_crossings
        if input_entrance>1:
            position = position - 2
        return (position, output_segment)

    def get_input(self):
        return self.input

    def get_output(self):
        return self.output

    def update_string_exit(self,output_segment):
        box_exit, old_segment = self.output
        self.output = (box_exit,output_segment)

    def get_segments(self):
        start = self.input[1]
        segments = [i for i in range(start,start+self.length)]
        segments[-1] = self.output[1]
        return segments


class Box:
    def __init__(self,bridge, number_of_crossings,box_number, number_of_boxes):
        self.bridge = bridge # upper or lower bridge in the knot
        self.number_of_crossings = number_of_crossings
        self.number_of_boxes = number_of_boxes
        self.box_number=box_number
        self.strings = []
    
    def __repr__(self):
        return f"Box number {self.box_number} on {self.bridge} bridge with {self.number_of_crossings} crossings"

    def update_last_string(self,segment,string=-1):
        self.strings[string].update_string_exit(segment)

    def is_string_already_added(self,entrance):
        for string in self.strings:
            if string.input[0]==entrance:
                return True
        return False

    def get_number_of_added_strings(self):
        return len(self.strings)

    def add_string(self,entrance,segment):
        if len(self.strings)>=2:
            raise ValueError("cannot add more than 2 strings")
        string = BoxString(entrance,segment,self.number_of_crossings+1)        
        self.strings.append(string)

    def get_segment_at_position(self,position):
        for string in self.strings:
            if string.input[0]==position:
                return string.input[1]        
            elif string.output[0]==position:
                return string.output[1]

    def get_first_string_in(self):
        return self.strings[0].get_input()
    def get_second_string_in(self):
        return self.strings[1].get_input()

    def get_string_exit(self,string_number):
        if string_number==0:
            return self.get_first_string_out()
        elif string_number==1:
            return self.get_second_string_out()

    def get_first_string_out(self):
        return self.strings[0].get_output()

    def get_second_string_out(self):
        return self.strings[1].get_output()

    def get_next_box_input(self, string):
        if string==0:
            exit_pos, output_segment = self.get_first_string_out()
        else:
            exit_pos, output_segment = self.get_second_string_out()
        next_box, bridge, entrance_next_box = self.get_next_box_number(string)
        return (next_box,entrance_next_box,output_segment)



    def get_next_box_number(self, string):
        """
        get the number of the next box
        Int: string
        0 == String A
        1 == String B

        returns next_box_number, bridge ("upper" or "lower"), entrance in next box
        """
        next_box_number = None
        if string==0:
            output_pos,output_segment = self.get_first_string_out()
        else: 
            output_pos,output_segment = self.get_second_string_out()
        if self.bridge == "upper":
            if output_pos == 2:
                next_box_number = self.box_number +2
                entrance_next_box = 0
                bridge = "upper"
                if self.box_number+2>=self.number_of_boxes:
                    if self.number_of_boxes%2==0:
                        next_box_number = 0
                        entrance_next_box = 1
                        bridge = "lower"
                    else:
                        next_box_number -= 1
                        entrance_next_box = 2
                        bridge = "lower"
            elif output_pos == 0:
                next_box_number = self.box_number -2
                if next_box_number < 0:
                    next_box_number = 0
                    entrance_next_box = 0
                    bridge = "lower"
            elif output_pos == 1:
                next_box_number = self.box_number -1
                entrance_next_box = 2
                bridge = "lower"
            elif output_pos == 3:
                if self.box_number+1 == self.number_of_boxes:
                    next_box_number = self.box_number -1 
                    bridge = "lower"
                    entrance_next_box = 3
                else:
                    next_box_number = self.box_number + 1
                    bridge = "lower"
                    entrance_next_box = 0
        elif self.bridge == "lower":
            if output_pos == 0:
                next_box_number = self.box_number -1
                bridge = "upper"
                entrance_next_box = 3
                if self.box_number == 0:
                    next_box_number = 1
                    bridge = "upper"
                    entrance_next_box = 0
            elif output_pos ==1:
                next_box_number = self.box_number - 2
                bridge = "lower"
                entrance_next_box = 3
                if next_box_number < 0:
                    if self.number_of_boxes%2==0:
                        next_box_number = self.number_of_boxes -1
                        bridge = "upper"
                        entrance_next_box = 2
                    else:
                        next_box_number = self.number_of_boxes -1
                        bridge = "lower"
                        entrance_next_box = 3
            elif output_pos == 2:
                next_box_number = self.box_number +1
                bridge = "upper"
                entrance_next_box = 1
                if self.box_number == self.number_of_boxes -1:
                    next_box_number=self.box_number -1
                    bridge = "upper"
                    entrance_next_box=2
            elif output_pos==3:
                next_box_number = self.box_number +2
                bridge = "lower"
                entrance_next_box = 1
                if self.box_number == self.number_of_boxes-2:
                    next_box_number = self.box_number+1
                    bridge = "upper"
                    entrance_next_box = 3
                elif self.box_number == self.number_of_boxes-1:
                    next_box_number = 0
                    bridge = "lower"
                    entrance_next_box = 1
        return (next_box_number,bridge,entrance_next_box)



    def construct_crossings(self):
        if len(self.strings)!=2:
            raise ValueError("You cannot construct the crossings in box if the box does not have two strings")
        first_string_entrance, first_string_segment = self.get_first_string_in()
        segments_first_string =  self.strings[0].get_segments()
        if first_string_entrance > 1:
            segments_first_string.reverse()

        second_string_entrance, second_string_segment = self.get_second_string_in()
        segments_second_string = self.strings[1].get_segments()
        if second_string_entrance > 1:
            segments_second_string.reverse()

        crossings_left_to_right = []
        for i in range(self.number_of_crossings):
            crossings_left_to_right.append(self.build_crossing(i,segments_first_string[i:i+2],first_string_entrance, segments_second_string[i:i+2],second_string_entrance))
        self.crossings = crossings_left_to_right


    def build_crossing(self,number_in_box, segments_string_a,entrance_a,segments_string_b,entrance_b):
        first_segment = None
        if entrance_a>1:
            crossing_position_starting_from_a = (self.number_of_crossings-number_in_box-1) %2
        else:
            crossing_position_starting_from_a = number_in_box % 2
        if entrance_b>1:
            crossing_position_starting_from_b = (self.number_of_crossings-number_in_box-1) %2
        else:
            crossing_position_starting_from_b = number_in_box % 2

        string_a_is_underpassing = True
        if self.bridge == "upper":
            if entrance_a == 3:
                if crossing_position_starting_from_a == 0:
                    string_a_is_underpassing = True
                else:
                    string_a_is_underpassing = False
            if entrance_a == 2:
                if crossing_position_starting_from_a == 0:
                    string_a_is_underpassing = False
                else:
                    string_a_is_underpassing = True
            if entrance_a == 1:
                if crossing_position_starting_from_a == 0:
                    string_a_is_underpassing = False
                else:
                    string_a_is_underpassing = True
            if entrance_a == 0:
                if crossing_position_starting_from_a == 0:
                    string_a_is_underpassing = True
                else:
                    string_a_is_underpassing = False
        else:
            if entrance_a == 3:
                if crossing_position_starting_from_a == 0:
                    string_a_is_underpassing = False
                else:
                    string_a_is_underpassing = True
            if entrance_a == 2:
                if crossing_position_starting_from_a == 0:
                    string_a_is_underpassing = True
                else:
                    string_a_is_underpassing = False
            if entrance_a == 1:
                if crossing_position_starting_from_a == 0:
                    string_a_is_underpassing = True
                else:
                    string_a_is_underpassing = False
            if entrance_a == 0:
                if crossing_position_starting_from_a == 0:
                    string_a_is_underpassing = False
                else:
                    string_a_is_underpassing = True

        if string_a_is_underpassing:
            if entrance_a>1:
                first_segment = segments_string_a[1]
                segments_string_a.remove(first_segment)
                if entrance_a == 2:
                    if crossing_position_starting_from_a == 0:
                        a_from_top = True
                    else:
                        a_from_top = False
                else:
                    if crossing_position_starting_from_a == 0:
                        a_from_top = False
                    else:
                        a_from_top = True
                
                if a_from_top:
                    second_segment = segments_string_b[0]
                    segments_string_b.remove(second_segment)
                else:
                    second_segment = segments_string_b[1]
                    segments_string_b.remove(second_segment)


            else:
                first_segment = segments_string_a[0]
                segments_string_a.remove(first_segment)
                if entrance_a == 0:
                    if crossing_position_starting_from_a == 0:
                        a_from_top = True
                    else:
                        a_from_top = False
                else:
                    if crossing_position_starting_from_a == 0:
                        a_from_top = False
                    else:
                        a_from_top = True
                
                if a_from_top:
                    second_segment = segments_string_b[0]
                    segments_string_b.remove(second_segment)
                else:
                    second_segment = segments_string_b[1]
                    segments_string_b.remove(second_segment)
            third_segment = segments_string_a[0]
            fourth_segment = segments_string_b[0]
        else:
            if entrance_b>1:
                first_segment = segments_string_b[1]
                segments_string_b.remove(first_segment)
                if entrance_b == 2:
                    if crossing_position_starting_from_b == 0:
                        b_from_top = True
                    else:
                        b_from_top = False
                else:
                    if crossing_position_starting_from_b == 0:
                        b_from_top = False
                    else:
                        b_from_top = True
                
                if b_from_top:
                    second_segment = segments_string_a[0]
                    segments_string_a.remove(second_segment)
                else:
                    second_segment = segments_string_a[1]
                    segments_string_a.remove(second_segment)


            else:
                first_segment = segments_string_b[0]
                segments_string_b.remove(first_segment)
                if entrance_b == 0:
                    if crossing_position_starting_from_b == 0:
                        b_from_top = True
                    else:
                        b_from_top = False
                else:
                    if crossing_position_starting_from_b == 0:
                        b_from_top = False
                    else:
                        b_from_top = True
                
                if b_from_top:
                    second_segment = segments_string_a[0]
                    segments_string_a.remove(second_segment)
                else:
                    second_segment = segments_string_a[1]
                    segments_string_a.remove(second_segment)

            third_segment = segments_string_b[0]
            fourth_segment = segments_string_a[0]
        return Crossing([first_segment,second_segment,third_segment,fourth_segment])

class TwoBridgeDiagram:
    def __init__(self, conway_normalform):
        self.normalform = conway_normalform

    def construct_boxes(self):
        boxes = []
        number_of_boxes = len(self.normalform)
        for box in range(number_of_boxes):
            if box%2==0:
                bridge = "lower"
            else:
                bridge = "upper"
            boxes.append(Box(bridge,self.normalform[box],box,number_of_boxes))
        self.boxes = boxes
        self.construct_connections()

    def construct_connections(self):
        number_of_boxes = len(self.normalform)
        connections =[]
        if number_of_boxes == 1:
            box_connections = [(0,2),(0,3),(0,0),(0,1)]
            connections.append(box_connections)
        else:
            connections = [[(0,0),(0,0),(0,0),(0,0)] for i in range(number_of_boxes)]
            connections[0][0] = (1,0)
            connections[1][0] = (0,0)
            for i in range(number_of_boxes):
                if i+2==number_of_boxes:
                    if self.boxes[i].bridge=="upper":
                        connections[i][2] = (i+1,2)
                        connections[i][3] = (i+1,0)
                        connections[i+1][2] = (i,2)
                        connections[i+1][0] = (i,3)
                    else:
                        connections[i][2] = (i+1,1)
                        connections[i][3] = (i+1,3)
                        connections[i+1][1] = (i,2)
                        connections[i+1][3] = (i,3)
                elif i+1==number_of_boxes:
                    if self.boxes[i].bridge=="upper":
                        connections[i][2] = (0,1)
                        connections[0][1] = (i,2)
                    elif self.boxes[i].bridge == "lower":
                        connections[i][3] = (0,1)
                        connections[0][1] = (i,3)
                else:
                    if self.boxes[i].bridge == "upper":
                        connections[i][2] = (i+2,0)
                        connections[i][3] = (i+1,0)
                        connections[i+2][0] = (i,2)
                        connections[i+1][0] = (i,3)
                    elif self.boxes[i].bridge == "lower":
                        connections[i][2] = (i+1,1)
                        connections[i][3] = (i+2,1)
                        connections[i+1][1] = (i,2)
                        connections[i+2][1] = (i,3)
        self.connections = connections



    def fill_out_box_segments(self):
        number_of_boxes = len(self.normalform)
        box = 0
        entrance = 1
        current_segment = 1

        for i in range(2*number_of_boxes):
            current_box = self.boxes[box]
            current_box.add_string(entrance,current_segment)
            string = current_box.get_number_of_added_strings()-1
            output_position,current_segment = current_box.get_string_exit(string)
            box,entrance = self.connections[box][output_position]
            next_box = self.boxes[box]
            segment = next_box.get_segment_at_position(entrance)
            if next_box.is_string_already_added(entrance):
                entrance = 0
                current_box.update_last_string(segment)
                box = 1
                entrance = 0
                if number_of_boxes==1:
                    box=0
                    entrance=2
                current_segment = sum(self.normalform) +1
                current_box = self.boxes[box]

class TwoBridgeKnot:
    def __init__(self, conway_normalform):
        self.normalform = conway_normalform

    def __repr__(self):
        return f"Conway Normalform: {self.normalform}"

    def get_rational(self):
        tmp = self.normalform
        tmp.reverse()
        nenner = tmp[0]
        zähler = 1
        for a in tmp[1:]:
            switch = a*nenner + zähler
            zähler = nenner
            nenner = switch
        return (zähler,nenner)
    
    def get_pd_notation(self):
        diagram = TwoBridgeDiagram(self.normalform)
        diagram.construct_boxes()
        diagram.fill_out_box_segments()
        pd_notation = []
        for box in diagram.boxes:
            box.construct_crossings()
            for crossing in box.crossings:
                pd_notation.append(tuple(crossing.segments))

        return pd_notation