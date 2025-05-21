import unittest
from core import KnotDiagram, Crossing, KauffmanState

class TestTrefoilKnotDiagram(unittest.TestCase):
    def setUp(self):
        self.pd = [(6, 4, 1,3), (4, 2, 5, 1), (2, 6, 3, 5)]
        self.diagram = KnotDiagram(self.pd)

    def test_crossing_count(self):
        self.assertEqual(self.diagram.number_of_crossings, 3)

    def test_segment_count(self):
        self.assertEqual(self.diagram.number_of_segments, 6)

    def test_region_count(self):
        self.assertEqual(self.diagram.number_of_regions, 5)

class TestKauffmanState(unittest.TestCase):
    def setUp(self):
        self.pd = [(6, 4, 1,3), (4, 2, 5, 1), (2, 6, 3, 5)]
        self.marker_positions = {
            Crossing(self.pd[0]): 0,
            Crossing(self.pd[1]): 1,
            Crossing(self.pd[2]): 1 
            }
        self.kstate = KauffmanState(self.marker_positions)

    def test_twice_transposition(self):
        self.assertEqual(self.kstate.transpose(6).transpose(6)==self.kstate,True)

if __name__=="__main__":
    unittest.main()