from src.knotdiagram import KnotDiagram
from src.lattice import StateLattice

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
    diagram = KnotDiagram(link_pd)

    lattice = StateLattice(diagram)
    min_state = lattice.get_minimal_state(22)
    print(min_state)
    print(min_state.get_all_possible_transpositions("ccw"))

    lattice.build_lattice(1)
    print(len(lattice.nodes))
    print(lattice.nodes)

if __name__ == "__main__":
    main()
