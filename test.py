import unittest
from src.knotdiagram import KnotDiagram,Crossing, Region
from src.kstate import KauffmanState, StateNode
from src.lattice import StateLattice


class TestTrefoilKnotDiagram(unittest.TestCase):
    def setUp(self):
        self.pd = [(6, 4, 1,3), (4, 2, 5, 1), (2, 6, 3, 5)]
        self.diagram = KnotDiagram(self.pd)
    
    def test_get_region(self):
        region = Region((6,4,2))
        self.assertEqual(self.diagram.get_region(0,0),region)

    def test_get_region2(self):
        region = Region((1,4))
        self.assertEqual(self.diagram.get_region(1,3),region)

    def test_crossing_count(self):
        self.assertEqual(self.diagram.number_of_crossings, 3)

    def test_segment_count(self):
        self.assertEqual(self.diagram.number_of_segments, 6)

    def test_region_count(self):
        self.assertEqual(self.diagram.number_of_regions, 5)

class TestKauffmanState(unittest.TestCase):
    def setUp(self):
        self.pd = [(6, 4, 1,3), (4, 2, 5, 1), (2, 6, 3, 5)]
        self.diagram = KnotDiagram(self.pd)
        self.marker_positions = {
            Crossing(self.pd[0]): 0,
            Crossing(self.pd[1]): 1,
            Crossing(self.pd[2]): 1 
            }
        self.kstate = KauffmanState(self.marker_positions)

    def test_twice_transposition(self):
        self.assertEqual(self.kstate.transpose(6).transpose(6)==self.kstate,True)

    def test_valid_kauffman_state(self):
        # Choose marker positions: crossing -> marker index (0 to 3)
        marker_positions = [0,1,1]
        state = KauffmanState.from_marker_positions(self.diagram, marker_positions)
        self.assertEqual(list(state.marker_positions.values()), marker_positions)

    def test_invalid_kauffman_state_missing_crossing(self):
        marker_positions = [0,1]  # Only 2 crossings provided
        with self.assertRaises(ValueError):
            KauffmanState.from_marker_positions(self.diagram, marker_positions)

    def test_invalid_kauffman_state_out_of_range_marker(self):
        marker_positions = [0,4,6] # Invalid marker index
        with self.assertRaises(ValueError):
            KauffmanState.from_marker_positions(self.diagram, marker_positions)

    def test_invalid_kauffman_state_same_region_marker(self):
        marker_positions = [0,0,0]
        with self.assertRaises(ValueError):
            KauffmanState.from_marker_positions(self.diagram, marker_positions)


class TestStateLattice(unittest.TestCase):
    def setUp(self):
        self.pd = [(6, 4, 1,3), (4, 2, 5, 1), (2, 6, 3, 5)]
        self.diagram = KnotDiagram(self.pd)
        self.state_lattice = StateLattice(self.diagram)

    def test_trefoil_min_state(self):
        min_state = KauffmanState.from_marker_positions(self.diagram, [3,0,3])
        self.assertEqual(self.state_lattice.get_minimal_state(1), min_state)

class TestStateNode(unittest.TestCase):
    def state_nodes(self):
        list_of_nodes = [StateNode(None,"12341"), StateNode(None,"12342"), StateNode(None,"12343")]
        self.assertEqual(StateNode(None,"11234") in list_of_nodes, True)

    def not_in_state_node_list(self):
        list_of_nodes = [StateNode(None,"12341"), StateNode(None,"12342"), StateNode(None,"12343")]
        self.assertEqual(StateNode(None,"123411") in list_of_nodes, False)
if __name__=="__main__":
    unittest.main()