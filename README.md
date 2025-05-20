# kstates - Kauffman states of knot diagrams
This project computes the Kauffman state lattice of a knot diagram which is 
given in planar diagram (PD) notation.

## Background
Kauffman states of a knot diagram are given by assigning a marker at each crossing in one of the four incident regions and which satisfy that no region contains more than one marker.
If two markers are adjacent to the same segment we can swap the region of the markers at the crossing to obtain a new Kauffman state. This is called state transposition.
Kauffman showed that the Kauffman states together with the state transposition form a lattice.

To calculate the Kauffman states of a knot diagram, the knot diagram has to be inserted 
in planar diagram (PD) notation. The notation is explained [here](https://knotinfo.math.indiana.edu/descriptions/pd_notation.html).



