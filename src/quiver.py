import math 

from PIL import Image,ImageDraw

class QuiverVertex:
    def __init__(self, segment, coordinates):
        self.segment = segment
        self.coordinates  = coordinates

    def __repr__(self):
        return f"Vertex {self.segment} at {self.coordinates}. "
        
    def get_text(self):
        if self.segment > 9:
            return f" {self.segment} "
        else:
            return f"  {self.segment} "

    def get_layer_spacing_x(self, image_size, quiver_width, padding):
        return math.floor((image_size[0] - 2 * padding[0]) / (quiver_width + 1))

    def get_layer_spacing_y(self, image_size,quiver_height, padding):
        """
        Calculate the vertical spacing between layers based on the image height and depth.
        """
        return math.floor((image_size[1] - 2 * padding[1]) / (quiver_height + 1))

    def get_coordinates_img(self, image_size, quiver_width, quiver_height, padding = [20,20]):
        
        layer_height = self.get_layer_spacing_y(image_size, quiver_height, padding)
        layer_width = self.get_layer_spacing_x(image_size,quiver_width,padding)
        x = padding[0] + self.coordinates[0] * layer_width
        y = padding[1] + self.coordinates[1] * layer_height
        return (x,y)
    
    def get_x_coordinate(self):
        return self.coordinates[0]
    
    def get_y_coordinate(self):
        return self.coordinates[1]

class EmptyVertex(QuiverVertex):
    def __init__(self, coordinates):
        super().__init__(" ", coordinates)

    def get_text(self):
        return "    "

class QuiverArrow:
    """
    ARrow in the quiver:
    source_vertex = object QuiverVertex
    target_vertex = object QuiverVertex
    """
    def __init__(self, source_vertex, target_vertex):
        self.source = source_vertex
        self.target = target_vertex

    def __repr__(self):
        return f"{self.source.segment}->{self.target.segment}"
    
    def get_coordinates(self):
        return [self.source.coordinates,self.target.coordinates]

    def point_on_line(self,source, target, t):
        return (source[0]*t+target[0]-target[0]*t, source[1]*t+target[1]-target[1]*t)

    def shorten_line(self, source, target, text_size):
        dx = source[0] - target[0]
        dy = source[1] - target[1]
        distance = math.sqrt( dx**2 + dy**2)
        length = (text_size+3)/distance
        return [self.point_on_line(source,target,1-length), self.point_on_line(source,target,length)]

    def get_arrow_triangle(self, image_size, text_size, quiver_width, quiver_height, padding=[20,20]):
        source_coordinates = self.source.get_coordinates_img(image_size,quiver_width,quiver_height,padding)
        target_coordinates = self.target.get_coordinates_img(image_size,quiver_width,quiver_height,padding)
        shortened = self.shorten_line(source_coordinates,target_coordinates, text_size)
        x1,y1  = shortened[1] #arrow tip
        x0,y0 = shortened[0]
        xb,yb = self.shorten_line(source_coordinates,target_coordinates, text_size+5)[1]
        alpha = math.atan2(y1-y0,x1-x0)-90*math.pi/180
        a = 2*math.cos(alpha)
        b = 2*math.sin(alpha)
        vtx0 = (xb+a, yb+b)
        vtx1 = (xb-a, yb-b)
        return [(x1,y1),vtx0,vtx1]

    def get_coordinates_img(self, image_size, text_size, quiver_width, quiver_height, padding = [20,20]):
        source_coordinates = self.source.get_coordinates_img(image_size,quiver_width,quiver_height,padding)
        target_coordinates = self.target.get_coordinates_img(image_size,quiver_width,quiver_height,padding)
        return self.shorten_line(source_coordinates,target_coordinates, text_size)


