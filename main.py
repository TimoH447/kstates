from src.knotdiagram import KnotDiagram
from src.lattice import StateLattice
from src.visualize import LatticeImage
from src.algebra import JacobianAlgebra,Path, StateModule
from src.two_bridge_knots import TwoBridgeDiagram
from src.polynom import LaurentPolynom

import json
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
perko = [
    (2,13,3,14),
    (5,10,6,11),
    (7,16,8,17),
    (8,1,9,2),
    (11,18,12,19),
    (12,3,13,4),
    (15,6,16,7),
    (17,14,18,15),
    (19,4,20,5),
    (20,9,1,10)
]
knot_8_8 = [
    (1,7,2,6),
    (3,11,4,10),
    (5,3,6,2),
    (7,1,8,16),
    (9,14,10,15),
    (11,5,12,4),
    (13,8,14,9),
    (15,12,16,13)
]
fig_8=[
    (4,1,3,8),
    (2,6,1,7),
    (8,5,7,4),
    (6,2,5,3),
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

def main():
    diagram = KnotDiagram(knot_8_8)
    lattice = StateLattice(diagram,8)

    print(len(lattice.nodes))
    i= lattice.nodes.index(lattice.edges[1][1])
    print(str(lattice.get_minimal_state()))
    print(lattice.get_f_polynomial_latex())
    print(lattice.get_alexander_polynomial_latex())

    lattice_image = LatticeImage(lattice, image_size=(1024, 2048), padding=(10, 20), text_size=6)

    trefoil_pd = [(6, 4, 1,3), (4, 2, 5, 1), (2, 6, 3, 5)]
    jac = JacobianAlgebra._from_pd_notation(trefoil_pd)
    print(jac.get_equivalent_paths([(3,1),(1,4),(4,6),(6,3)]))

def get_paths_of_2bridge():
    knot = TwoBridgeDiagram([3,3])
    print(knot)
    print(knot.get_pd_notation())
    algebra = JacobianAlgebra._from_pd_notation(knot.get_pd_notation())
    paths = algebra.get_equivalent_paths([(1,7),(7,5),(5,9)])
    paths.sort(key=len)
    print(paths)

def get_rolfsen_pd(rolfsen_number):
    with open("rolfsen_pd_dict.json") as f:
        rolfsen_pd_dict = json.load(f)
    return [tuple(x) for x in rolfsen_pd_dict[rolfsen_number]]

def compute_dimensions_rolfsen():
    with open("rolfsen_pd_dict.json") as f:
        rolfsen_pd_dict = json.load(f)
    del rolfsen_pd_dict["0_1"]
    for knot in rolfsen_pd_dict:
        pd_notation = rolfsen_pd_dict[knot]
        algebra = JacobianAlgebra._from_pd_notation(pd_notation)
        print(f"Knot {knot} - Dimension: {algebra.get_dimension()}")



if __name__ == "__main__":
    difference = []
    k9_18 = [
        (1,8,2,9),
        (1,7,18,8),
        (2,12,3,11),
        (18,13,17,12),
        (17,13,16,14),
        (16,7,15,6),
        (6,15,5,14),
        (5,9,4,10),
        (11,3,10,4)
    ]
    #compute_dimensions_rolfsen()
# 32, 92, 184, 308
#  12, 40, 84, 144
# 6 + 6*1, 10 +(1)  10 +(2) 10 +(3) 10, 14*6, 18 * 8
    #pd_notation = get_rolfsen_pd("4_1")
    knot = TwoBridgeDiagram([2,3,3,3])
    print(knot)
    knot.get_structure_info()



"""
    crit = Path([(4,9),(9,2),(2,8),(8,18),(18,7),(7,16),(16,6),(6,15)])
    for element in basis:
        if element==crit:
            print(element)
            print("Equiv_paths:")
            print(element.equivalent_paths)
"""
# 10_81, 10_80, 10_79, 10_148, 10_149, 10_150, 10_151, 10_152, 10_153, 10_154  
    
        
    


