from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from math import cos
from math import sin
from math import sqrt

import compas
import compas_tna

from compas.files import OBJ
from compas.utilities import pairwise
from compas.utilities import flatten
from compas.utilities import i_to_red

from compas.geometry import subtract_vectors_xy
from compas.geometry import add_vectors_xy
from compas.geometry import normalize_vector_xy
from compas.geometry import centroid_points_xy
from compas.geometry import rotate_points_xy
from compas.geometry import rotate_points
from compas.geometry import is_ccw_xy
from compas.geometry import angle_vectors_xy
from compas.geometry import mesh_cull_duplicate_vertices
from compas.geometry import length_vector_xy
from compas.geometry import cross_vectors

from compas.geometry import convex_hull_xy

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.equilibrium import horizontal_nodal
from compas_tna.equilibrium import vertical_from_zmax

from compas_tna.viewers import Viewer2


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


file = compas_tna.get('clean.obj')
# file = compas.get('faces.obj')

form = FormDiagram.from_obj(file)

# this should still work after updating
# keys = form.edges_on_boundary()
# print(keys)
# form.set_edges_attribute('q', 10.0, keys=keys)

# ==============================================================================

form.collapse_small_edges(tol=0.5)

boundaries = form.vertices_on_boundary()

exterior = boundaries[0]
interior = boundaries[1:]

# for key in form.corners():
#     form.set_vertex_attribute(key, 'is_anchor', True)

for key in exterior:
    form.set_vertex_attribute(key, 'is_anchor', True)

form.update_exterior(exterior, feet=1)
form.update_interior(interior)

fixed = set(list(flatten(boundaries)) + form.fixed())
# fixed = set(form.anchors() + form.fixed())

form.relax(fixed=fixed)

# ==============================================================================

force = ForceDiagram.from_formdiagram(form)

# ==============================================================================

horizontal_nodal(form, force)
vertical_from_zmax(form, force)

# ==============================================================================

viewer = Viewer2(form, force)
viewer.default['edgewidth'] = 0.1
viewer.setup()

vertexcolor = {}

z = form.get_vertices_attribute('z')
zmin, zmax = min(z), max(z)
vertexcolor.update({key: i_to_red((attr['z'] - zmin) / (zmax - zmin)) for key, attr in form.vertices(True)})

vertexcolor.update({key: '#00ff00' for key in form.vertices_where({'is_fixed': True})})
vertexcolor.update({key: '#000000' for key in form.vertices_where({'is_anchor': True})})

viewer.draw_form(
    vertexsize=0.1,
    vertexcolor=vertexcolor,
)
viewer.draw_force(vertices_on=False, vertexsize=0.02)

viewer.show()