class QuiverPlotter:
    def __init__(self,diagram, image_size = (700,400), text_size = 12, padding = [20,20]):
        self.diagram = diagram
        self.image_size = image_size
        self.text_size = text_size
        self.padding = padding
        self.vertices = []
        self.arrows = []
        self._build_graph()

    def __repr__(self):
        return f"Quiver:\n Vertices {self.vertices} \n Arrows {self.arrows}"

    def get_vertex(self,segment):
        for vertex in self.vertices:
            if vertex.segment == segment:
                return vertex

    def create_arrow(self,source,target):
        source = self.get_vertex(source)
        target = self.get_vertex(target)
        if source == None or target == None:
            return
        return QuiverArrow(source, target)

    def get_arrows(self):
        arrows = []
        for crossing in self.diagram.pd_notation:
            for i in range(4):
                arrow = self.create_arrow(crossing[i],crossing[i-1])
                if arrow:
                    arrows.append(arrow)
        return arrows

    def _build_graph(self):
        if self.diagram.get_diagram_type()=="2-bridge":
            self._build_graph_2bridge()
        else:
            raise NotImplementedError("At the moment only quivers of 2-bridge knots can be plotted")

    def _build_graph_2bridge(self):
        previous_box_start, previous_box_width = (0,0)
        for box in self.diagram.boxes:
            vertex_data = box.get_vertices_with_coordinates(previous_box_start,previous_box_width)
            this_box_start,this_box_width = box.get_box_x_measures(previous_box_start,previous_box_width)
            vertices = [QuiverVertex(vertex_date[0],vertex_date[1]) for vertex_date in vertex_data]
            self.vertices.extend(vertices)
            previous_box_start,previous_box_width=this_box_start,this_box_width
        self.arrows = self.get_arrows()

    def _get_max_width(self):
        max_width = 0
        for vertex in self.vertices:
            x_axis = vertex.get_x_coordinate()
            if x_axis>max_width:
                max_width = x_axis
        return max_width
    
    def _get_max_height(self):
        max_height = 0
        for vertex in self.vertices:
            y_axis = vertex.get_y_coordinate()
            if y_axis>max_height:
                max_height = y_axis
        return max_height
    
    def _get_vertex_at_coordinates(self,coordinates):
        """
        returns empty vertex if no vertex found at coordinates
        """
        for vertex in self.vertices:
            if vertex.coordinates == coordinates:
                return vertex
        return EmptyVertex(coordinates)

    def _preprocess_labels(self, labels):
        labels = [str(label) for label in labels]
        max_len = len(max(labels,key=len))
        labels = [f' {" "*(max_len-len(label))}{label} ' for label in labels]
        return labels
        
    def print_quiver(self, custom_labels=None):
        labels = self._preprocess_labels(custom_labels) if custom_labels is not None else None
        quiver_width = self._get_max_width()
        quiver_height = self._get_max_height()
        for i in range(quiver_height+1):
            row = ""
            for j in range(quiver_width+1):
                vertex = self._get_vertex_at_coordinates((j,i))
                if custom_labels and not isinstance(vertex, EmptyVertex):
                    row += labels[vertex.segment-1]
                else:
                    row += vertex.get_text()
            print(row)
            print()


    def _get_image_size(self):
        return self.image_size
        

    def _get_text_size(self):
        return self.text_size

    def get_padding(self):
        return self.padding

    def draw_quiver(self,filename=None):
        image_size = self._get_image_size()
        text_size = self._get_text_size()
        padding = self.get_padding()
        quiver_width = self._get_max_width()
        quiver_height = self._get_max_height()
        image = Image.new('1', image_size, "white")
        draw = ImageDraw.Draw(image)
        for arrow in self.arrows:
            draw.line(arrow.get_coordinates_img(image_size,text_size,quiver_width,quiver_height,padding), fill="black", width=1)
            draw.polygon(arrow.get_arrow_triangle(image_size,text_size,quiver_width,quiver_height,padding), fill="black")
        for vertex in self.vertices:
            draw.text(vertex.get_coordinates_img(image_size,quiver_width,quiver_height,padding), vertex.get_text(), fill="black",anchor="mm",font_size=text_size)
        if filename==None:
            image.save("quiver.png")
        else:
            image.save(filename)

    def vertex_label(self,vertex,module):
        dim_vec = module.get_dimension_vector()
        dim = dim_vec[vertex.segment-1]
        return str(dim)+f"({str(vertex.segment)})"


    
    def  draw_module(self, module, filename=None):
        image_size = self._get_image_size()
        text_size = self._get_text_size()
        padding = self.get_padding()
        quiver_width = self._get_max_width()
        quiver_height = self._get_max_height()
        image = Image.new('1', (image_size[0]+250,image_size[1]+50), "white")
        draw = ImageDraw.Draw(image)
        for arrow in self.arrows:
            draw.line(arrow.get_coordinates_img(image_size,text_size,quiver_width,quiver_height,padding), fill="black", width=1)
            draw.polygon(arrow.get_arrow_triangle(image_size,text_size,quiver_width,quiver_height,padding), fill="black")
        for vertex in self.vertices:
            draw.text(vertex.get_coordinates_img(image_size,quiver_width,quiver_height,padding), self.vertex_label(vertex,module), fill="black",anchor="mm",font_size=text_size)
        draw.text((image_size[0]+30,30), module.get_map_list_string(), font_size = text_size, align = "left")
        if filename==None:
            image.save("module.png")
        else:
            image.save(filename)
