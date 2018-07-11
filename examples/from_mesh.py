from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from math import cos
from math import sin
from math import sqrt

import compas
import compas_tna

from compas.utilities import flatten
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

# make a form diagram from an obj file

file = compas_tna.get('clean.obj')
form = FormDiagram.from_obj(file)

# collapse edges that are shorter than 0.5

form.collapse_small_edges(tol=0.5)

# extract the exterior and interior boundaries

boundaries = form.vertices_on_boundary()

exterior = boundaries[0]
interior = boundaries[1:]

# anchor the vertices of the exterior boundary

for key in exterior:
    form.set_vertex_attribute(key, 'is_anchor', True)

# update the boundary conditions

form.update_exterior(exterior, feet=1)
form.update_interior(interior)

# relax the interior

fixed = set(list(flatten(boundaries)) + form.fixed())

form.relax(fixed=fixed)

# create the force diagram

force = ForceDiagram.from_formdiagram(form)

# compute equilibrium

horizontal_nodal(form, force)
vertical_from_zmax(form, force)

# visualise result

viewer = Viewer2(form, force)
viewer.default['edgewidth'] = 0.1
viewer.setup()

vertexcolor = {}

z = form.get_vertices_attribute('z')
zmin, zmax = min(z), max(z)
zrange = zmax - zmin

vertexcolor.update({key: i_to_red((attr['z'] - zmin) / (zrange)) for key, attr in form.vertices(True)})
vertexcolor.update({key: '#00ff00' for key in form.vertices_where({'is_fixed': True})})
vertexcolor.update({key: '#000000' for key in form.vertices_where({'is_anchor': True})})

viewer.draw_form(
    vertexsize=0.01,
    vertexcolor=vertexcolor,
)
viewer.draw_force(vertices_on=False, vertexsize=0.02)

viewer.show()
