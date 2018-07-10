from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_tna

from compas.numerical import fd_numpy
from compas.utilities import pairwise
from compas.utilities import i_to_red

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.equilibrium import horizontal_nodal
from compas_tna.equilibrium import vertical_from_zmax

from compas_tna.viewers import Viewer2


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


# ==============================================================================
# init form
# ==============================================================================

form = FormDiagram.from_obj(compas.get('faces.obj'))

# ==============================================================================
# identify anchors
# ==============================================================================

for key in form.vertices_where({'vertex_degree': 2}):
    form.vertex[key]['is_anchor'] = True

# ==============================================================================
# split boundary into unsuppported openings
# ==============================================================================

boundary = form.vertices_on_boundary(ordered=True)

unsupported = [[]]
for key in boundary:
    unsupported[-1].append(key)
    if form.vertex[key]['is_anchor']:
        unsupported.append([key])

unsupported[-1] += unsupported[0]
del unsupported[0]

# ==============================================================================
# set force densities of openings
# to control curvature (sag)
# ==============================================================================

for vertices in unsupported:
    for u, v in pairwise(vertices):
        form.set_edge_attribute((u, v), 'q', 10)

# ==============================================================================
# mark openings as unloaded
# ==============================================================================

for vertices in unsupported:
    fkey = form.add_face(vertices, is_loaded=False)

# ==============================================================================
# mark outside edges of openings as not relevant
# ==============================================================================

for vertices in unsupported:
    u = vertices[-1]
    v = vertices[0]
    form.set_edge_attribute((u, v), 'is_edge', False)

# ==============================================================================
# use force density method
# to compute feasible open edges geometry
# ==============================================================================

relax_formdiagram(form)

# ==============================================================================

force = ForceDiagram.from_formdiagram(form)

# ==============================================================================

horizontal_nodal(form, force)
vertical_from_zmax(form, force)

# ==============================================================================
# visualise
# ==============================================================================

viewer = Viewer2(form, force)

viewer.setup()

z = form.get_vertices_attribute('z')
zmin, zmax = min(z), max(z)

vertexcolor = {key: i_to_red((attr['z'] - zmin) / (zmax - zmin)) for key, attr in form.vertices(True)}

# for key in form.vertices_where({'is_anchor': True}):
#     vertexcolor[key] = '#000000'

viewer.draw_form(
    # vertexlabel={key: key for key, attr in form.vertices(True)},
    vertexsize=0.1,
    vertexcolor=vertexcolor
)
viewer.draw_force()

viewer.show()

