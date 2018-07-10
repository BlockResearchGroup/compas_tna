from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from math import cos
from math import sin

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


def rotate(point, angle):
    x = cos(angle) * point[0] - sin(angle) * point[1]
    y = sin(angle) * point[0] + cos(angle) * point[1]
    return x, y, 0


filepath = compas_tna.get('clean.obj')

obj      = OBJ(filepath)
vertices = obj.parser.vertices
faces    = obj.parser.faces

form = FormDiagram.from_vertices_and_faces(vertices, faces)

# ==============================================================================

form.collapse_small_edges(tol=0.5)

# ==============================================================================

boundaries = form.vertices_on_boundary()

# ==============================================================================

form.relax(fixed=set(list(flatten(boundaries))))

# ==============================================================================

boundary = boundaries[0]

for key in boundary:
    form.set_vertex_attribute(key, 'is_anchor', True)

for vertices in boundaries[1:]:
    form.add_face(vertices, is_loaded=False)

unsupported = [[]]
for key in boundary:
    unsupported[-1].append(key)
    if form.vertex[key]['is_anchor']:
        unsupported.append([key])

unsupported[-1] += unsupported[0]
del unsupported[0]

# ==============================================================================

scale = 0.1

key_foot = {}

for i in range(len(unsupported)):
    vertices = unsupported[i]

    key = vertices[0]

    a = vertices[1]
    b = unsupported[i - 1][-2]

    o = form.vertex_coordinates(key)

    nbrs = form.vertex_neighbours(key)

    if len(nbrs) == 2:
        c = centroid_points_xy([form.face_centroid(fkey) for fkey in form.vertex_faces(key)])
        oc = subtract_vectors_xy(c, o)
        r = normalize_vector_xy(oc)
        r = [-scale * axis for axis in r]

    else:
        xyz = [form.vertex_coordinates(nbr) for nbr in nbrs if nbr not in (a, b)]
        c = centroid_points_xy(xyz)
        oc = subtract_vectors_xy(c, o)
        r = normalize_vector_xy(oc)
        r = [-scale * axis for axis in r]

    b = add_vectors_xy(o, rotate(r, +45 * pi / 180))
    a = add_vectors_xy(o, rotate(r, -45 * pi / 180))

    b = form.add_vertex(x=b[0], y=b[1], z=0, is_fixed=True)
    a = form.add_vertex(x=a[0], y=a[1], z=0, is_fixed=True)

    key_foot[key] = (b, a)


for vertices in unsupported:

    l = vertices[0]
    r = vertices[-1]

    lb = key_foot[l][0]
    la = key_foot[l][1]

    rb = key_foot[r][0]

    form.add_face([lb, l, la])
    form.add_face([la] + vertices + [rb])

    if (la, lb) not in form.edgedata:
        form.edgedata[la, lb] = {}

    form.edgedata[la, lb]['is_edge'] = False

    if (lb, la) not in form.edgedata:
        form.edgedata[lb, la] = {}

    form.edgedata[lb, la]['is_edge'] = False

    if (rb, la) not in form.edgedata:
        form.edgedata[rb, la] = {}

    form.edgedata[rb, la]['is_edge'] = False

    if (la, rb) not in form.edgedata:
        form.edgedata[la, rb] = {}

    form.edgedata[la, rb]['is_edge'] = False

# ==============================================================================

force = ForceDiagram.from_formdiagram(form)

horizontal_nodal(form, force)
vertical_from_zmax(form, force)

viewer = Viewer2(form, force)

viewer.setup()

z = form.get_vertices_attribute('z')
zmin, zmax = min(z), max(z)

vertexcolor = {}
# vertexcolor.update({key: i_to_red((attr['z'] - zmin) / (zmax - zmin)) for key, attr in form.vertices(True)})
# vertexcolor.update({key: '#ffffff' for key in form.vertices_where({'is_fixed': True})})
# vertexcolor.update({key: '#000000' for key in form.vertices_where({'is_anchor': True})})

viewer.draw_form(
    # vertexlabel={key: key for key, attr in form.vertices(True)},
    vertexsize=0.05,
    vertexcolor=vertexcolor
)
viewer.draw_force(vertexsize=0.02)

viewer.show()
