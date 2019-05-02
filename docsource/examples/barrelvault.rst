================================================================================
The barrel vault
================================================================================

.. figure:: /_images/barrelvault.png
    :figclass: figure
    :class: figure-img img-fluid


Make the form diagram
---------------------

The first step is to make a form diagram from a set of connected lines.
Make sure the lines are individual line segments and properly connected.
Alternatively, the form diagram can be created from an OBJ file, from a JSON file,
from a Rhino mesh, or a Rhino surface.

.. literalinclude:: barrelvault.py
    :language: python
    :lines: 60-65


Identify the supports
---------------------

After initialising the form diagram, we identify the supports.
The identify the supports, we select the relevant vertices and change their attribute
``is_anchor`` to ``True``.

.. literalinclude:: barrelvault.py
    :language: python
    :lines: 67-74


Update the boundary conditions
------------------------------

Having identified the supports, we update the boundary conditions.
To update the boundary conditions, we add "feet" to the support vertices.

There are two options.
We can add one "foot" per support or two.
The feet represent the horizontal components of the reaction forces at the supports.
If only foot is added, the reaction force at that support is fully constrained to the direction of the foot.
If two feet are added, the horizontal component of the reaction force can be any combination of those two force vectors.

Since a barrel vault is a single curvature equilibrium geometry,
and the form diagram edges in this example are organised in an orthogonal grid,
the horizontal reaction forces at the supports can only lie in the direction of the
spanning arches.

.. literalinclude:: barrelvault.py
    :language: python
    :lines: 76-91


Make the force diagram
----------------------

Once the boundary conditions are set, we can make the force diagram.

.. literalinclude:: barrelvault.py
    :language: python
    :lines: 107-110


Set the constraints
-------------------

This is the most important part of the procedure that ensures we end up with a barrel vault.
A barrel vault is a single curvature geometry and therefore carries loads in only one direction.

This means we have to constrain the relationship between form and force diagram
to only allow forces in one direction. and to make sure that the forces are equally
distributed over the single-span arches.

First, we select all the edges and set ``fmin`` and ``fmax`` of those edges to ``0``.
Then, we select all the edges in the curved, spanning direction
and set ``fmin`` and ``fmax`` to ``2``.
Finally, we set the arches at the beginning and end of the vault to allow only half
of the amount of horizontal force compared to the internal ones, because, in comparison,
they carry only half of the load (set ``fmin`` and ``fmax`` to ``1``).

.. literalinclude:: barrelvault.py
    :language: python
    :lines: 93-105

