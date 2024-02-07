********************************************************************************
compas_tna.equilibrium
********************************************************************************

.. currentmodule:: compas_tna.equilibrium


Horizontal
==========

Algorithms related to horizontal equilibrium of the form diagram and thus of the
corresponding thrust network.

Horizontal equilibrium is established when the form and force diagram are reciprocal.
Two diagrams are said to be reciprocal if they are each other's dual and if all
corresponding edges are at any specific constant angle.

Note that for legibility, the form and force diagrams in ``compas_tna`` are drawn
such that corresponding edges of reciprocal diagrams are perpendicular.
However, the diagrams are made reciprocal by parallelising the corresponding edges.
The diagrams are thus rotated by 90 degrees and back at the beginning and end of
each of the horizontal equilibrium algorithms.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    horizontal_nodal
    horizontal_numpy
    horizontal_nodal_numpy


Vertical
========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    vertical_from_zmax
    vertical_from_q
