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

    def draw_lattice(self,filename=None):
        self.set_node_coordinates()
        im = Image.new('1', self.image_size, "white")
        draw = ImageDraw.Draw(im)
        for edge in self.lattice.edges:
            draw.line(self.get_edge_coordinates(edge), fill="black", width=1)
        for node in self.lattice.nodes:
            node_coords = self.get_node_coordinates(node)

            draw.text((node_coords[0], node_coords[1]), node.transpositions.string, fill="black",anchor="mm",font_size=self.text_size)
        if filename==None:
            im.save("lattice.png")
        else:
            im.save(filename)




    

