import compas
import compas_rhino
import compas_tna

from compas.rpc import Proxy

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram
from compas_tna.rhino import DiagramHelper

import rhinoscriptsyntax as rs


tna = Proxy('compas_tna.equilibrium')


def horizontal(form, force, alpha=100, kmax=500):
    """Compute horizontal equilibrium by parallelising the form and force diagram.

    Parameters
    ----------
    form : compas_tna.diagrams.FormDiagram
        The form diagram.
    force : compas_tna.diagrams.ForceDiagram
        The force diagram.
    alpha : int (100)
        Weighting factor for the calculation of the target vectors.
        ``alpha = 100`` means target vectors parallel to the edges of the form diagram.
        ``alpha = 0`` means target vectors parallel to the edges of the force diagram.
    kmax : int (500)
        Maximum number of iterations.

    Notes
    -----
    This is a wrapper around the proxy for the function ``compas_tna.equilibrium.horizontal_nodal``.

    """
    formdata, forcedata = tna.horizontal_nodal_proxy(form.to_data(), force.to_data(), alpha=alpha, kmax=kmax)
    form.data = formdata
    force.data = forcedata


def vertical(form, zmax):
    """Compute the scale of the force diagram such that the maximum z-coordinate
    of all vertices corresponds to a chosen value.

    Parameters
    ----------
    form : compas_tna.diagrams.FormDiagram
        The form diagram.
    zmax : float
        The maximum z-coordinate of all vertices of the equilibrium network.

    """
    formdata, scale = tna.vertical_from_zmax_proxy(form.to_data(), zmax)
    form.data = formdata
    return scale


# make the form diagram from selected line elements

guids = compas_rhino.select_lines()

form = FormDiagram.from_rhinolines(guids)
form.draw(layer='TNA::FormDiagram', clear_layer=True)

# identify the supports

guids = compas_rhino.select_curves()
keys = DiagramHelper.identify_vertices_on_curves(form, guids)

if keys:
    form.set_vertices_attributes(['is_anchor', 'is_fixed'], [True, True], keys=keys)
    form.draw(layer='TNA::FormDiagram', clear_layer=True)

# update the boundaries
# Note: add only one foot per support to control the direction of the horizontal component
#       of the reaction force

form.update_boundaries(feet=1)
form.draw(layer='TNA::FormDiagram', clear_layer=True)

# move the "feet" such that the horizontal reaction forces are constrained in the correct direction

while True:
    key = DiagramHelper.select_vertex(form)
    if key is None:
        break

    if DiagramHelper.move_vertex(form, key):
        form.draw(layer='TNA::FormDiagram', clear_layer=True)

# set the constraints
# Note: you should apply 3 sets of constraints
#       1. the edges in the spanning direction                 => fmin := 2, fmax := 2
#       2. the edges in the spanning direction on the boundary => fmin := 1, fmin := 1
#       3. the edges in the opposite direction                 => fmin := 0, fmax := 0

while True:
    edges = DiagramHelper.select_edges(form)
    if not edges:
        break

    if DiagramHelper.update_edge_attributes(form, edges):
        form.draw(layer='TNA::FormDiagram', clear_layer=True)

# make the force diagram

force = ForceDiagram.from_formdiagram(form)
force.draw(layer='TNA::ForceDiagram', clear_layer=True)

# compute horizontal equilibrium

horizontal(form, force, alpha=100, kmax=500)
force.draw(layer='TNA::ForceDiagram', clear_layer=True)

# compute vertical equilibrium based on a chosen height of the highest point of the equilibrium network

zmax = rs.GetReal('Z Max')

scale = vertical(form, zmax)
force.attributes['scale'] = scale

# visualise the result

settings = {
    'show.forces'    : True,
    'show.reactions' : True,
    'scale.forces'   : 0.02,
    'scale.reactions': 1.0
}

form.draw(layer='TNA::FormDiagram', clear_layer=True, settings=settings)
