from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_tna

from compas.files import OBJ
from compas.utilities import pairwise

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.equilibrium import horizontal_nodal
from compas_tna.equilibrium import vertical_from_zmax

from compas_tna.viewers import Viewer2


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


filepath = compas.get('lines.obj')

obj      = OBJ(filepath)
vertices = obj.parser.vertices
edges    = obj.parser.lines
lines    = [(vertices[u], vertices[v], 0) for u, v in edges]

form = FormDiagram.from_lines(lines)

# ==============================================================================

boundary = form.vertices_on_boundary(ordered=True)

for u, v in pairwise(boundary + boundary[0:1]):

    form.set_vertex_attribute(u, 'is_anchor', True)

    if (u, v) not in form.edgedata:
        form.edgedata[u, v] = {}
    form.edgedata[(u, v)]['is_edge'] = False

    if (v, u) not in form.edgedata:
        form.edgedata[v, u] = {}
    form.edgedata[(v, u)]['is_edge'] = False

# ==============================================================================

force = ForceDiagram.from_formdiagram(form)

horizontal_nodal(form, force)
vertical_from_zmax(form, force)

viewer = Viewer2(form, force)

viewer.setup()

viewer.draw_form(vertexlabel={key: "{:.1f}".format(attr['z']) for key, attr in form.vertices(True)}, vertexsize=0.2)
viewer.draw_force()

viewer.show()
