********************************************************************************
Vertical equilibrium
********************************************************************************

.. plot:: tutorial/080_equilibrium_vertical.py
    :class: figure-img img-fluid

Compute vertical equilibrium of a three-dimensional force network.

There are no external loads.
Only selfweight is taken into account.

1. Load the form diagram from a json file.

    Here we use a json file representing a form diagram that has already been
    pre-processed.

2. Initialise the force diagram.

    The force diagram is initialised as the dual of the form diagram.

3. Compute horizontal equilibrium.

    This is achieved by parallelising the form and force diagrams.
    In this example, we keep the geometry of the form diagram fixed (alpha 100).
    After this, the form and force diagram are not just dual but also reciprocal.

4. Compute vertical equilibrium.

    The equilibrium shape of the force network depends on the distribution of
    horizontal forces in the form diagram, and on their magnitude in relation to
    the loads.

    Once the distribution of horizontal forces is fixed, the magnitude can be
    determined by simply choosing a scale factor.

    However, it is difficult to predict which scale factor will result in a
    well-proportioned equilibrium shape.

    Instead, the scale factor can be conveniently determined from the desired maximum
    height of the force network using ``vertical_from_zmax``.


.. literalinclude:: 080_equilibrium_vertical.py
    :language: python

