from PIL import Image,ImageDraw
import math

class LatticeImage:
    """
    Class to handle the creation of an image representation of a knot lattice.
    """
    def __init__(self, lattice, image_size=(512, 1024),padding=(10, 20),text_size=8):
        self.lattice = lattice
        self.image_size = image_size
        self.padding = padding
        self.text_size = text_size
    
    def get_layer_spacing_y(self):
        """
        Calculate the vertical spacing between layers based on the image height and depth.
        """
        return math.floor((self.image_size[1] - 2 * self.padding[1]) / (self.lattice.get_depth() + 1))

    def set_node_coordinates(self):
        """
        Set the coordinates for each node in the lattice based on its layer and position.
        """
        length_list_x = [node.get_length() for node in self.lattice.nodes]
        for node in self.lattice.nodes:
            node.position = (length_list_x.count(node.get_length()), node.get_length())
            length_list_x.remove(node.get_length())


    def get_layer_spacing_x(self, node):
        number_of_nodes_in_layer = len(self.lattice.get_nodes_in_layer(node.get_length()))
        return math.floor((self.image_size[0] - 2 * self.padding[0]) / (number_of_nodes_in_layer + 1))


    def set_image_size(self, width, height):
        self.image_size = (width, height)


    def get_node_coordinates(self, node):
        """
        Convert a node's position to pixel coordinates in the image.
        """
        layer_length = self.get_layer_spacing_y()
        layer_width = self.get_layer_spacing_x(node)
        x = self.padding[0] + node.position[0] * layer_width
        y = self.padding[1] + node.position[1] * layer_length
        return (x, y)

    def get_edge_coordinates(self,edge):
        start_node = self.lattice.get_node_by_transpositions(edge[0].transpositions.string)
        end_node = self.lattice.get_node_by_transpositions(edge[1].transpositions.string)
        start_node_coords = self.get_node_coordinates(start_node)
        end_node_coords = self.get_node_coordinates(end_node)

        return [
            (start_node_coords[0], start_node_coords[1] + self.text_size),
            (end_node_coords[0], end_node_coords[1] - self.text_size)
        ]

    def draw_lattice(self):
        self.set_node_coordinates()
        im = Image.new('1', self.image_size, "white")
        draw = ImageDraw.Draw(im)
        for edge in self.lattice.edges:
            draw.line(self.get_edge_coordinates(edge), fill="black", width=1)
        for node in self.lattice.nodes:
            node_coords = self.get_node_coordinates(node)

            draw.text((node_coords[0], node_coords[1]), node.transpositions.string, fill="black",anchor="mm",font_size=self.text_size)
        im.save("lattice.png")

def node_coordinate_to_img_position(node_coordinate, layer_length, layer_width, padding_x, padding_y):
    """
    Convert node coordinates to image pixel positions.
    """
    x = padding_x + node_coordinate[0] * layer_width
    y = padding_y + node_coordinate[1] * layer_length 
    return (x, y)

def set_node_coordinates(nodes):
    length_list_x = [node.get_length() for node in nodes]
    for node in nodes:
        node.position = (length_list_x.count(node.get_length()),node.get_length())
        length_list_x.remove(node.get_length())

def draw_lattice(nodes,edges):
    set_node_coordinates(nodes)
    length_list_x = [node.get_length() for node in nodes]
    depth = nodes[-1].get_length()
    img_width = 512
    img_height = 1024
    padding_x = 10
    padding_y = 20
    padding_text_y = 8
    im = Image.new('1',(img_width,img_height),"white")
    draw = ImageDraw.Draw(im)
    layer_length  = math.floor((img_height - 2*padding_y)/(depth+1))
    for edge in edges:
        start_node_index = nodes.index(edge[0])
        end_node_index = nodes.index(edge[1])

        layer = edge[0].get_length()
        number_of_layer_nodes_layer_start = length_list_x.count(layer)
        layer_width_start = math.floor((img_width - 2*padding_x)/(number_of_layer_nodes_layer_start+1))

        number_of_layer_nodes_layer_target = length_list_x.count(layer+1)
        layer_width_target = math.floor((img_width - 2*padding_x)/(number_of_layer_nodes_layer_target+1))

        start_pos = node_coordinate_to_img_position(nodes[start_node_index].position, layer_length,layer_width_start, padding_x, padding_y)
        end_pos = node_coordinate_to_img_position(nodes[end_node_index].position, layer_length, layer_width_target, padding_x, padding_y)
        start_pos = (start_pos[0], start_pos[1] + padding_text_y)
        end_pos = (end_pos[0], end_pos[1] - padding_text_y)
        draw.line([start_pos,end_pos],fill="black",width=1)

        
    im.save("lattice.png")




    

