import pytest
import os

from src.knotdiagram import KnotDiagram

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

def test_fig_8():
    diagram = KnotDiagram(fig_8)
    lattice = diagram.get_lattice(1)
    assert lattice.get_depth()==3

def test_8_8():
    diagram = KnotDiagram(knot_8_8)
    lattice = diagram.get_lattice(1)
    assert lattice.get_depth()==9