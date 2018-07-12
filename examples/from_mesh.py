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

from compas_tna.equilibrium import horizontal
from compas_tna.equilibrium import vertical_from_zmax
from compas_tna.equilibrium import vertical_from_average
from compas_tna.equilibrium import vertical_from_formforce

from compas_tna.viewers import FormViewer
from compas_tna.viewers import Viewer2


# todo: update attributes from kwargs


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


# make a form diagram from an obj file

form = FormDiagram.from_obj(compas.get('faces.obj'))

form.attributes['foot.scale'] = 0.5

# collapse edges that are shorter than 0.5

form.collapse_small_edges(tol=0.5)

# extract the exterior and interior boundaries

boundaries = form.vertices_on_boundaries()

exterior = boundaries[0]
interior = boundaries[1:]

# anchor the vertices of the exterior boundary

form.set_vertices_attribute('is_anchor', True, keys=exterior)

# update the boundary conditions

form.update_exterior(exterior, feet=1)
form.update_interior(interior)

# relax the interior

fixed = set(list(flatten(boundaries)) + form.fixed())

form.relax(fixed=fixed)

# create the force diagram

force = ForceDiagram.from_formdiagram(form)

# compute equilibrium

horizontal(form, force)
vertical_from_zmax(form, force, zmax=5, kmax=100)
vertical_from_formforce(form, force, kmax=300, tol=1e-1)

# visualise result

viewer = FormViewer(form, figsize=(16, 9))
viewer.defaults['edge.fontsize'] = 4

edgelabels = {(u, v): "{:.1f}".format(attr['a']) for u, v, attr in form.edges_where({'is_edge': True}, True) if attr['a'] > 0.1} 

viewer.draw_vertices(
    keys=list(form.vertices_where({'is_external': False})),
    text={key: "{:.1f}".format(attr['z']) for key, attr in form.vertices(True)}
)
viewer.draw_edges(
    keys=list(form.edges_where({'is_edge': True, 'is_external': False})),
    width=0.1,
    text=edgelabels
)
viewer.draw_reactions(scale=1.0)
viewer.draw_horizontalforces(scale=1.0)

viewer.show()
