from src.knotdiagram import KnotDiagram
from src.lattice import StateLattice
from src.visualize import LatticeImage

from PIL import Image
k16 = [
    (2,9,3,10),
    (4,2,5,1),
    (7,16,8,17),
    (8,3,9,4),
    (10,6,11,5),
    (11,21,12,20),
    (13,25,14,24),
    (15,6,16,7),
    (17,1,18,32),
    (19,28,20,29),
    (21,15,22,14),
    (23,30,24,31),
    (25,13,26,12),
    (27,18,28,19),
    (29,26,30,27),
    (31,22,32,23)
]

def main():
    # Example: Trefoil knot in PD notation
    trefoil_pd = [(6, 4, 1,3), (4, 2, 5, 1), (2, 6, 3, 5)]
    link_pd = [
        (1,5,4,16),
        (16,4,15,3),
        (3,13,2,12),
        (2,11,1,12),
        (15,7,14,8),
        (8,14,9,13),
        (5,17,6,22),
        (22,6,21,7),
        (9,18,10,19),
        (19,10,20,11),
        (21,17,20,18)
    ]
    knot_8_8 = [
        (1,7,2,6),
        (2,5,3,6),
        (5,12,4,11),
        (4,10,3,11),
        (1,8,16,7),
        (16,13,15,12),
        (13,8,14,9),
        (14,10,15,9)
    ]
    fig_8=[
        (4,8,3,1),
        (2,7,1,6),
        (8,4,7,5),
        (6,3,5,2),
    ]
    paper_knot = [
        (1,13,20,14),
        (19,9,18,10),
        (17,7,16,8),
        (15,1,14,2),
        (13,5,12,6),
        (11,15,10,16),
        (9,17,8,18),
        (7,3,6,4),
        (5,11,4,12),
        (3,19,2,20)
    ]

    diagram = KnotDiagram(k16)

    lattice = StateLattice(diagram,1)
    lattice.build_lattice()

    print(len(lattice.nodes))
    i= lattice.nodes.index(lattice.edges[1][1])
    print(lattice.get_depth())

    lattice_image = LatticeImage(lattice, image_size=(1024, 2048), padding=(10, 20), text_size=6)
    lattice_image.draw_lattice()

if __name__ == "__main__":
    main()

