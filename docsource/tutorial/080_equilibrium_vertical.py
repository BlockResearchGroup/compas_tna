"""
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

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.equilibrium import horizontal
from compas_tna.equilibrium import vertical_from_zmax

from compas.plotters import MeshPlotter
from compas.utilities import i_to_black


form = FormDiagram.from_json('data/boundaryconditions.json')
force = ForceDiagram.from_formdiagram(form)

horizontal(form, force, alpha=100)
scale = vertical_from_zmax(form, 3.0)

print(scale)


# ==============================================================================
# visualise
# ==============================================================================

z = form.get_vertices_attribute('z')
zmin = min(z)
zmax = max(z)
zrng = zmax - zmin

plotter = MeshPlotter(form, figsize=(12, 8), tight=True)

plotter.draw_vertices(
    keys=list(form.vertices_where({'is_external': False})),
    facecolor={key: i_to_black((attr['z'] - zmin) / zrng) for key, attr in form.vertices_where({'is_external': False}, True)},
    radius=0.1
)

plotter.draw_edges(
    keys=list(form.edges_where({'is_edge': True})),
    color={key: '#00ff00' for key in form.edges_where({'is_external': True})},
    width={key: 2.0 for key in form.edges_where({'is_external': True})}
)

plotter.draw_faces(
    keys=list(form.faces_where({'is_loaded': True}))
)

plotter.show()
