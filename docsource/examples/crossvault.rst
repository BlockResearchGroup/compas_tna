================================================================================
The cross vault
================================================================================

.. figure:: /_images/crossvault.png
    :figclass: figure
    :class: figure-img img-fluid


.. note::

    This example uses the Rhino UI for compas_tna.
    Please download and install the Plugin from here:
    https://github.com/BlockResearchGroup/compas_tna-UI


Load the sample file
====================

First download and open the Rhino file with sample input geometry: :download:`crossvault.3dm <crossvault.3dm>`.


.. figure:: /_images/TNA_open.png
    :figclass: figure
    :class: figure-img img-fluid


Initialise the UI
=================

**Commands**

* ``TNA_init``


To initialise the TNA PythonPlugin, run the command ``TNA_init``.


.. figure:: /_images/TNA_init.png
    :figclass: figure
    :class: figure-img img-fluid


Make the form diagram
=====================

**Commands**

* ``TNA_form > lines``


The first step is then to make a form diagram from a set of connected lines.
Run the command ``TNA_form`` and select the option ``lines``.
Then select the lines on the layer ``Input::Lines``.


.. figure:: /_images/TNA_form.png
    :figclass: figure
    :class: figure-img img-fluid


Identify the supports
=====================

**Commands**

* ``TNA_attributes > form > vertices``


After initialising the form diagram, we identify the supports.
Select the vertices in the corners of the diagram and change their attribute ``is_anchor`` to ``True``.
Use the command ``TNA_attributes`` with options ``form`` and ``vertices``.


.. figure:: /_images/TNA_supports.png
    :figclass: figure
    :class: figure-img img-fluid


Update the boundary conditions
==============================

**Commands**

* ``TNA_boundaries``


Having identified the supports, we update the boundary conditions.
To update the boundary conditions, we add "feet" to the support vertices
that represent the horizontal components of the reaction forces at the supports.

There are two options.
We can add one horizontal component per support or two.
If only component is added, the direction of the horizontal reaction force at that support is fully constrained.
If two components are added, the horizontal component of the reaction force at that support can be any combination of those two force vectors.


.. figure:: /_images/TNA_boundaries.png
    :figclass: figure
    :class: figure-img img-fluid


Make the force diagram
======================

**Commands**

* ``TNA_force``


Once the boundary conditions are set, we can make the force diagram.
The force diagram is intialised as the dual of the form diagram.
This means that the vertices of the force diagram are at the centroids of the
corresponding faces of the form diagram.


.. figure:: /_images/TNA_force.png
    :figclass: figure
    :class: figure-img img-fluid


**Commands**

* ``TNA_move > force > diagram``


After constructing the force diagram, move it out of the way.
Use the command ``TNA_move`` with the options ``force`` and ``diagram``.


.. figure:: /_images/TNA_move.png
    :figclass: figure
    :class: figure-img img-fluid


Initial equilibrium shape
=========================

**Commands**

* ``TNA_horizontal``


At this point, we can generate a first, unconstrained version of the equilibrium shape of the funicular force network.
First, run horizontal equilibrium using ``TNA_horizontal``.


.. figure:: /_images/TNA_horizontal.png
    :figclass: figure
    :class: figure-img img-fluid


**Commands**

* ``TNA_settings``


Note that the default settings of the horizontal equilibrium solver will allow for only 100 iterations at a time.
This will not immediately result in the fully resolved horizontal equilibrium depicted above.
Either increase the maximum number of iterations, or run ``TNA_horizontal`` multiple times, or both.
Use the commmand ``TNA_settings`` to change ``horizontal.kmax``.

.. note::

    We use Remote Procedure Calls to solve horizontal and vertical equilibrium
    outside of Rhino such that we can use Numpy and Scipy.
    The current implementation of ``compas.rpc`` limits the amount of time a remote
    procedure can run before the connection is interrupted.
    Therefore, don't increase the number of iterations by too much.
    For example, don't go over 500.
    If you need more iterations, just run the command multiple times.


**Commands**

* ``TNA_vertical``


Once horizontal equilibrium has been established, run ``TNA_vertical``.
This command will ask for ``Z Max``, which is a value for the highest vertex
of the equilibrium network that will be used to determine an appropriate scale


.. figure:: /_images/TNA_vertical.png
    :figclass: figure
    :class: figure-img img-fluid


Set the constraints
===================

1. Edges spanning the ribs
--------------------------

**Commands**

* ``TNA_select > form > edges > continuous``
* ``TNA_attributes > form > edges``


First, we select the edges in the directions spanning the ribs.
Run command ``TNA_select``, choose option ``form`` and then ``edges`` and finally
selection mode ``continuous``.
Then, select one edge per spanning direction (see image below).
Selection mode ``continuous`` will make sure all other adges are found as well.
Finally, use command ``TNA_attributes`` (choose ``form`` and then ``edges``)
to set ``fmin := 2`` and ``fmax := 2`` of the selected edges.


.. figure:: /_images/TNA_constraints-spanning.png
    :figclass: figure
    :class: figure-img img-fluid


2. Edges on boundary
--------------------

**Commands**

* ``TNA_select > form > edges > continuous``
* ``TNA_attributes > form > edges``


The vertices on the boundary carry less load than the internal ones.
Therefore, use the same procedure as in the previous step to select the edges on the boundary and set
``fmin := 1`` and ``fmax := 1``.


.. figure:: /_images/TNA_constraints-boundary.png
    :figclass: figure
    :class: figure-img img-fluid


3. Edges perpendicular to boundary
----------------------------------

**Commands**

* ``TNA_select > form > edges > parallel``
* ``TNA_attributes > form > edges``


The edges perpendicular to the vault boundaries are not supposed to carry any loads.
Therefore, we set ``fmin := 0.0`` and ``fmax := 0.0`` such that the corresponding
edges in the force diagram collapse.
Use the selection mode ``parallel`` and select the edges shown in the image below to
select all the edges perpendicular to the boundary.


.. figure:: /_images/TNA_constraints-other.png
    :figclass: figure
    :class: figure-img img-fluid


4. Edges central cross
----------------------

**Commands**

* ``TNA_attributes > form > edges``


Finally, make sure the edges in the force diagram corresponding to the central cross (see image below) don't collapse.
Set ``fmin := 1.0``.

.. figure:: /_images/TNA_constraints-cross.png
    :figclass: figure
    :class: figure-img img-fluid


Constrained equilibrium
=======================

**Commands**

* ``TNA_horizontal``


After setting all constraints, we can update horizontal equilibrium.
As before, you will have to run ``TNA_horizontal`` multiple times before horizontal
equilibrium si fully resolved.


.. figure:: /_images/TNA_horizontal-constrained.png
    :figclass: figure
    :class: figure-img img-fluid


**Commands**

* ``TNA_vertical``


Using ``zmax := 4.0``, compute the final equilibrium shape of the constrained funicular problem.


.. figure:: /_images/TNA_vertical-constrained.png
    :figclass: figure
    :class: figure-img img-fluid


Visualise the result
====================

**Commands**

* ``TNA_settings``


Use the settings dialog to turn on the visualisation of the internal forces and the reaction forces in the solution.
Run command ``TNA_settings`` and set

* ``show.forces := True``
* ``show.reactions := True``
* ``scale.forces := 0.01``
* ``scale.reactions := 0.1``


.. figure:: /_images/TNA_result.png
    :figclass: figure
    :class: figure-img img-fluid
