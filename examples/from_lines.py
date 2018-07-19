from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import sqrt

import compas
import compas_tna

from compas.files import OBJ

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.equilibrium import horizontal_nodal
from compas_tna.equilibrium import vertical_from_zmax
from compas_tna.equilibrium import vertical_from_target
from compas_tna.equilibrium import vertical_from_self
from compas_tna.equilibrium import vertical_from_formforce

from compas_tna.viewers import FormViewer


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


# ==============================================================================
# make a form diagram from a set of lines

filepath = compas.get('lines.obj')

obj      = OBJ(filepath)
vertices = obj.parser.vertices
edges    = obj.parser.lines
lines    = [(vertices[u], vertices[v], 0) for u, v in edges]

form = FormDiagram.from_lines(lines)

# ==============================================================================
# update boundary conditions

boundaries = form.vertices_on_boundaries()

exterior = boundaries[0]
interior = boundaries[1:]

form.set_vertices_attribute('is_anchor', True, keys=exterior)

form.update_exterior(exterior, feet=1)
form.update_interior(interior)

# ==============================================================================
# create the force diagram

force = ForceDiagram.from_formdiagram(form)

# ==============================================================================
# compute equilibrium

horizontal_nodal(form, force)
vertical_from_zmax(form, force, zmax=4)
vertical_from_formforce(form, force)

print('scale:', force.attributes['scale'])
print('zmax:', max(form.get_vertices_attribute('z')))
print('residual:', form.residual())

# ==============================================================================
# visualise the result

viewer = FormViewer(form, figsize=(14, 9))

viewer.draw_vertices(
    keys=list(form.vertices_where({'is_external': False})),
    text={key: "{:.1f}".format(attr['z']) for key, attr in form.vertices(True)})
viewer.draw_edges(
    keys=list(form.edges_where({'is_edge': True, 'is_external': False})),
    width=0.1)
viewer.draw_reactions(scale=0.1)
viewer.draw_forces(scale=1.0)
viewer.draw_faces(keys=form.faces_where({'is_loaded': True}))

viewer.show()
