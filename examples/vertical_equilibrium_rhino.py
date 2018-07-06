from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino
import compas_tna

from compas.utilities import XFunc
from compas.utilities import pairwise

from compas_tna.rhino import RhinoFormDiagram
from compas_tna.rhino import RhinoForceDiagram

fd_numpy = XFunc('compas.numerical.fd_numpy')
horizontal_nodal = XFunc('compas_tna.equilibrium.horizontal_nodal')
vertical_from_formforce = XFunc('compas_tna.equilibrium.vertical_from_formforce')
vertical_from_zmax = XFunc('compas_tna.equilibrium.vertical_from_zmax')


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


form = RhinoFormDiagram.from_obj(compas.get('faces.obj'))

for key in form.vertices_where({'vertex_degree': 2}):
    form.vertex[key]['is_anchor'] = True

boundary = form.vertices_on_boundary(ordered=True)

unsupported = [[]]
for key in boundary:
    unsupported[-1].append(key)
    if form.vertex[key]['is_anchor']:
        unsupported.append([key])

unsupported[-1] += unsupported[0]
del unsupported[0]

for vertices in unsupported:
    for u, v in pairwise(vertices):
        form.set_edge_attribute((u, v), 'q', 10)

for vertices in unsupported:
    fkey = form.add_face(vertices, is_unloaded=True)

for vertices in unsupported:
    u = vertices[-1]
    v = vertices[0]
    form.set_edge_attribute((u, v), 'is_edge', False)

vertices = form.get_vertices_attributes('xyz')
edges = list(form.edges_where({'is_edge': True}))
fixed = list(form.vertices_where({'is_anchor': True}))
qs = [form.get_edge_attribute(uv, 'q') for uv in edges]
loads = form.get_vertices_attributes(('px', 'py', 'pz'), (0, 0, 0))

xyz, q, f, l, r = fd_numpy(vertices, edges, fixed, qs, loads)

for key, attr in form.vertices(True):
    attr['x'] = xyz[key][0]
    attr['y'] = xyz[key][1]
    attr['z'] = xyz[key][2]

force = RhinoForceDiagram.from_formdiagram(form)

formdata, forcedata = horizontal_nodal(form.to_data(), force.to_data())
# formdata, forcedata = vertical_from_formforce(formdata, forcedata, density=0.05)
formdata, forcedata = vertical_from_zmax(formdata, forcedata, density=0.05)

form.data = formdata
force.data = forcedata

form.draw()
form.show_reactions()

force.draw()