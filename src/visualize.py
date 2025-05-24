from PIL import Image,ImageDraw
import math

class LatticeImage:
    """
    Class to handle the creation of an image representation of a knot lattice.
    """
    def __init__(self, lattice, image_size=(512, 1024)):
        self.lattice = lattice
        self.image_size = image_size

    def set_image_size(self, width, height):
        self.image_size = (width, height)

    def draw_lattice(self):
        im = Image.new('1', self.image_size, "white")
        draw = ImageDraw.Draw(im)

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




    

