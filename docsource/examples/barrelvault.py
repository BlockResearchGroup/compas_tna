"""Generate a barrel vault starting from a grid of lines.

Note: use with data/barrelvault.3dm

"""
import compas
import compas_rhino
import compas_tna

from compas.rpc import Proxy

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.rhino import DiagramHelper

import rhinoscriptsyntax as rs


tna = Proxy('compas_tna.equilibrium')


def horizontal(form, force, *args, **kwargs):
    formdata, forcedata = tna.horizontal_nodal_proxy(form.to_data(), force.to_data(), *args, **kwargs)
    form.data = formdata
    force.data = forcedata


def vertical(form, zmax):
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
# Note:

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
#       1. the edges in the spanning direction => fmin := 2, fmax := 2
#       2. the edges in the spanning direction on the boundary => fmin := 1, fmin := 1
#       3. the edges in the opposite direction => fmin := 0, fmax := 0

while True:
    edges = DiagramHelper.select_edges(form)
    if not edges:
        break

    if DiagramHelper.update_edge_attributes(form, edges):
        form.draw(layer='TNA::FormDiagram', clear_layer=True)

# make the force diagram

force = ForceDiagram.from_formdiagram(form)
force.draw(layer='TNA::ForceDiagram', clear_layer=True)

# move the force diagram

if DiagramHelper.move(force):
    force.draw(layer='TNA::ForceDiagram', clear_layer=True)

# fix the position of the force diagram

key = DiagramHelper.select_vertex(force)
if key is not None:
    if Diagramelper.update_vertex_attributes(force, [key]):
        force.draw(layer='TNA::ForceDiagram', clear_layer=True)

# compute horizontal equilibrium

horizontal(form, force, alpha=100, kmax=500)
force.draw(layer='TNA::ForceDiagram', clear_layer=True)

# compute vertical equilibrium based on a chosen height of the highest point of the equilibrium network

zmax = rs.GetReal('Z Max')

scale = vertical(form, zmax)
force.attributes['scale'] = scale

settings = {
    'show.forces'    : True,
    'show.reactions' : True,
    'scale.forces'   : 0.02,
    'scale.reactions': 1.0
}

form.draw(layer='TNA::FormDiagram', clear_layer=True, settings=settings)
