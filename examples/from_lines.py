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
points   = obj.parser.points
lines    = [(vertices[u], vertices[v], 0) for u, v in edges]

print(points)

form = FormDiagram.from_lines(lines)

form.attributes['foot.scale'] = 1.0

# ==============================================================================

boundaries = form.vertices_on_boundary()

exterior = boundaries[0]
interior = boundaries[1:]

form.set_vertices_attribute('is_anchor', True, keys=exterior)

form.update_exterior(exterior, feet=2)
form.update_interior(interior)

# ==============================================================================

force = ForceDiagram.from_formdiagram(form)

horizontal_nodal(form, force)
vertical_from_zmax(form, force)

viewer = Viewer2(form, force)

viewer.setup()

vertexcolor = {}
vertexcolor.update({key: '#00ff00' for key in form.fixed()})
vertexcolor.update({key: '#ff0000' for key in form.anchors()})

viewer.draw_form(
    vertexcolor=vertexcolor,
    vertexlabel={key: key for key in form.vertices()},
    vertexsize=0.2
)
viewer.draw_force()

viewer.show()
