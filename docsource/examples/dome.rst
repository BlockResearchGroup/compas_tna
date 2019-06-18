================================================================================
The dome
================================================================================

.. figure:: /_images/dome.png
    :figclass: figure
    :class: figure-img img-fluid


**Downloads**

* :download:`dome.3dm <dome.3dm>`
* :download:`dome.json <dome.json>`


Load session
============

In this example, we will load the previously computed form and force diagrams of
a dome from a TNA json file, which can be downloaded from the link above.

Note that if you would like to go through the process yourself, the connected lines which served
as input geometry are available in the Rhino file (:download:`dome.3dm <dome.3dm>`).
These are the required steps:

* ``TNA_form > lines``
* ``TNA_select > form > vertices > boundary`` => mark as supports (``is_anchor = True``).
* ``TNA_settings`` => ``boundaries.feet = 1``
* ``TNA_boundaries``
* ``TNA_force``
* ``TNA_move > force > diagram``
* ``TNA_horizontal``
* ``TNA_vertical`` => ``Z Max = 4.0``

To load the equilibrium solution from a session file, run ``TNA_file``,
choose the option ``open`` and then select the downloaded json file (:download:`dome.json <dome.json>`).


Modify equilibrium
==================

At this point you can continue modifying the equilibrium starting from the previously
saved state and save the new state as a different session..

For example, you could recompute vertical equilibrium with a different ``Z Max`` value,
or you could set constraints on the horizontal forces and see what happens.

To save the new state in the same file, do ``TNA_file > save``
To save the new state in a different file, do ``TNA_file > save_as``, select a destination folder and
provide a new target name.
