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
horizontal_nodal_xfunc = XFunc('compas_tna.equilibrium.horizontal_nodal_xfunc')


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


def relax_formdiagram(form):
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


def horizontal_nodal(form, force):
    formdata, forcedata = horizontal_nodal_xfunc(form.to_data(), force.to_data())
    form.data = formdata
    force.data = forcedata


# ==============================================================================
# Main
# ==============================================================================

form = RhinoFormDiagram.from_obj(compas.get('faces.obj'))

# ==============================================================================
# use force density method
# to compute feasible open edges geometry
# ==============================================================================

for key in form.vertices_where({'vertex_degree': 2}):
    form.vertex[key]['is_anchor'] = True

boundary = form.vertices_on_boundary(ordered=True)

# search for first anchor and start boundary cycle from there

unsupported = [[]]
for key in boundary:
    unsupported[-1].append(key)
    if form.vertex[key]['is_anchor']:
        unsupported.append([key])

unsupported[-1] += unsupported[0]
del unsupported[0]

# define the ratio between the internal force density
# and the one on the boundary to control the sag (look up in membranes book)

for vertices in unsupported:
    for u, v in pairwise(vertices):
        form.set_edge_attribute((u, v), 'q', 10)

# combine?

for vertices in unsupported:
    fkey = form.add_face(vertices, is_loaded=False)

for vertices in unsupported:
    u = vertices[-1]
    v = vertices[0]
    form.set_edge_attribute((u, v), 'is_edge', False)

# ==============================================================================

# use version based on alglib
# load from compas.numerical
# catch rhino in try except
# load alternative modules

relax_formdiagram(form)

# ==============================================================================

force = RhinoForceDiagram.from_formdiagram(form)

horizontal_nodal(form, force)

form.draw()
force.draw()
