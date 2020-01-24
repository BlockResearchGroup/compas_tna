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
    # try:
    formdata, forcedata = tna.horizontal_nodal_proxy(form.to_data(), force.to_data(), alpha=alpha, kmax=kmax)
    # except BrokenPipeError:
    #     return
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
    # try:
    formdata, scale = tna.vertical_from_zmax_proxy(form.to_data(), zmax)
    # except BrokenPipeError:
    #     return None
    form.data = formdata
    return scale


# make the form diagram from selected line elements

guids = compas_rhino.select_lines()

form = FormDiagram.from_rhinolines(guids)
form.draw(layer='TNA::FormDiagram', clear_layer=True)

# identify the supports

keys = DiagramHelper.select_vertices(form)

if keys:
    form.vertices_attributes(['is_anchor', 'is_fixed'], [True, True], keys=keys)
    form.draw(layer='TNA::FormDiagram', clear_layer=True)

# update the boundaries
# Note: two feet per support to allow for non-symmetrical force distributions
#       in the different webs of the cross-vault

form.update_boundaries(feet=2)
form.draw(layer='TNA::FormDiagram', clear_layer=True)

# make the force diagram

force = ForceDiagram.from_formdiagram(form)
force.draw(layer='TNA::ForceDiagram', clear_layer=True)

# move the force diagram

if DiagramHelper.move(force):
    force.draw(layer='TNA::ForceDiagram', clear_layer=True)

# fix one of the vertices of the force diagram
# to keep it in place

key = DiagramHelper.select_vertex(force)
if key is not None:
    force.vertex_attribute(key, 'is_fixed', True)
    force.draw(layer='TNA::ForceDiagram', clear_layer=True)

# set the constraints for the edges in the spanning direction
# => fmin := 2, fmax := 2

guids = compas_rhino.get_curves(layer='spanning')
if guids:
    keys = DiagramHelper.identify_edges_on_curves(form, guids)
    if keys:
        DiagramHelper.highlight_edges(form, keys)
        if DiagramHelper.update_edge_attributes(form, keys, names=['fmin', 'fmax']):
            form.draw(layer='TNA::FormDiagram', clear_layer=True)

# set the constraints for the edges on the boundary
# => fmin := 1, fmax := 1

guids = compas_rhino.get_curves(layer='boundary')
if guids:
    keys = DiagramHelper.identify_edges_on_curves(form, guids)
    if keys:
        DiagramHelper.highlight_edges(form, keys)
        if DiagramHelper.update_edge_attributes(form, keys, names=['fmin', 'fmax']):
            form.draw(layer='TNA::FormDiagram', clear_layer=True)

# set the constraints for the edges in the central cross
# => fmin := 1

guids = compas_rhino.get_curves(layer='cross')
if guids:
    keys = DiagramHelper.identify_edges_on_curves(form, guids)
    if keys:
        DiagramHelper.highlight_edges(form, keys)
        if DiagramHelper.update_edge_attributes(form, keys, names=['fmin', 'fmax']):
            form.draw(layer='TNA::FormDiagram', clear_layer=True)

# set the constraints for the other edges
# => fmin := 0, fmax := 0

guids = compas_rhino.get_curves(layer='other')
if guids:
    keys = DiagramHelper.identify_edges_on_curves(form, guids)
    if keys:
        DiagramHelper.highlight_edges(form, keys)
        if DiagramHelper.update_edge_attributes(form, keys, names=['fmin', 'fmax']):
            form.draw(layer='TNA::FormDiagram', clear_layer=True)

# compute horizontal equilibrium
# Note: this is split up into two parts to avoid BrokenPipeError

horizontal(form, force, alpha=100, kmax=500)
horizontal(form, force, alpha=100, kmax=500)

force.draw(layer='TNA::ForceDiagram', clear_layer=True)

horizontal(form, force, alpha=100, kmax=500)
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
    'scale.forces'   : 0.01,
    'scale.reactions': 0.1
}

form.draw(layer='TNA::FormDiagram', clear_layer=True, settings=settings)
